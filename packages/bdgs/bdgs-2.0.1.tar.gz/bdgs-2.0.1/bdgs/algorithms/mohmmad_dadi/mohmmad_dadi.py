import os
import pickle
from enum import Enum

import cv2
import numpy as np
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC

from bdgs.algorithms.bdgs_algorithm import BaseAlgorithm
from bdgs.common.set_options import set_options
from bdgs.data.gesture import GESTURE
from bdgs.data.processing_method import PROCESSING_METHOD
from bdgs.models.image_payload import ImagePayload
from bdgs.models.learning_data import LearningData
from definitions import ROOT_DIR


class MohmmadDadi(BaseAlgorithm):
    def process_image(self, payload: ImagePayload,
                      processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT) -> np.ndarray:
        # Experimental
        if processing_method != PROCESSING_METHOD.DEFAULT:
            from bdgs.data.algorithm_functions import ALGORITHM_FUNCTIONS
            return ALGORITHM_FUNCTIONS[processing_method].process_image(payload)

        gray = cv2.cvtColor(payload.image, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, (100, 100))  # added
        _, binary = cv2.threshold(resized, 127, 255, cv2.THRESH_BINARY)
        kernel = np.ones((3, 3), np.uint8)
        eroded = cv2.erode(binary, kernel, iterations=2)
        dilated = cv2.dilate(eroded, kernel, iterations=1)
        processed = cv2.subtract(binary, dilated)
        edges = cv2.Canny(processed, threshold1=100, threshold2=200)
        return edges

    def classify(self, payload: ImagePayload, custom_model_dir=None,
                 processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT,
                 custom_options: dict = None) -> (Enum, int):
        default_options = {
            "gesture_enum": GESTURE
        }
        options = set_options(default_options, custom_options)
        gesture_enum = options['gesture_enum']

        model_filename = "mohmmad_dadi_svm.pkl"
        model_path = os.path.join(custom_model_dir, model_filename) if custom_model_dir is not None else os.path.join(
            ROOT_DIR, "bdgs_trained_models",
            model_filename)

        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        with open(os.path.join(ROOT_DIR, "bdgs_trained_models", 'mohmmad_dadi_pca.pkl'), 'rb') as f:
            pca = pickle.load(f)

        processed_image = self.process_image(payload=payload, processing_method=processing_method).flatten()
        processed_image_pca = pca.transform([processed_image])
        try:
            if hasattr(model, "predict_proba"):
                proba = model.predict_proba(processed_image_pca)[0]
                predicted_label = np.argmax(proba)
                certainty = int(np.max(proba) * 100)
            else:
                raise AttributeError
        except (AttributeError, NotImplementedError):
            predictions = model.predict(processed_image_pca)
            predicted_label = predictions[0]
            certainty = 100

        return gesture_enum(predicted_label + 1), certainty

    def learn(self, learning_data: list[LearningData], target_model_path: str, custom_options: dict = None) -> (float,
                                                                                                                float):
        default_options = {
            "n_components": 50,
        }
        options = set_options(default_options, custom_options)

        processed_images = []
        etiquettes = []
        for data in learning_data:
            hand_image = cv2.imread(data.image_path)
            processed_image = (self.process_image(
                payload=ImagePayload(image=hand_image)
            )).flatten()
            processed_images.append(processed_image)
            etiquettes.append(data.label.value - 1)

        X = np.array(processed_images)
        y = np.array(etiquettes)

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        pca = PCA(n_components=options["n_components"])  # PCA can be replaced by LDA
        X_train_pca = pca.fit_transform(X_train)
        X_test_pca = pca.transform(X_test)

        # # KNN is alternative for SVM
        # knn = KNeighborsClassifier(n_neighbors=5)
        # knn.fit(X_train_pca, y_train)
        # knn_accuracy = knn.score(X_test_pca, y_test)
        # print(f"KNN Accuracy: {knn_accuracy * 100:.2f}%")

        svm = SVC(kernel='linear', probability=True)
        svm.fit(X_train_pca, y_train)
        svm_accuracy = svm.score(X_test_pca, y_test)
        # print(f"SVM Accuracy: {svm_accuracy * 100:.2f}%")

        model_path = os.path.join(target_model_path, 'mohmmad_dadi_pca.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(pca, f)

        # # KNN is alternative for SVM
        # model_path = os.path.join(target_model_path, 'mohmmad_dadi_knn.pkl')
        # with open(model_path, 'wb') as f:
        #     pickle.dump(knn, f)

        model_path = os.path.join(target_model_path, 'mohmmad_dadi_svm.pkl')
        with open(model_path, 'wb') as f:
            pickle.dump(svm, f)

        return svm_accuracy, None
