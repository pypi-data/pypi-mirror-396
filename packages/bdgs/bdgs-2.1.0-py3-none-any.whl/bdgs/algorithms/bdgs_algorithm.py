from abc import abstractmethod, ABC
from enum import Enum

from numpy import ndarray

from bdgs.data.processing_method import PROCESSING_METHOD
from bdgs.models.image_payload import ImagePayload
from bdgs.models.learning_data import LearningData


class BaseAlgorithm(ABC):
    @staticmethod
    @abstractmethod
    def process_image(payload: ImagePayload,
                      processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT) -> ndarray:
        """Process image"""
        raise NotImplementedError("Method process_image not implemented")

    @abstractmethod
    def classify(self, payload: ImagePayload, custom_model_dir=None,
                 processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT,
                 custom_options: dict = None) -> Enum:
        """Classify gesture based on static image"""
        raise NotImplementedError("Method classify not implemented")

    @abstractmethod
    def learn(self, learning_data: list[LearningData], target_model_path: str, custom_options: dict = None) -> (float,
                                                                                                                float):
        """Learn from static images"""
        raise NotImplementedError("Method learn not implemented")
