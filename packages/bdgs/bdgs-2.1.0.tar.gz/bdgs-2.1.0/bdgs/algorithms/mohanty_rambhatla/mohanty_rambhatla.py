import os

import cv2
import keras
import numpy as np
from keras import Sequential
from keras.src.layers import Rescaling, Conv2D, MaxPooling2D, Flatten, Dense, Dropout, Activation
from keras.src.optimizers import SGD
from keras.src.utils import to_categorical
from numpy import ndarray

from bdgs.algorithms.bdgs_algorithm import BaseAlgorithm
from bdgs.algorithms.mohanty_rambhatla.mohanty_rambhatla_payload import MohantyRambhatlaPayload
from bdgs.common.crop_image import crop_image
from bdgs.common.set_options import set_options
from bdgs.common.dataset_spliter import split_dataset, choose_fit_kwargs
from bdgs.data.gesture import GESTURE
from bdgs.data.processing_method import PROCESSING_METHOD
from bdgs.models.learning_data import LearningData
from definitions import ROOT_DIR, NUM_CLASSES


def augment(image: ndarray, repeat_num: int, target_size: tuple[int, int] = (32, 32)):
    images = []

    for i in range(1, repeat_num + 1):
        cropped = image[i:, i:]
        resized = cv2.resize(cropped, target_size)
        images.append(resized)

    return images


def create_model(learning_rate: float, use_relu: bool,
                 num_classes: int, dropout_rate: float = 0.5):
    model = Sequential()
    model.add(Rescaling(1.0 / 255))

    model.add(Conv2D(filters=10, kernel_size=(5, 5)))
    model.add(Activation('relu' if use_relu else 'sigmoid'))
    if dropout_rate > 0:
        model.add(Dropout(dropout_rate))

    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Conv2D(filters=20, kernel_size=(5, 5)))
    model.add(Activation('relu' if use_relu else 'sigmoid'))
    if dropout_rate > 0:
        model.add(Dropout(dropout_rate))

    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Flatten())
    model.add(Dense(num_classes, activation='relu' if use_relu else 'sigmoid'))

    model.compile(
        optimizer=SGD(learning_rate=learning_rate),
        loss='mean_squared_error',
        metrics=["accuracy"],
    )
    return model


class MohantyRambhatla(BaseAlgorithm):
    def process_image(self, payload: MohantyRambhatlaPayload,
                      processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT) -> ndarray:
        image = payload.image
        coords = payload.coords
        if coords is not None:
            image = crop_image(image=image, coords=coords)
        image = cv2.resize(image, (32, 32))

        return image

    def classify(self, payload: MohantyRambhatlaPayload, custom_model_path=None,
                 processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT,
                 custom_options: dict = None) -> GESTURE:
        default_options = {
            "gesture_enum": GESTURE
        }
        options = set_options(default_options, custom_options)
        gesture_enum = options['gesture_enum']

        model_filename = "mohanty_rambhatla.keras"
        model_path = os.path.join(custom_model_path, model_filename) if custom_model_path is not None else os.path.join(
            ROOT_DIR, "bdgs_trained_models",
            model_filename)

        model = keras.models.load_model(model_path)
        processed_image = self.process_image(payload=payload)
        expanded_dims = np.expand_dims(processed_image, axis=0)
        predictions = model.predict(expanded_dims, verbose=0)

        predicted_class = 1
        certainty = 0
        for prediction in predictions:
            predicted_class = np.argmax(prediction) + 1
            certainty = int(np.max(prediction) * 100)

        return gesture_enum(predicted_class), certainty

    def learn(self, learning_data: list[LearningData], target_model_path: str
              , custom_options: dict = None) -> (float, float):

        # Note: The paper mentioned these parameters to achieve the best results:
        # enable_augmentation = False
        # learning_rate = 5e-6
        # epochs = 2000
        # batch_size = 10
        # use_relu = True
        # dropout_rate = 0.5
        #
        # However, based on test found parameters specified 
        # in default_options to have better performance on BDSG dataset:
        default_options = {
            "batch_size": 32,
            "epochs": 120,
            "learning_rate": 0.01,
            "enable_augmentation": False,
            "dropout_rate": 0.5,
            "use_relu": True,
            "num_classes": NUM_CLASSES,
            "test_subset_size": 0.2
        }
        options = set_options(default_options, custom_options)

        processed_images = []
        labels = []
        for data in learning_data:
            hand_image = cv2.imread(data.image_path)

            processed_image = self.process_image(
                payload=MohantyRambhatlaPayload(image=hand_image, coords=data.coords))

            if options["enable_augmentation"]:
                augmented_images = augment(processed_image, 5)
                for augmented_image in augmented_images:
                    processed_images.append(augmented_image)
                    labels.append(data.label.value - 1)
            else:
                processed_images.append(processed_image)
                labels.append(data.label.value - 1)

        processed_images = np.array(processed_images)
        labels = np.array(labels)

        model = create_model(learning_rate=options["learning_rate"],
                             use_relu=options["use_relu"], num_classes=options["num_classes"],
                             dropout_rate=options["dropout_rate"])

        x_train, x_val, y_train, y_val = split_dataset(processed_images, labels, test_size=options["test_subset_size"],
                                                          random_state=42)

        y_train = to_categorical(y_train, num_classes=options["num_classes"])
        if y_val is not None:
            y_val = to_categorical(y_val, num_classes=options["num_classes"])

        history = model.fit(**choose_fit_kwargs(x_train, y_train,
                            validation_data=(x_val, y_val),
                            batch_size=options["batch_size"],
                            epochs=options["epochs"],
                            verbose=0))

        keras.models.save_model(
            model=model,
            filepath=os.path.join(target_model_path, "mohanty_rambhatla.keras")
        )
        
        if x_val is not None and y_val is not None:
            test_loss, test_acc = model.evaluate(x_val, y_val, verbose=0)
        else:
            test_loss, test_acc = model.evaluate(x_train, y_train, verbose=0)

        return test_acc, test_loss
