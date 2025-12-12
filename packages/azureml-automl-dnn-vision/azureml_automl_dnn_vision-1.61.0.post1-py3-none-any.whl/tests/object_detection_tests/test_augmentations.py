# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Unit tests for augmentation for object detection."""
import random
from hashlib import new
import os
import pytest

import torch

from PIL import Image
from unittest.mock import patch
from azureml.automl.dnn.vision.object_detection.common.augmentations import transform, random_crop_around_bbox


@pytest.mark.usefixtures("new_clean_dir")
@pytest.mark.parametrize("is_train", [False, True])
@pytest.mark.parametrize("apply_automl_train_augmentations", [False, True])
def test_transform(is_train, apply_automl_train_augmentations):
    image_root = "object_detection_data/images"
    image = Image.open(os.path.join(image_root, "000001030.png")).convert("RGB")
    height, width = image.height, image.width
    image_area = width * height
    boxes = torch.Tensor([
        [int(0.25 * width), int(0.25 * height), int(0.5 * width), int(0.5 * height)],
        [int(0.5 * width), int(0.5 * height), int(0.75 * width), int(0.75 * height)],
    ])

    for _ in range(100):
        new_image, new_boxes, new_areas, new_height, new_width, _ = transform(
            image, boxes, is_train, apply_automl_train_augmentations, 0.5)

        assert new_image.shape[1] == new_height
        assert new_image.shape[2] == new_width
        assert (new_height >= 0.5 * image.height) and (new_height <= 2 * image.height)
        assert (new_width >= 0.5 * image.width) and (new_width <= 2 * image.width)

        assert (new_areas[0] >= 0.0625 * image_area) and (new_areas[0] <= 0.25 * image_area)
        assert (new_areas[1] >= 0.0625 * image_area) and (new_areas[1] <= 0.25 * image_area)
        assert len(new_boxes) == 2
        if apply_automl_train_augmentations is False:
            assert new_width == width
            assert new_height == height
            assert torch.all(boxes.eq(new_boxes))


@pytest.mark.usefixtures("new_clean_dir")
@pytest.mark.parametrize("apply_automl_train_augmentations", [True, False])
def test_transform_empty_boxes(apply_automl_train_augmentations):
    image_root = "object_detection_data/images"
    image = Image.open(os.path.join(image_root, "000001030.png")).convert("RGB")
    _, new_boxes, new_areas, _, _, _ = transform(image, torch.Tensor([]), False, apply_automl_train_augmentations, 0.5)

    assert len(new_boxes) == 0
    assert len(new_areas) == 0


@pytest.mark.usefixtures("new_clean_dir")
@patch("logging.Logger.warning")
def test_random_crop_around_bbox_invalid_boxes(mock_logger_warning):
    image_root = "object_detection_data/images"
    image = Image.open(os.path.join(image_root, "000001030.png")).convert("RGB")
    height, width = image.height, image.width

    # Out of bounds co-ordinates
    invalid_boxes = [
        [-1, 0, int(0.5 * width), int(0.5 * height)],
        [0, -1, int(0.5 * width), int(0.5 * height)],
        [0, 0, width + 1, int(0.5 * height)],
        [0, 0, int(0.5 * width), height + 1]
    ]
    for box in invalid_boxes:
        boxes = torch.Tensor([box])
        new_image, new_boxes, _ = random_crop_around_bbox(image, boxes)
        assert torch.equal(new_boxes, boxes)
        mock_logger_warning.assert_any_call(
            "Due to out of bounds bbox coordinates, no random_crop_around_bbox will be applied"
        )
        mock_logger_warning.reset_mock()


def _test_boxes_within_image(test_image, test_boxes):
    # Check if the boxes are within the image.
    test_image_width = test_image.width
    test_image_height = test_image.height

    boxes_within_bounds = (test_boxes[:, 0] >= 0) * (test_boxes[:, 2] <= test_image_width) * \
        (test_boxes[:, 1] >= 0) * (test_boxes[:, 3] <= test_image_height)
    assert torch.all(boxes_within_bounds)


@pytest.mark.usefixtures("new_clean_dir")
def test_random_crop_around_bbox_edge_boxes():
    image_root = "object_detection_data/images"
    image = Image.open(os.path.join(image_root, "000001030.png")).convert("RGB")
    height, width = image.height, image.width

    def mock_randint_side_effect(range_min, range_max):
        return int((range_min + range_max) / 2)

    # Scenario when cropped image shares the right & bottom edges with bounding box
    with patch("random.randint", side_effect=mock_randint_side_effect):
        boxes = torch.Tensor([
            [int(0.20 * width), int(0.20 * height), int(width), int(height)]
        ])
        new_image, new_boxes, _ = random_crop_around_bbox(image, boxes)
        _test_boxes_within_image(new_image, new_boxes)

    # Scenario when cropped image shares the left & top edges with bounding box
    with patch("random.randint", side_effect=mock_randint_side_effect):
        boxes = torch.Tensor([
            [0, 0, int(0.80 * width), int(0.80 * height)]
        ])
        new_image, new_boxes, _ = random_crop_around_bbox(image, boxes)
        _test_boxes_within_image(new_image, new_boxes)


@pytest.mark.usefixtures("new_clean_dir")
def test_random_crop_around_bbox():
    image_root = "object_detection_data/images"
    image = Image.open(os.path.join(image_root, "000001030.png")).convert("RGB")
    height, width = image.height, image.width

    # Generic scenarios
    boxes = torch.Tensor([
        [int(0.25 * width), int(0.25 * height), int(0.5 * width), int(0.5 * height)],
        [int(0.5 * width), int(0.5 * height), int(0.75 * width), int(0.75 * height)],
    ])
    for _ in range(100):
        new_image, new_boxes, _ = random_crop_around_bbox(image, boxes)
        _test_boxes_within_image(new_image, new_boxes)
