from enum import Enum

from bdgs.models.learning_data import LearningData


class MurthyJadonLearningData(LearningData):
    def __init__(self, image_path: str, bg_image_path: str, label: Enum):
        super().__init__(image_path, label)
        self.bg_image_path = bg_image_path
