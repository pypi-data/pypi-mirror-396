import os
import pickle
from enum import Enum

import cv2
import numpy as np
from sklearn.neighbors import KNeighborsClassifier

from bdgs.algorithms.bdgs_algorithm import BaseAlgorithm
from bdgs.algorithms.chang_chen.chang_chen_learning_data import ChangChenLearningData
from bdgs.algorithms.chang_chen.chang_chen_payload import ChangChenPayload
from bdgs.common.crop_image import crop_image
from bdgs.common.set_options import set_options
from bdgs.data.gesture import GESTURE
from bdgs.data.processing_method import PROCESSING_METHOD
from definitions import ROOT_DIR


def extract_features(image: np.ndarray) -> np.ndarray:
    moments = cv2.moments(image)
    hu = cv2.HuMoments(moments).flatten()
    return np.log(np.abs(hu) + 1e-10)


class ChangChen(BaseAlgorithm):

    def process_image(self, payload: ChangChenPayload,
                      processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT) -> np.ndarray:
        image = payload.image
        coords = payload.coords
        if coords is not None:
            image = crop_image(image=image, coords=coords)

        image = cv2.resize(image, (100, 100))
        processed = image.copy()

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower_skin = np.array([0, 30, 60], dtype=np.uint8)
        upper_skin = np.array([20, 150, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        silhouette = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))

        contours, _ = cv2.findContours(silhouette, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            return processed

        cnt = max(contours, key=cv2.contourArea)
        (x_center, y_center), radius = cv2.minEnclosingCircle(cnt)
        center = (int(x_center), int(y_center))
        radius = int(radius)

        palm_mask = np.zeros_like(silhouette)
        cv2.circle(palm_mask, center, int(radius * 0.6), 255, -1)
        palm_part = cv2.bitwise_and(silhouette, palm_mask)
        finger_part = cv2.subtract(silhouette, palm_part)

        cv2.circle(processed, center, radius, (0, 255, 0), 2)
        cv2.circle(processed, center, int(radius * 0.6), (255, 0, 0), 1)
        processed[finger_part > 0] = [0, 255, 255]
        processed[palm_part > 0] = [255, 0, 255]

        return processed

    def classify(self, payload: ChangChenPayload, custom_model_dir=None,
                 processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT,
                 custom_options: dict = None) -> (Enum, int):
        default_options = {
            "gesture_enum": GESTURE
        }
        options = set_options(default_options, custom_options)
        gesture_enum = options['gesture_enum']

        model_filename = "chang_chen.pkl"
        model_path = os.path.join(custom_model_dir, model_filename) if custom_model_dir is not None else os.path.join(
            ROOT_DIR, "bdgs_trained_models", model_filename)

        with open(model_path, "rb") as f:
            model = pickle.load(f)

        processed_image = self.process_image(payload, processing_method)
        gray = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
        features = extract_features(gray).reshape(1, -1)

        prediction = model.predict(features)
        distances, indices = model.kneighbors(features, n_neighbors=1)
        confidence = round(100 * (1 / (1 + distances[0][0])), 0)

        return gesture_enum(prediction[0] + 1), confidence

    def learn(self, learning_data: list[ChangChenLearningData], target_model_path: str,
              custom_options: dict = None) -> (float, float):
        default_options = {
            "n_neighbors": 1
        }
        options = set_options(default_options, custom_options)
        X, y = [], []

        for data in learning_data:
            image = cv2.imread(data.image_path)
            processed = self.process_image(ChangChenPayload(image, data.coords))
            gray = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
            features = extract_features(gray)

            if features is not None and features.size > 0:
                X.append(features)
                y.append(data.label.value - 1)

        X, y = np.array(X), np.array(y)
        model = KNeighborsClassifier(n_neighbors=options["n_neighbors"])
        model.fit(X, y)
        accuracy = model.score(X, y)

        model_path = os.path.join(target_model_path, "chang_chen.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(model, f)

        return accuracy, None
