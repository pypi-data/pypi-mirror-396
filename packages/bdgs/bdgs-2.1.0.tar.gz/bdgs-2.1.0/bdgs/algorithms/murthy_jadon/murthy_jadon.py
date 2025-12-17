import os.path
from enum import Enum

import cv2
import keras
import numpy as np

from bdgs.algorithms.bdgs_algorithm import BaseAlgorithm
from bdgs.algorithms.murthy_jadon.murthy_jadon_learning_data import MurthyJadonLearningData
from bdgs.algorithms.murthy_jadon.murthy_jadon_payload import MurthyJadonPayload
from bdgs.common.set_options import set_options
from bdgs.common.dataset_spliter import split_dataset, choose_fit_kwargs
from bdgs.data.gesture import GESTURE
from bdgs.data.processing_method import PROCESSING_METHOD
from definitions import ROOT_DIR, NUM_CLASSES


def subtract_background(background, image):
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=2, varThreshold=50, detectShadows=False)
    bg_subtractor.apply(background)
    fg_mask = bg_subtractor.apply(image)

    kernel = np.ones((3, 3), np.uint8)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_DILATE, kernel)
    _, fg_mask = cv2.threshold(fg_mask, 127, 255, cv2.THRESH_BINARY)
    fg_color = cv2.bitwise_and(image, image, mask=fg_mask)

    return fg_color


def extract_hand_region(image):
    image = image.astype(np.uint8)
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return image, (0, 0, 0, 0)
    largest_contour = max(contours, key=cv2.contourArea)

    hand_mask = np.zeros_like(image, dtype=np.uint8)
    cv2.drawContours(hand_mask, [largest_contour], -1, [255], thickness=cv2.FILLED)

    x, y, w, h = cv2.boundingRect(largest_contour)
    hand_region = hand_mask[y:y + h, x:x + w]

    cut_ratio = 0.2
    cut_height = int(h * (1 - cut_ratio))
    hand_region = hand_region[:cut_height, :]

    result = cv2.bitwise_not(hand_region)
    return result


class MurthyJadon(BaseAlgorithm):
    def process_image(self, payload: MurthyJadonPayload,
                      processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT) -> np.ndarray:
        if processing_method == PROCESSING_METHOD.DEFAULT or processing_method == PROCESSING_METHOD.MURTHY_JADON_PROC:
            image = payload.image
            background = payload.bg_image

            subtracted = subtract_background(background, image)
            gray = cv2.cvtColor(subtracted, cv2.COLOR_BGR2GRAY)
            hand_only = extract_hand_region(gray)
            try:
                resized = cv2.resize(hand_only, (30, 30))
            except:
                return cv2.resize(gray, (30, 30))

            return resized
        else:
            raise Exception("Invalid processing method")

    def classify(self, payload: MurthyJadonPayload, custom_model_dir=None,
                 processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT,
                 custom_options: dict = None) -> (Enum, int):
        default_options = {
            "gesture_enum": GESTURE
        }
        options = set_options(default_options, custom_options)
        gesture_enum = options['gesture_enum']

        predicted_class = 1
        certainty = 0

        model_filename = "murthy_jadon.keras"
        model_path = os.path.join(custom_model_dir, model_filename) if custom_model_dir is not None else os.path.join(
            ROOT_DIR, "bdgs_trained_models",
            model_filename)

        model = keras.models.load_model(model_path)
        processed_image = (self.process_image(payload=payload, processing_method=processing_method).flatten()) / 255
        processed_image = np.expand_dims(processed_image, axis=0)  #

        predictions = model.predict(processed_image, verbose=0)

        for i, prediction in enumerate(predictions):
            predicted_class = np.argmax(prediction) + 1
            certainty = int(np.max(prediction) * 100)

        return gesture_enum(predicted_class), certainty

    def learn(self, learning_data: list[MurthyJadonLearningData], target_model_path: str,
              custom_options: dict = None) -> (float, float):
        default_options = {
            "epochs": 80,
            "num_classes": NUM_CLASSES,
            "test_subset_size": 0.2
        }
        options = set_options(default_options, custom_options)
        processed_images = []
        etiquettes = []
        for data in learning_data:
            hand_image = cv2.imread(data.image_path)
            background_image = cv2.imread(data.bg_image_path)
            processed_image = (self.process_image(
                payload=MurthyJadonPayload(image=hand_image, bg_image=background_image)
            ).flatten()) / 255

            processed_images.append(processed_image)
            etiquettes.append(data.label.value - 1)

        X_train, X_val, y_train, y_val = split_dataset(np.array(processed_images), np.array(etiquettes),
                                                          test_size=options["test_subset_size"],
                                                          random_state=42)

        model = keras.Sequential([
            keras.layers.InputLayer(input_shape=(900,)),
            keras.layers.Dense(14, activation='relu'),
            keras.layers.Dense(options["num_classes"], activation='softmax')
        ])
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        model.fit(**choose_fit_kwargs(X_train, y_train, epochs=options["epochs"], validation_data=(X_val, y_val), verbose=0))
        keras.models.save_model(model, os.path.join(target_model_path, 'murthy_jadon.keras'))

        if X_val is not None and y_val is not None:
            test_loss, test_acc = model.evaluate(X_val, y_val, verbose=0)
        else:
            test_loss, test_acc = model.evaluate(X_train, y_train, verbose=0)

        return test_acc, test_loss
