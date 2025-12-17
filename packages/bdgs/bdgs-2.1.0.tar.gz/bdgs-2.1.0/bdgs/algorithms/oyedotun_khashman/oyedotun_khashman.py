import os
from enum import Enum

import cv2
import keras
import numpy as np
from keras import Sequential
from keras.src.activations import activations
from keras.src.layers import Rescaling, Conv2D, MaxPooling2D, Flatten, Dense, Dropout, Input
from keras.src.losses import MeanSquaredError
from keras.src.optimizers import SGD
from keras.src.utils import to_categorical
from numpy import ndarray

from bdgs.algorithms.bdgs_algorithm import BaseAlgorithm
from bdgs.algorithms.oyedotun_khashman.oyedotun_khashman_payload import OyedotunKhashmanPayload
from bdgs.common.crop_image import crop_image
from bdgs.common.set_options import set_options
from bdgs.common.dataset_spliter import split_dataset, choose_fit_kwargs
from bdgs.data.gesture import GESTURE
from bdgs.data.processing_method import PROCESSING_METHOD
from bdgs.models.learning_data import LearningData
from definitions import NUM_CLASSES, ROOT_DIR


def extract_hand(image: ndarray):
    binary_image = image.astype(np.uint8)

    ys, xs = np.where(binary_image > 0)
    if len(xs) == 0 or len(ys) == 0:
        return image

    x_min, x_max = np.min(xs), np.max(xs)
    y_min, y_max = np.min(ys), np.max(ys)

    return image[y_min:y_max + 1, x_min:x_max + 1]


def create_model_cnn1(num_classes, learning_rate):
    model = Sequential()
    model.add(Rescaling(1.0 / 255))
    # H1
    model.add(Conv2D(
        filters=6,
        kernel_size=(5, 5),
        activation='log_sigmoid',
        padding='valid'
    ))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    # H2
    model.add(Conv2D(
        filters=12,
        kernel_size=(5, 5),
        activation='log_sigmoid',
        padding='valid'
    ))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(400, activation='log_sigmoid'))

    model.add(Dense(num_classes, activation='softmax'))

    model.compile(
        optimizer=SGD(learning_rate=learning_rate),
        loss=MeanSquaredError(),
        metrics=["accuracy"],
    )
    return model


def create_model_cnn2(num_classes, learning_rate):
    model = Sequential()
    model.add(Rescaling(1.0 / 255))
    # H1
    model.add(Conv2D(
        filters=6,
        kernel_size=(5, 5),
        activation='log_sigmoid',
        padding='valid'
    ))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    # H2
    model.add(Conv2D(
        filters=12,
        kernel_size=(5, 5),
        activation='log_sigmoid',
        padding='valid'
    ))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    # H3
    model.add(Conv2D(
        filters=12,
        kernel_size=(5, 5),
        activation='log_sigmoid',
        padding='valid'
    ))
    model.add(MaxPooling2D(pool_size=(3, 3)))

    model.add(Flatten())
    model.add(Dense(400, activation='log_sigmoid'))

    # model.add(Dense(NUM_CLASSES, activation='log_sigmoid'))
    model.add(Dense(num_classes, activation='softmax'))

    model.compile(
        optimizer=SGD(learning_rate=learning_rate),
        loss=MeanSquaredError(),
        metrics=["accuracy"],
    )
    return model


def create_model_cnn3(num_classes, learning_rate):
    model = Sequential()
    model.add(Rescaling(1.0 / 255))
    # H1
    model.add(Conv2D(
        filters=5,
        kernel_size=(3, 3),
        activation='log_sigmoid',
        padding='valid'
    ))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    # H2
    model.add(Conv2D(
        filters=10,
        kernel_size=(4, 4),
        activation='log_sigmoid',
        padding='valid'
    ))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    # H3
    model.add(Conv2D(
        filters=15,
        kernel_size=(3, 3),
        activation='log_sigmoid',
        padding='valid'
    ))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    # H4
    model.add(Conv2D(
        filters=20,
        kernel_size=(3, 3),
        activation='log_sigmoid',
        padding='valid'
    ))
    model.add(MaxPooling2D(pool_size=(2, 2)))

    model.add(Flatten())
    model.add(Dense(400, activation='log_sigmoid'))

    # model.add(Dense(NUM_CLASSES, activation='log_sigmoid'))
    model.add(Dense(num_classes, activation='softmax'))

    model.compile(
        optimizer=SGD(learning_rate=learning_rate),
        loss=MeanSquaredError(),
        metrics=["accuracy"],
    )
    return model


def create_dae(x_train, input_dims, output_dims, num_epoch):
    model = Sequential()
    model.add(Input(shape=(input_dims,)))
    model.add(Dropout(0.5))  # noise
    model.add(Dense(output_dims, activation=activations.sigmoid))  # encoder
    model.add(Dense(input_dims, activation=activations.sigmoid))  # decoder
    model.compile(loss=MeanSquaredError(), optimizer=SGD(learning_rate=0.8))
    model.fit(x_train, x_train, epochs=num_epoch, batch_size=5)

    # model.summary()

    return model


def sdae_pretrain(x_train, layers, pretrain_epochs=5):
    pretrained = []
    current_data = x_train

    for i in range(len(layers) - 1):
        dae = create_dae(
            current_data,
            layers[i],
            layers[i + 1],
            pretrain_epochs
        )
        pretrained.append(dae)

        encoder_layer = next(l for l in dae.layers if isinstance(l, Dense))
        encoder_weights = encoder_layer.get_weights()

        encoder_model = Sequential([Input(shape=(layers[i],)), Dense(layers[i + 1], activation=activations.sigmoid)])
        encoder_model.layers[-1].set_weights(encoder_weights)

        current_data = encoder_model.predict(current_data, verbose=0)

    return pretrained


