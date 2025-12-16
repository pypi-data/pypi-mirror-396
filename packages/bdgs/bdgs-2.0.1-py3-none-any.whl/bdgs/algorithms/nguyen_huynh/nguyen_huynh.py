import os
import pickle
from enum import Enum

import cv2
import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from bdgs.algorithms.bdgs_algorithm import BaseAlgorithm
from bdgs.algorithms.nguyen_huynh.nguyen_huynh_payload import NguyenHuynhPayload
from bdgs.common.crop_image import crop_image
from bdgs.common.set_options import set_options
from bdgs.data.gesture import GESTURE
from bdgs.data.processing_method import PROCESSING_METHOD
from definitions import ROOT_DIR


class NguyenHuynh(BaseAlgorithm):

    def process_image(self, payload: NguyenHuynhPayload,
                      processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT) -> np.ndarray:
        image = payload.image
        coords = payload.coords

        if coords is not None:
            image = crop_image(image=image, coords=coords)

        img = image
        if img.dtype != np.uint8:
            img = (np.clip(img, 0, 1) * 255).astype(np.uint8) if img.max() <= 1.0 else img.astype(np.uint8)

        ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCrCb)

        skin_mask = cv2.inRange(ycrcb, np.array((0, 135, 85), dtype=np.uint8),
                                np.array((255, 180, 135), dtype=np.uint8))

        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.morphologyEx(skin_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return np.zeros((img.shape[0], img.shape[1]), dtype=np.uint8)

        largest = max(contours, key=cv2.contourArea)
        mask = np.zeros_like(mask)
        cv2.drawContours(mask, [largest], -1, 255, thickness=cv2.FILLED)

        flood = mask.copy()
        h, w = flood.shape
        mask_flood = flood.copy()
        mask_temp = np.zeros((h + 2, w + 2), np.uint8)
        cv2.floodFill(mask_flood, mask_temp, (0, 0), 255)
        mask_flood_inv = cv2.bitwise_not(mask_flood)
        mask = mask | mask_flood_inv

        ys, xs = np.where(mask == 255)
        if len(ys) == 0:
            return np.zeros((h, w), dtype=np.uint8)

        top, bottom = np.min(ys), np.max(ys)
        left, right = np.min(xs), np.max(xs)

        bbox_height = bottom - top + 1
        lower_fraction = 0.4
        lower_start = int(bottom - bbox_height * lower_fraction)
        if lower_start <= top:
            lower_start = top

        widths = []
        rows = list(range(lower_start, bottom + 1))
        for y in rows:
            wcount = np.sum(mask[y, left:right + 1] == 255)
            widths.append(wcount)

        if len(widths) > 0:
            min_idx = int(np.argmin(widths))
            wrist_row = rows[min_idx]
            safety_pixels = max(5, int(0.03 * h))
            cut_line = wrist_row + safety_pixels
            if cut_line < bottom:
                mask[cut_line:bottom + 1, :] = 0

        kernel2 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel2, iterations=1)
        mask = cv2.medianBlur(mask, 5)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            largest = max(contours, key=cv2.contourArea)
            final = np.zeros_like(mask)
            cv2.drawContours(final, [largest], -1, 255, thickness=cv2.FILLED)
        else:
            final = np.zeros_like(mask)

        ys, xs = np.where(final == 255)
        if len(ys) > 0:
            top, bottom = np.min(ys), np.max(ys)
            left, right = np.min(xs), np.max(xs)

            hand_crop = final[top:bottom + 1, left:right + 1]

            h2, w2 = hand_crop.shape

            size = max(h2, w2)
            square = np.zeros((size, size), dtype=np.uint8)

            y_offset = (size - h2) // 2
            x_offset = (size - w2) // 2
            square[y_offset:y_offset + h2,
            x_offset:x_offset + w2] = hand_crop

            target_size = 128
            square = cv2.resize(square, (target_size, target_size),
                                interpolation=cv2.INTER_NEAREST)

            final = square

        return final

    def _extract_features(self, binary_img: np.ndarray) -> np.ndarray:
        h, w = binary_img.shape
        features = []

        binary = (binary_img > 0).astype(np.uint8)

        num_sections = 8
        y_positions = np.linspace(0, h - 1, num_sections, dtype=int)
        for y in y_positions:
            row = binary[y, :]
            transitions = np.count_nonzero(row[1:] != row[:-1])
            features.append(transitions)
        x_positions = np.linspace(0, w - 1, num_sections, dtype=int)
        for x in x_positions:
            col = binary[:, x]
            transitions = np.count_nonzero(col[1:] != col[:-1])
            features.append(transitions)

        def boundary_hist(direction):
            distances = []
            if direction == 'left':
                for y in range(h):
                    idx = np.argmax(binary[y, :] > 0)
                    distances.append(idx if binary[y, idx] > 0 else w)
            elif direction == 'right':
                for y in range(h):
                    idx = np.argmax(binary[y, ::-1] > 0)
                    distances.append(idx if binary[y, w - idx - 1] > 0 else w)
            elif direction == 'top':
                for x in range(w):
                    idx = np.argmax(binary[:, x] > 0)
                    distances.append(idx if binary[idx, x] > 0 else h)
            return np.array(distances, dtype=np.float32)

        left_hist = boundary_hist('left')
        right_hist = boundary_hist('right')
        top_hist = boundary_hist('top')

        def average_sections(hist, n_sections):
            hist = np.array(hist)
            seg_len = len(hist) // n_sections
            avgs = [np.mean(hist[i * seg_len:(i + 1) * seg_len]) for i in range(n_sections)]
            return avgs

        for hist in [left_hist, right_hist, top_hist]:
            features.extend(average_sections(hist, 10))

        ys, xs = np.where(binary == 1)
        if len(xs) == 0 or len(ys) == 0:
            width = height = 1
            area = 0
        else:
            left, right = np.min(xs), np.max(xs)
            top, bottom = np.min(ys), np.max(ys)
            width = right - left + 1
            height = bottom - top + 1
            area = np.sum(binary)

        edges_ratio = width / height if height != 0 else 1.0
        area_ratio = area / (width * height) if width * height != 0 else 0.0

        features.extend([edges_ratio, area_ratio])

        return np.array(features, dtype=np.float32)

    def learn(self, learning_data: list, target_model_path: str, custom_options: dict = None) -> (float, float):
        default_options = {
            "max_iter": 500
        }
        options = set_options(default_options, custom_options)

        X, y = [], []

        for data in learning_data:
            image = cv2.imread(data.image_path)
            if image is None:
                continue

            payload = NguyenHuynhPayload(image=image, coords=data.coords)
            processed = self.process_image(payload)
            features = self._extract_features(processed)

            X.append(features)
            y.append(data.label.value - 1)

        X, y = np.array(X), np.array(y)

        mlp = MLPClassifier(hidden_layer_sizes=(64,), activation='tanh',
                            solver='adam', max_iter=options["max_iter"], random_state=42)
        pipeline = make_pipeline(StandardScaler(), mlp)
        pipeline.fit(X, y)

        y_pred = pipeline.predict(X)
        accuracy = accuracy_score(y, y_pred)

        os.makedirs(target_model_path, exist_ok=True)
        model_path = os.path.join(target_model_path, "nguyen_huynh.pkl")
        with open(model_path, "wb") as f:
            pickle.dump(pipeline, f)

        return accuracy, None

    def classify(self, payload: NguyenHuynhPayload, custom_model_path=None,
                 processing_method: PROCESSING_METHOD = PROCESSING_METHOD.DEFAULT,
                 custom_options: dict = None) -> (Enum, int):
        default_options = {
            "gesture_enum": GESTURE
        }
        options = set_options(default_options, custom_options)
        gesture_enum = options['gesture_enum']
        model_path = os.path.join(custom_model_path or os.path.join(ROOT_DIR, "bdgs_trained_models"),
                                  "nguyen_huynh.pkl")

        with open(model_path, "rb") as f:
            model = pickle.load(f)

        processed_image = self.process_image(payload, processing_method)
        features = self._extract_features(processed_image).reshape(1, -1)

        prediction = model.predict(features)
        proba = model.predict_proba(features)
        confidence = round(100 * np.max(proba), 0)

        return gesture_enum(prediction[0] + 1), confidence
