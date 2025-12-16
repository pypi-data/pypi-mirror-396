import numpy as np

from bdgs.models.image_payload import ImagePayload


class GuptaJaafarPayload(ImagePayload):
    def __init__(self, image: np.ndarray, coords: list[tuple[int, int]]):
        super().__init__(image)
        self.coords = coords
