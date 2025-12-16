import numpy as np

from bdgs.models.image_payload import ImagePayload


class MurthyJadonPayload(ImagePayload):
    def __init__(self, image: np.ndarray, bg_image: np.ndarray):
        super().__init__(image)
        self.bg_image = bg_image
