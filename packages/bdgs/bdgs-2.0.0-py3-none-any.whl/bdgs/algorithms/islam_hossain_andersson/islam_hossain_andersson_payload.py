import numpy as np

from bdgs.models.image_payload import ImagePayload


class IslamHossainAnderssonPayload(ImagePayload):
    def __init__(self, image: np.ndarray, bg_image: np.ndarray,
                 coords: list[tuple[int, int]]):
        super().__init__(image)
        self.bg_image = bg_image
        self.coords = coords
