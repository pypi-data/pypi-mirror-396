from enum import Enum

from bdgs.models.learning_data import LearningData


class MohantyRambhatlaLearningData(LearningData):
    def __init__(self, image_path: str, label: Enum, coords: list[tuple[int, int]]):
        super().__init__(image_path, label)
        self.coords = coords
