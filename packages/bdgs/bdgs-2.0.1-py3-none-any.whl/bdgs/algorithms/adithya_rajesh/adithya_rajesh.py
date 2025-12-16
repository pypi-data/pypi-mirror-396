import os
from enum import Enum

import cv2
import keras
import numpy as np
from keras import Sequential
from keras.src.layers import Rescaling, Conv2D, MaxPooling2D, Flatten, Dense
from keras.src.losses import SparseCategoricalCrossentropy
from keras.src.optimizers import SGD
from sklearn.model_selection import train_test_split

from bdgs.algorithms.adithya_rajesh.adithya_rajesh_learning_data import AdithyaRajeshLearningData
from bdgs.algorithms.adithya_rajesh.adithya_rajesh_payload import AdithyaRajeshPayload
from bdgs.algorithms.bdgs_algorithm import BaseAlgorithm
from bdgs.common.crop_image import crop_image
from bdgs.common.set_options import set_options
from bdgs.data.gesture import GESTURE
from bdgs.data.processing_method import PROCESSING_METHOD
from definitions import ROOT_DIR, NUM_CLASSES


def create_model(num_classes, learning_rate, momentum):
    model = Sequential()
    model.add(Rescaling(1.0 / 255))
    # 1st layer
    model.add(Conv2D(filters=8, kernel_size=(19, 19), padding="same", activation="relu"))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(3, 3)))
    # 2nd layer
    model.add(Conv2D(filters=16, kernel_size=(17, 17), padding="same", activation="relu"))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(3, 3)))
    # 3rd layer
    model.add(Conv2D(filters=32, kernel_size=(15, 15), padding="same", activation="relu"))
    model.add(MaxPooling2D(pool_size=(2, 2), strides=(3, 3)))
    model.add(Flatten())
    model.add(Dense(num_classes, activation="softmax"))
    model.compile(
        optimizer=SGD(learning_rate=learning_rate, momentum=momentum),
        loss=SparseCategoricalCrossentropy(from_logits=False),
        metrics=["accuracy"],
    )
    return model


# def k_fold_train():
#     images, labels = get_training_data()
#     num_classes = len(GESTURE)
# 
#     acc_per_fold = []
#     loss_per_fold = []
#     fold_no = 0
# 
#     kfold = KFold(n_splits=5, shuffle=True)
# 
#     for index, test in kfold.split(images, labels):
#         model = create_model(num_classes)
# 
#         print(f'Training for fold {fold_no} ...')
# 
#         history = model.fit(images[index], labels[index],
#                             batch_size=32,
#                             epochs=2,
#                             verbose="auto")
# 
#         scores = model.evaluate(images[test], labels[test], verbose=0)
# 
#         print(
#             f'Score for fold {fold_no}: {model.metrics_names[0]} of {scores[0]}; {model.metrics_names[1]} of {scores[1] * 100}%')
#         acc_per_fold.append(scores[1] * 100)
#         loss_per_fold.append(scores[0])
#         fold_no = fold_no + 1


class AdithyaRajesh(BaseAlgorithm):
    def process_image(self, payload: AdithyaRajeshPayload,
                      processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT) -> np.ndarray:
        image = payload.image
        coords = payload.coords
        if coords is not None:
            image = crop_image(image=image, coords=coords)
        image = cv2.resize(image, (100, 100))

        return image

    def classify(self, payload: AdithyaRajeshPayload, custom_model_dir=None,
                 processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT,
                 custom_options: dict = None) -> (Enum, int):
        default_options = {
            "gesture_enum": GESTURE
        }
        options = set_options(default_options, custom_options)
        gesture_enum = options['gesture_enum']

        model_filename = "adithya_rajesh.keras"
        model_path = os.path.join(custom_model_dir, model_filename) if custom_model_dir is not None else os.path.join(
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

    def learn(self, learning_data: list[AdithyaRajeshLearningData], target_model_path: str,
              custom_options: dict = None) -> (float, float):
        default_options = {
            "batch_size": 32,
            "epochs": 20,
            "learning_rate": 0.001,
            "momentum": 0.9,
            "num_classes": NUM_CLASSES,
        }
        options = set_options(default_options, custom_options)

        processed_images = []
        labels = []
        for data in learning_data:
            hand_image = cv2.imread(data.image_path)
            processed_image = self.process_image(
                payload=AdithyaRajeshPayload(image=hand_image, coords=data.coords))

            processed_images.append(processed_image)
            labels.append(data.label.value - 1)

        processed_images = np.array(processed_images)
        labels = np.array(labels)

        model = create_model(options['num_classes'], options['learning_rate'], options['momentum'])

        x_train, x_val, y_train, y_val = train_test_split(processed_images, labels, test_size=0.2,
                                                          random_state=42)

        # reduced the epochs from 20 to 3 to reduce overfitting for now.
        history = model.fit(x_train, y_train,
                            validation_data=(x_val, y_val),
                            batch_size=options['batch_size'],
                            epochs=options['epochs'],
                            verbose="auto")

        keras.models.save_model(
            model=model,
            filepath=os.path.join(target_model_path, "adithya_rajesh.keras")
        )
        test_loss, test_acc = model.evaluate(x_val, y_val, verbose=0)

        return test_acc, test_loss
