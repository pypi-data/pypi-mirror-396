import os
from enum import Enum

import cv2
import keras
import numpy as np
from keras import models, layers

from bdgs.algorithms.bdgs_algorithm import BaseAlgorithm
from bdgs.common.set_options import set_options
from bdgs.common.dataset_spliter import split_dataset, choose_fit_kwargs
from bdgs.data.gesture import GESTURE
from bdgs.data.processing_method import PROCESSING_METHOD
from bdgs.models.image_payload import ImagePayload
from bdgs.models.learning_data import LearningData
from definitions import ROOT_DIR, NUM_CLASSES


def segment_skin(image: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_skin = np.array([0, 0, 0], dtype=np.uint8)
    upper_skin = np.array([38, 255, 255], dtype=np.uint8)
    mask = cv2.inRange(hsv, lower_skin, upper_skin)
    return cv2.bitwise_and(image, image, mask=mask)


class EidSchwenker(BaseAlgorithm):
    def process_image(self, payload: ImagePayload,
                      processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT) -> np.ndarray:
        if processing_method == PROCESSING_METHOD.DEFAULT or processing_method == PROCESSING_METHOD.EID_SCHWENKER:
            image = payload.image

            processed = segment_skin(image)
            processed = cv2.cvtColor(processed, cv2.COLOR_BGR2GRAY)
            processed = cv2.resize(processed, (32, 32))
            return processed
        else:
            raise Exception("Invalid processing method")

    def classify(self, payload: ImagePayload, custom_model_dir=None,
                 processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT, custom_options: dict = None) -> (
            Enum, int):
        default_options = {
            "gesture_enum": GESTURE
        }
        options = set_options(default_options, custom_options)
        gesture_enum = options['gesture_enum']

        predicted_class = 1
        certainty = 0

        model_filename = "eid_schwenker.keras"
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

    def learn(self, learning_data: list[LearningData], target_model_path: str, custom_options: dict = None) -> (float,
                                                                                                                float):
        default_options = {
            "epochs": 100,
            "batch_size": 8,
            "num_classes": NUM_CLASSES,
            "test_subset_size": 0.2
        }
        options = set_options(default_options, custom_options)
        processed_images = []
        etiquettes = []

        for data in learning_data:
            hand_image = cv2.imread(data.image_path)
            processed_image = self.process_image(
                payload=ImagePayload(image=hand_image)
            )

            processed_images.append(processed_image)
            etiquettes.append(data.label.value - 1)

        X = np.array(processed_images).reshape(-1, 32, 32, 1)
        y = np.array(etiquettes)

        X_train, X_val, y_train, y_val = split_dataset(X, y, test_size=options["test_subset_size"], random_state=42)

        model = models.Sequential([
            layers.Conv2D(15, (6, 6), activation='relu', input_shape=(32, 32, 1)),
            layers.MaxPooling2D((2, 2)),
            layers.Conv2D(32, (3, 3), activation='relu'),
            layers.MaxPooling2D((2, 2)),
            layers.Flatten(),
            layers.Dropout(0.5),
            layers.Dense(64, activation='relu'),
            layers.Dense(options['num_classes'], activation='softmax')
        ])

        model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
        model.fit(**choose_fit_kwargs(X_train, y_train, epochs=options["epochs"], validation_data=(X_val, y_val), verbose=0,
                  batch_size=options["batch_size"]))
        keras.models.save_model(model, os.path.join(target_model_path, 'eid_schwenker.keras'))
        if X_val is not None and y_val is not None:
            test_loss, test_acc = model.evaluate(X_val, y_val, verbose=0)
        else:
            test_loss, test_acc = model.evaluate(X_train, y_train, verbose=0)

        return test_acc, test_loss
