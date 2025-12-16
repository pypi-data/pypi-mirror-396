import numpy as np

from bdgs.models.image_payload import ImagePayload


class ChangChenPayload(ImagePayload):
    def __init__(self, image: np.ndarray, coords: list[tuple[int, int]]):
        super().__init__(image)
        self.coords = coords
