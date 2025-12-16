import os
import pickle
from enum import Enum

import cv2
import numpy as np
from numpy import ndarray
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from bdgs.algorithms.bdgs_algorithm import BaseAlgorithm
from bdgs.algorithms.joshi_kumar.joshi_kumar_payload import JoshiKumarPayload
from bdgs.common.crop_image import crop_image
from bdgs.common.set_options import set_options
from bdgs.data.gesture import GESTURE
from bdgs.data.processing_method import PROCESSING_METHOD
from definitions import ROOT_DIR


def reorient_image(img: ndarray) -> ndarray:
    moments = cv2.moments(img)
    if moments["m00"] == 0:
        return img

    mu20 = moments["mu20"]
    mu02 = moments["mu02"]
    mu11 = moments["mu11"]

    angle = 0.5 * np.arctan2(2 * mu11, mu20 - mu02)
    angle_deg = np.degrees(angle)

    h, w = img.shape
    if w > h:
        angle_deg += 90

    rotation_matrix = cv2.getRotationMatrix2D((w // 2, h // 2), angle_deg, 1.0)
    rotated = cv2.warpAffine(img, rotation_matrix, (w, h), flags=cv2.INTER_LINEAR, borderValue=0)

    return rotated


def crop_to_roi(img: ndarray) -> ndarray:
    vertical_sum = np.sum(img, axis=0)
    horizontal_sum = np.sum(img, axis=1)

    x_nonzero = np.where(vertical_sum > 0)[0]
    y_nonzero = np.where(horizontal_sum > 0)[0]

    if len(x_nonzero) == 0 or len(y_nonzero) == 0:
        return img

    x_start, x_end = x_nonzero[0], x_nonzero[-1]
    y_start, y_end = y_nonzero[0], y_nonzero[-1]

    cropped = img[y_start:y_end, x_start:x_end]
    return cropped


def normalize_image(img: ndarray) -> ndarray:
    img = img.astype(np.float32)
    mean, std = cv2.meanStdDev(img)
    std = std if std != 0 else 1.0
    normalized = (img - mean) / std
    return normalized


class JoshiKumar(BaseAlgorithm):
    def process_image(self, payload: JoshiKumarPayload,
                      processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT) -> ndarray:
        image = payload.image
        coords = payload.coords
        if coords is not None:
            image = crop_image(image=image, coords=coords)

        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        _, segmented = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        reoriented = reorient_image(segmented)

        cropped = crop_to_roi(reoriented)
        normalized = normalize_image(cropped)

        fixed_size = (90, 60)
        normalized = cv2.resize(normalized, fixed_size)

        return normalized

    def learn(self, learning_data: list, target_model_path: str, custom_options: dict = None) -> (float, float):
        default_options = {
            "n_components": 0.95
        }
        options = set_options(default_options, custom_options)
        X, y = [], []

        for data in learning_data:
            image = cv2.imread(data.image_path)
            processed = self.process_image(JoshiKumarPayload(image, data.coords))
            features = processed.flatten()

            X.append(features)
            y.append(data.label.value - 1)

        X, y = np.array(X), np.array(y)
        pca = PCA(n_components=options["n_components"], svd_solver='full')

        svm = SVC(kernel='rbf', probability=True)
        pipeline = make_pipeline(StandardScaler(), pca, svm)

        pipeline.fit(X, y)

        y_pred = pipeline.predict(X)
        accuracy = accuracy_score(y, y_pred)

        os.makedirs(target_model_path, exist_ok=True)
        model_path = os.path.join(target_model_path, "joshi_kumar.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(pipeline, f)

        return accuracy, None

    def classify(self, payload: JoshiKumarPayload, custom_model_path=None,
                 processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT,
                 custom_options: dict = None) -> (Enum, int):
        default_options = {
            "gesture_enum": GESTURE
        }
        options = set_options(default_options, custom_options)
        gesture_enum = options['gesture_enum']

        model_path = os.path.join(custom_model_path or os.path.join(ROOT_DIR, "bdgs_trained_models"), "joshi_kumar.pkl")

        with open(model_path, "rb") as f:
            model = pickle.load(f)

        processed_image = self.process_image(payload, processing_method)
        features = processed_image.flatten().reshape(1, -1)

        prediction = model.predict(features)
        proba = model.predict_proba(features)
        confidence = round(100 * np.max(proba), 0)

        return gesture_enum(prediction[0] + 1), confidence
