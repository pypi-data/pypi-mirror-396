import numpy as np


def crop_image(image: np.ndarray, coords: list[tuple[int, int]]) -> np.ndarray:
    (x1, y1), (x2, y2) = coords
    return image[y1:y2, x1:x2]
