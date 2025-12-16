import os
from enum import Enum

import cv2
import keras
import numpy as np
from keras import models, layers
from sklearn.model_selection import train_test_split

from bdgs.algorithms.bdgs_algorithm import BaseAlgorithm
from bdgs.algorithms.pinto_borges.pinto_borges_learning_data import PintoBorgesLearningData
from bdgs.algorithms.pinto_borges.pinto_borges_payload import PintoBorgesPayload
from bdgs.common.crop_image import crop_image
from bdgs.common.set_options import set_options
from bdgs.data.gesture import GESTURE
from bdgs.data.processing_method import PROCESSING_METHOD
from definitions import ROOT_DIR, NUM_CLASSES


def skin_segmentation(image: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)

    skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
    return skin_mask


def morphological_processing(mask: np.ndarray) -> np.ndarray:
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))
    eroded = cv2.erode(mask, horizontal_kernel, iterations=1)

    square_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (13, 13))
    closed = cv2.morphologyEx(eroded, cv2.MORPH_CLOSE, square_kernel)

    return closed


def polygonal_approximation(mask: np.ndarray) -> np.ndarray:
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    approx_mask = np.zeros_like(mask)

    for contour in contours:
        epsilon = 0.01 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)
        cv2.drawContours(approx_mask, [approx], -1, (255,), thickness=cv2.FILLED)

    return approx_mask


def apply_mask(image: np.ndarray, mask: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    result = cv2.bitwise_and(gray, gray, mask=mask)
    return result


class PintoBorges(BaseAlgorithm):
    def process_image(self, payload: PintoBorgesPayload,
                      processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT) -> np.ndarray:
        cropped_image = crop_image(payload.image, payload.coords)

        cropped_image = cv2.resize(cropped_image, (100, 100))

        skin_mask = skin_segmentation(cropped_image)
        skin_mask = morphological_processing(skin_mask)
        skin_mask = polygonal_approximation(skin_mask)
        masked_image = apply_mask(cropped_image, skin_mask)

        return masked_image

    def classify(self, payload: PintoBorgesPayload, custom_model_dir=None,
                 processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT,
                 custom_options: dict = None) -> (Enum, int):
        default_options = {
            "gesture_enum": GESTURE
        }
        options = set_options(default_options, custom_options)
        gesture_enum = options['gesture_enum']
        predicted_class = 1
        certainty = 0

        model_filename = "pinto_borges.keras"
        model_path = os.path.join(custom_model_dir, model_filename) if custom_model_dir is not None else os.path.join(
            ROOT_DIR, "bdgs_trained_models",
            model_filename)
        model = keras.models.load_model(model_path)
        processed_image = self.process_image(payload=payload, processing_method=processing_method)
        processed_image = np.expand_dims(processed_image, axis=0)  #

        predictions = model.predict(processed_image, verbose=0)

        for i, prediction in enumerate(predictions):
            predicted_class = np.argmax(prediction) + 1
            certainty = int(np.max(prediction) * 100)

        return gesture_enum(predicted_class), certainty

    def learn(self, learning_data: list[PintoBorgesLearningData], target_model_path: str,
              custom_options: dict = None) -> (float, float):
        default_options = {
            "batch_size": 8,
            "epochs": 10,
            "num_classes": NUM_CLASSES
        }
        options = set_options(default_options, custom_options)
        processed_images = []
        etiquettes = []
        for data in learning_data:
            hand_image = cv2.imread(data.image_path)
            image = self.process_image(
                payload=PintoBorgesPayload(image=hand_image, coords=data.coords)
            )

            processed_images.append(image)
            etiquettes.append(data.label.value - 1)

        X = np.array(processed_images).reshape(-1, 100, 100, 1) / 255.0
        y = np.array(etiquettes)

        X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)

        model = models.Sequential([
            layers.Conv2D(32, (3, 3), activation='relu', input_shape=(100, 100, 1)),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(64, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(128, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dense(400, activation='relu'),
            layers.Dense(800, activation='relu'),
            layers.Dense(options["num_classes"], activation='softmax')
        ])

        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        model.fit(X_train, y_train, epochs=options["epochs"], validation_data=(X_val, y_val), verbose=0,
                  batch_size=options["batch_size"])

        keras.models.save_model(model, os.path.join(target_model_path, 'pinto_borges.keras'))
        test_loss, test_acc = model.evaluate(X_val, y_val, verbose=0)

        return test_acc, test_loss
