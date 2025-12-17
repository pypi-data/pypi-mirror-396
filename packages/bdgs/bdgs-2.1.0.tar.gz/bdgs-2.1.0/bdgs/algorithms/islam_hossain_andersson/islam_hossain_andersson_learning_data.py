from enum import Enum

from bdgs.models.learning_data import LearningData


class IslamHossainAnderssonLearningData(LearningData):
    def __init__(self, image_path: str, bg_image_path: str, coords: list[tuple[int, int]], label: Enum):
        super().__init__(image_path, label)
        self.bg_image_path = bg_image_path
        self.coords = coords