def sdae_fine_tuning(num_classes, x_train, y_train, x_val, y_val, layers, fine_tune_epochs=200):
    pretrained = sdae_pretrain(x_train, layers, pretrain_epochs=10)

    model = Sequential()
    model.add(Input(shape=(layers[0],)))
    model.add(Dropout(0.5))

    for i, dae in enumerate(pretrained):
        weights = next(l for l in dae.layers if isinstance(l, Dense)).get_weights()
        model.add(Dense(layers[i + 1], activation=activations.sigmoid))
        model.layers[-1].set_weights(weights)
    # model.summary()

    model.add(Dense(num_classes, activation=activations.softmax))

    optimizer = SGD(learning_rate=0.4, momentum=0.5)
    model.compile(loss="categorical_crossentropy", optimizer=optimizer, metrics=['accuracy'])
    history = model.fit(x_train, y_train, epochs=fine_tune_epochs, batch_size=4, validation_data=(x_val, y_val))
    return model


class OyedotunKhashman(BaseAlgorithm):
    def process_image(self, payload: OyedotunKhashmanPayload,
                      processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT) -> ndarray:
        if payload.coords is not None:
            img = crop_image(payload.image, payload.coords)
        else:
            img = payload.image

        gray_image = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
        _, binary_threshed = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
        # authors specieid the size of median filter (15 x 10)
        median_filtered = cv2.medianBlur(binary_threshed, 13)
        extracted_hand = extract_hand(median_filtered)
        # For CNN1 add SDAEs  rescale to 32x32
        # resized = cv2.resize(extracted_hand, (32, 32), interpolation=cv2.INTER_AREA)
        # For CNN2 and CNN3 rescale to 64x64
        resized = cv2.resize(extracted_hand, (64, 64), interpolation=cv2.INTER_AREA)

        return resized

    def classify(self, payload: OyedotunKhashmanPayload, custom_model_dir=None,
                 processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT,
                 custom_options: dict = None) -> (Enum, int):
        default_options = {
            "gesture_enum": GESTURE
        }
        options = set_options(default_options, custom_options)
        gesture_enum = options['gesture_enum']

        model_filename = "oyedotun_khashman.keras"
        model_path = os.path.join(custom_model_dir, model_filename) if custom_model_dir is not None else os.path.join(
            ROOT_DIR, "bdgs_trained_models",
            model_filename)

        model = keras.models.load_model(model_path)
        processed_image = self.process_image(payload=payload)
        expanded_dims = np.expand_dims(processed_image, axis=0)
        # reshaped_to_vector = expanded_dims.reshape(expanded_dims.shape[0], -1)
        # normalized = reshaped_to_vector.astype("float32") / 255.0
        predictions = model.predict(expanded_dims, verbose=0)

        predicted_class = 1
        certainty = 0
        for prediction in predictions:
            predicted_class = np.argmax(prediction) + 1
            certainty = int(np.max(prediction) * 100)

        return gesture_enum(predicted_class), certainty

    def learn(self, learning_data: list[LearningData], target_model_path: str, custom_options: dict = None) -> (float,
                                                                                                                float):
        # these are defualt for CNN2
        default_options = {
            "batch_size": 5,
            "epochs": 400,
            "learning_rate": 0.8,
            "num_classes": NUM_CLASSES,
            "test_subset_size": 0.2
        }
        options = set_options(default_options, custom_options)
        processed_images = []
        labels = []
        for data in learning_data:
            hand_image = cv2.imread(data.image_path)
            processed_image = self.process_image(
                payload=OyedotunKhashmanPayload(image=hand_image, coords=data.coords))

            processed_images.append(processed_image)
            labels.append(data.label.value - 1)

        processed_images = np.array(processed_images)
        labels = np.array(labels)

        x_train, x_val, y_train, y_val = split_dataset(processed_images, labels, test_size=options["test_subset_size"],
                                                          random_state=42)

        x_train = np.expand_dims(x_train, axis=-1)
        y_train = to_categorical(y_train, options["num_classes"])

        if x_val is not None and y_val is not None:
            y_val = to_categorical(y_val, options["num_classes"])
            x_val = np.expand_dims(x_val, axis=-1)

        # For CNNs training:
        model = create_model_cnn2(options["num_classes"], options["learning_rate"])
        history = model.fit(**choose_fit_kwargs(x_train, y_train,
                            validation_data=(x_val, y_val),
                            batch_size=options["batch_size"],
                            epochs=options["epochs"],
                            verbose="auto"))
        if x_val is not None and y_val is not None:
            test_loss, test_acc = model.evaluate(x_val, y_val, verbose=0)
        else:
            test_loss, test_acc = model.evaluate(x_train, y_train, verbose=0)

        # FOR SDAES:

        # reshape img to vector, for example 32x32 -> 1024 x 1
        # x_train = x_train.reshape(x_train.shape[0], -1)
        # x_val = x_val.reshape(x_val.shape[0], -1)

        # normalize
        # x_train = x_train.astype("float32") / 255.0
        # x_val = x_val.astype("float32") / 255.0

        # y_train = to_categorical(y_train, NUM_CLASSES)
        # y_val = to_categorical(y_val, NUM_CLASSES)

        # model = sdae_fine_tuning(
        #    num_classes=options["num_classes"]
        #    x_train=x_train,
        #    y_train=y_train,
        #    x_val=x_val,
        #    y_val=y_val,
        #    layers=[32*32, 120, 90, 50, 40],
        #    fine_tune_epochs=300
        # )

        keras.models.save_model(
            model=model,
            filepath=os.path.join(target_model_path, "oyedotun_khashman.keras")
        )
        # test_loss, test_acc = model.evaluate(x_val, y_val, verbose=0)

        return test_acc, test_loss
