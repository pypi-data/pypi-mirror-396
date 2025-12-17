import os
from enum import Enum

from numpy import ndarray

from bdgs.data.algorithm import ALGORITHM
from bdgs.data.algorithm_functions import ALGORITHM_FUNCTIONS
from bdgs.data.processing_method import PROCESSING_METHOD
from bdgs.models.image_payload import ImagePayload
from bdgs.models.learning_data import LearningData


def process_image(algorithm: ALGORITHM, payload: ImagePayload,
                  processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT) -> ndarray:
    """
    Preprocesses an image

    :param algorithm: ALGORITHM enum value specifying the preprocessing algorithm.
    :param payload: Image payload class instance
    :param processing_method: A PROCESSING_METHOD enum value, defaults to PROCESSING_METHOD.DEFAULT.

    :return:
        Numpy ndarray
    """
    classifier = ALGORITHM_FUNCTIONS[algorithm]
    processed = classifier.process_image(payload, processing_method)

    return processed


def classify(algorithm: ALGORITHM, payload: ImagePayload, custom_model_dir=None,
             processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT,
             custom_options: dict = None) -> (Enum, int):
    """
    Classifies an image using the specified gesture recognition algorithm.

    :param algorithm: ALGORITHM enum value specifying the training algorithm.
    :param payload: Image payload class instance
    :param custom_model_dir: Optional path to a directory containing a custom pre-trained model.
    :param processing_method: A PROCESSING_METHOD enum value, defaults to PROCESSING_METHOD.DEFAULT.
    :param custom_options: Optional dictionary to override default training parameters.

    :return: Tuple (prediction, certainty)
            
    """
    classifier = ALGORITHM_FUNCTIONS[algorithm]
    prediction, certainty = classifier.classify(payload, custom_model_dir, processing_method, custom_options)

    return prediction, certainty


def learn(algorithm: ALGORITHM, learning_data: list[LearningData], target_model_path: str, custom_options: dict = None):
    """
    Starts the algorithm training process.

    :param algorithm: ALGORITHM enum value specifying the training algorithm.
    :param learning_data: List of LearningData instances used for training.
    :param target_model_path: Directory where the trained model will be saved.
    :param custom_options: Optional dictionary to override default training parameters.

        Example::
            custom_options = {
                "batch_size": 64,
                "epochs": 30
            }

    :return: Tuple (accuracy, loss) from the final evaluation.
    """
    os.makedirs(os.path.abspath(target_model_path), exist_ok=True)

    classifier = ALGORITHM_FUNCTIONS[algorithm]
    acc, loss = classifier.learn(learning_data, target_model_path, custom_options)

    return acc, loss
