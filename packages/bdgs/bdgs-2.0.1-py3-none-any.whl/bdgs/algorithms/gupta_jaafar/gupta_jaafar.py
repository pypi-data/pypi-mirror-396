import os
import pickle
from enum import Enum

import cv2
import numpy as np
from skimage.filters import gabor
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis as LDA
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

from bdgs.algorithms.bdgs_algorithm import BaseAlgorithm
from bdgs.algorithms.gupta_jaafar.gupta_jaafar_learning_data import GuptaJaafarLearningData
from bdgs.algorithms.gupta_jaafar.gupta_jaafar_payload import GuptaJaafarPayload
from bdgs.common.crop_image import crop_image
from bdgs.common.set_options import set_options
from bdgs.data.gesture import GESTURE
from bdgs.data.processing_method import PROCESSING_METHOD
from definitions import ROOT_DIR


class GuptaJaafar(BaseAlgorithm):
    GABOR_SCALES = [1, 2, 3]
    GABOR_ORIENTATIONS = [0, np.deg2rad(36), np.deg2rad(72), np.deg2rad(108), np.deg2rad(144)]

    def __init__(self):
        self.feature_vector = None

    def process_image(self, payload: GuptaJaafarPayload,
                      processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT) -> np.ndarray:

        # Experimental
        if processing_method != PROCESSING_METHOD.DEFAULT:
            from bdgs.data.algorithm_functions import ALGORITHM_FUNCTIONS
            return ALGORITHM_FUNCTIONS[processing_method].process_image(payload)

        cropped_image = crop_image(payload.image, payload.coords)
        gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (16, 16))
        features = []
        preview_accumulator = np.zeros_like(resized, dtype=np.float32)
        for sigma in self.GABOR_SCALES:
            for theta in self.GABOR_ORIENTATIONS:
                real, _ = gabor(resized, frequency=0.5, theta=theta, sigma_x=sigma, sigma_y=sigma)
                preview_accumulator += real.astype(np.float32)
                features.append(real.flatten())

        self.feature_vector = np.concatenate(features)
        preview_image = preview_accumulator / len(features)
        preview_image = cv2.normalize(preview_image, None, 0, 255, cv2.NORM_MINMAX)
        preview_image = preview_image.astype(np.uint8)
        return preview_image

    def classify(self, payload: GuptaJaafarPayload, custom_model_dir=None,
                 processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT, custom_options: dict = None) -> (
            Enum, int):
        default_options = {
            "gesture_enum": GESTURE
        }
        options = set_options(default_options, custom_options)
        gesture_enum = options['gesture_enum']

        model_filename = "gupta_jaafar_svm.pkl"
        model_path = os.path.join(custom_model_dir, model_filename) if custom_model_dir is not None else os.path.join(
            ROOT_DIR, "bdgs_trained_models",
            model_filename)

        with open(os.path.join(ROOT_DIR, "bdgs_trained_models", 'gupta_jaafar_pca.pkl'), 'rb') as f:
            pca = pickle.load(f)
        with open(os.path.join(ROOT_DIR, "bdgs_trained_models", 'gupta_jaafar_lda.pkl'), 'rb') as f:
            lda = pickle.load(f)
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        self.process_image(payload=payload, processing_method=processing_method)
        pca_data = pca.transform([self.feature_vector])
        lda_data = lda.transform(pca_data)
        try:
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(lda_data)[0]
                predicted_label = np.argmax(proba)
                certainty = int(np.max(proba) * 100)
            else:
                raise AttributeError
        except (AttributeError, NotImplementedError):
            predictions = model.predict(lda_data)
            predicted_label = predictions[0]
            certainty = 100

        return gesture_enum(predicted_label + 1), certainty

    def learn(self, learning_data: list[GuptaJaafarLearningData], target_model_path: str,
              custom_options: dict = None) -> (float, float):
        default_options = {
            "pca_n_components": 50,
            "lda_n_components": 5
        }
        options = set_options(default_options, custom_options)

        processed_features = []
        etiquettes = []
        for data in learning_data:
            hand_image = cv2.imread(data.image_path)
            self.process_image(payload=GuptaJaafarPayload(image=hand_image, coords=data.coords))
            processed_features.append(self.feature_vector)
            etiquettes.append(data.label.value - 1)
        X = np.array(processed_features)
        y = np.array(etiquettes)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        pca = PCA(n_components=options["pca_n_components"])
        pca_data_train = pca.fit_transform(X_train)
        pca_data_test = pca.transform(X_test)
        lda = LDA(n_components=options["lda_n_components"])
        lda_data_train = lda.fit_transform(pca_data_train, y_train)
        lda_data_test = lda.transform(pca_data_test)
        svm = SVC(kernel='rbf', decision_function_shape='ovo', probability=True)
        svm.fit(lda_data_train, y_train)
        # train_accuracy = svm.score(lda_data_train, y_train)
        test_accuracy = svm.score(lda_data_test, y_test)
        model_path = os.path.join(target_model_path, 'gupta_jaafar_pca.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(pca, f)
        model_path = os.path.join(target_model_path, 'gupta_jaafar_lda.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(lda, f)
        model_path = os.path.join(target_model_path, 'gupta_jaafar_svm.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(svm, f)

        return test_accuracy, None
