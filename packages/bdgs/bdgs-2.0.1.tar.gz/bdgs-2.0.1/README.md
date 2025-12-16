# BDGS library development setup

## Prerequisites

- Python 3.11
- PIP

## Development

### Installation

1. Create/activate virtual environment
2. Install required packages with `pip install -r requirements.txt`

### Create new algorithm

To create a new algorithm, use algorithm creation script: `./scripts/generate_algorithm.py`

### Validate algorithms

To validate algorithms use scripts located in `./validation` directory. Json files with validation results are located
in `./validation/results` directory

## Usage

### Import library

To use library in external project, use `pip install bdgs`.

### Sample use cases

To predict gesture on selected image, run the code below. You can select desired algorithm by using values
on `ALGORITHM` enum. Some algorithms require their own payload (e.g. hand coordinates or background image
without hand). You can import specific payload from `bdgs.algorithms.<alg>.<alg>_payload`.

```python
import cv2
from bdgs import classify
from bdgs.data.algorithm import ALGORITHM
from bdgs.models.image_payload import ImagePayload

image = cv2.imread("resources/image.jpg")
result = classify(algorithm=ALGORITHM.EID_SCHWENKER, payload=ImagePayload(image=image))

print(result)
```

To show image processed by the selected algorithm, run:

```python
import cv2
from bdgs import process_image
from bdgs.data.algorithm import ALGORITHM
from bdgs.models.image_payload import ImagePayload

image = cv2.imread("resources/image.jpg")
processed_image = process_image(algorithm=ALGORITHM.EID_SCHWENKER, payload=ImagePayload(image=image))

cv2.imshow("Image", processed_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
```

To learn your own algorithm's model (e.g. on other image base than ours), run:

```python
import cv2
from bdgs import learn
from bdgs.data.algorithm import ALGORITHM
from bdgs.data.gesture import GESTURE
from bdgs.models.learning_data import LearningData

image = cv2.imread("resources/image.jpg")
acc, loss = learn(algorithm=ALGORITHM.EID_SCHWENKER, target_model_path="models",
                  learning_data=[LearningData(image_path="resources/image.jpg", label=GESTURE.FIVE)] * 10)

print(acc, loss)
```
