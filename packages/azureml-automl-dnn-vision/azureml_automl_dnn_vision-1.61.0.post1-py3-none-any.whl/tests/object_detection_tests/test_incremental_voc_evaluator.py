import numpy as np
import pickle
import pytest

from pytest import approx

from azureml.automl.dnn.vision.common.constants import MetricsLiterals
from azureml.automl.dnn.vision.object_detection.common import masktools
from azureml.automl.dnn.vision.object_detection.eval.incremental_voc_evaluator import IncrementalVocEvaluator


PRECISION, RECALL = MetricsLiterals.PRECISION, MetricsLiterals.RECALL
AVERAGE_PRECISION, MEAN_AVERAGE_PRECISION = MetricsLiterals.AVERAGE_PRECISION, MetricsLiterals.MEAN_AVERAGE_PRECISION
PER_LABEL_METRICS = MetricsLiterals.PER_LABEL_METRICS
IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS = MetricsLiterals.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS
CONFUSION_MATRICES_PER_SCORE_THRESHOLD = MetricsLiterals.CONFUSION_MATRICES_PER_SCORE_THRESHOLD
PRECISIONS_PER_SCORE_THRESHOLD = MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD
RECALLS_PER_SCORE_THRESHOLD = MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD


def _check_metrics_keys(metrics, task_is_detection=True):
    expected_metrics_keys = {
        MEAN_AVERAGE_PRECISION, PRECISION, RECALL, PRECISIONS_PER_SCORE_THRESHOLD, RECALLS_PER_SCORE_THRESHOLD,
        PER_LABEL_METRICS, IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS, CONFUSION_MATRICES_PER_SCORE_THRESHOLD
    } if task_is_detection else {
        MEAN_AVERAGE_PRECISION, PRECISION, RECALL, PRECISIONS_PER_SCORE_THRESHOLD, RECALLS_PER_SCORE_THRESHOLD,
        PER_LABEL_METRICS
    }

    assert set(metrics.keys()) == expected_metrics_keys


def _check_valid_metric_value(metric_value):
    assert (metric_value == -1.0) or ((metric_value >= 0.0) and (metric_value <= 1.0))


def _make_random_objects(width, height, num_classes, num_boxes, is_ground_truth):
    xs = np.random.randint(0, width, size=(num_boxes, 2))
    ys = np.random.randint(0, height, size=(num_boxes, 2))
    boxes = np.concatenate(
        (
            np.amin(xs, axis=1, keepdims=True), np.amin(ys, axis=1, keepdims=True),
            np.amax(xs, axis=1, keepdims=True), np.amax(ys, axis=1, keepdims=True),
        ),
        axis=1
    )

    classes = np.random.randint(num_classes, size=(len(boxes),))
    if is_ground_truth:
        return {"boxes": boxes, "masks": None, "classes": classes, "scores": None}

    scores = np.random.uniform(size=(len(boxes),))
    return {"boxes": boxes, "masks": None, "classes": classes, "scores": scores}


def _xyxy2xywh(box):
    return [
        float(box[0]), float(box[1]), float(box[2]) - float(box[0]), float(box[3]) - float(box[1])
    ]


def _image_level_base(metrics):
    return {
        k: v for k, v in metrics[IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS].items()
        if k in {AVERAGE_PRECISION, PRECISION, RECALL}
    }


class TestIncrementalVocEvaluator:
    @staticmethod
    def _rle_mask_from_bbox(bbox, height, width):
        x1, y1, x2, y2 = bbox
        polygon = [[x1, y1, x2, y1, x2, y2, x1, y2, x1, y1]]
        rle_masks = masktools.convert_polygon_to_rle_masks(polygon, height, width)
        return rle_masks[0]

    @staticmethod
    def _create_annotation(image_id, bbox, label, iscrowd):
        result = {
            "image_id": image_id, "bbox": _xyxy2xywh(bbox), "category_id": label, "iscrowd": iscrowd
        }
        return result

    @staticmethod
    def _create_prediction(image_id, bbox, label, score):
        result = {
            "image_id": image_id, "bbox": _xyxy2xywh(bbox), "category_id": label, "score": score
        }
        return result

    def test_single_image_no_gt_no_pred(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([], dtype=bool)}]
        gt_objects_per_image = [
            {"boxes": np.zeros((0, 4)), "masks": None, "classes": np.zeros((0,)), "scores": None}
        ]
        predicted_objects_per_image = [
            {"boxes": np.zeros((0, 4)), "masks": None, "classes": np.zeros((0,)), "scores": np.zeros((0,))}
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            1: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == -1.0
        assert metrics[PRECISION] == -1.0
        assert metrics[RECALL] == -1.0
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == undefined_for_all_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == undefined_for_all_st

    def test_single_image_no_gt_one_pred(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([], dtype=bool)}]
        gt_objects_per_image = [
            {"boxes": np.zeros((0, 4)), "masks": None, "classes": np.zeros((0,)), "scores": None}
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        zero_for_all_st = {st / 100.0: 0.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            1: {
                AVERAGE_PRECISION: -1.0, PRECISION: 0.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: zero_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == -1.0
        assert metrics[PRECISION] == 0.0
        assert metrics[RECALL] == -1.0
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == zero_for_all_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == undefined_for_all_st

    def test_single_image_one_gt_no_pred1(self):
        # no predictions specified with empty prediction objects dictionary

        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [{}]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        zero_for_all_st = {st / 100.0: 0.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            1: {
                AVERAGE_PRECISION: 0.0, PRECISION: -1.0, RECALL: 0.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: zero_for_all_st
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == 0.0
        assert metrics[PRECISION] == -1.0
        assert metrics[RECALL] == 0.0
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == undefined_for_all_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == zero_for_all_st

    def test_single_image_one_gt_no_pred2(self):
        # no predictions specified with prediction objects with empty boxes

        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.zeros((0, 4)), "masks": None,
                "classes": np.zeros((0,)), "scores": np.zeros((0,))
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        zero_for_all_st = {st / 100.0: 0.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            1: {
                AVERAGE_PRECISION: 0.0, PRECISION: -1.0, RECALL: 0.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: zero_for_all_st
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == 0.0
        assert metrics[PRECISION] == -1.0
        assert metrics[RECALL] == 0.0
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == undefined_for_all_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == zero_for_all_st

    def test_single_image_one_gt_one_pred_perfect_overlap(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        precision_per_st = {st / 100.0: approx(1.0) if st <= 75 else -1.0 for st in range(100)}
        recall_per_st = {st / 100.0: approx(1.0) if st <= 75 else 0.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            1: {
                AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0),
                PRECISIONS_PER_SCORE_THRESHOLD: precision_per_st, RECALLS_PER_SCORE_THRESHOLD: recall_per_st
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == precision_per_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == recall_per_st

    def test_single_image_one_gt_one_pred_crowd(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([True])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        zero_for_all_st = {st / 100.0: 0.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            1: {
                AVERAGE_PRECISION: -1.0, PRECISION: 0.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: zero_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == -1.0
        assert metrics[PRECISION] == 0.0
        assert metrics[RECALL] == -1.0
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == zero_for_all_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == undefined_for_all_st

    def test_single_image_one_gt_one_pred_different_class(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([2]), "scores": np.array([1.0])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        zero_for_all_st = {st / 100.0: 0.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            1: {
                AVERAGE_PRECISION: 0.0, PRECISION: -1.0, RECALL: 0.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: zero_for_all_st
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: 0.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: zero_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == 0.0
        assert metrics[PRECISION] == 0.0
        assert metrics[RECALL] == 0.0
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == zero_for_all_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == zero_for_all_st

    def test_single_image_one_gt_one_pred_insufficient_overlap(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 240, 180]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        zero_for_all_st = {st / 100.0: 0.0 for st in range(100)}
        precision_per_st = {st / 100.0: 0.0 if st <= 75 else -1.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            1: {
                AVERAGE_PRECISION: 0.0, PRECISION: 0.0, RECALL: 0.0,
                PRECISIONS_PER_SCORE_THRESHOLD: precision_per_st, RECALLS_PER_SCORE_THRESHOLD: zero_for_all_st
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == 0.0
        assert metrics[PRECISION] == 0.0
        assert metrics[RECALL] == 0.0
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == precision_per_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == zero_for_all_st

    def test_single_image_one_gt_one_pred_sufficient_overlap(self):
        # Like insufficient above, but with lower IOU threshold that makes the overlap sufficient.
        ive = IncrementalVocEvaluator(True, 3, 0.25)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 240, 180]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        precision_per_st = {st / 100.0: approx(1.0) if st <= 75 else -1.0 for st in range(100)}
        recall_per_st = {st / 100.0: approx(1.0) if st <= 75 else 0.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            1: {
                AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0),
                PRECISIONS_PER_SCORE_THRESHOLD: precision_per_st, RECALLS_PER_SCORE_THRESHOLD: recall_per_st
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == precision_per_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == recall_per_st

    def test_single_image_one_gt_one_pred_masks_small_overlap(self):
        ive = IncrementalVocEvaluator(False, 3, 0.1)

        # Two polygons roughly along the diagonals of a square.
        p1 = [0, 0, 35, 0, 200, 165, 200, 200, 165, 200, 0, 35, 0, 0]
        p2 = [200, 0, 165, 0, 0, 165, 0, 200, 35, 200, 200, 35, 200, 0]
        m1 = masktools.convert_polygon_to_rle_masks([p1], 480, 640)[0]
        m2 = masktools.convert_polygon_to_rle_masks([p2], 480, 640)[0]

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": None, "masks": [m1], "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": None, "masks": [m2], "classes": np.array([1]), "scores": np.array([0.5])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics, task_is_detection=False)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        precision_per_st = {st / 100.0: approx(1.0) if st <= 50 else -1.0 for st in range(100)}
        recall_per_st = {st / 100.0: approx(1.0) if st <= 50 else 0.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            1: {
                AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0),
                PRECISIONS_PER_SCORE_THRESHOLD: precision_per_st, RECALLS_PER_SCORE_THRESHOLD: recall_per_st
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == precision_per_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == recall_per_st

    def test_single_image_one_gt_one_pred_masks_zero_overlap(self):
        ive = IncrementalVocEvaluator(False, 3, 0.1)

        # Two completely disjoint polygons, each consisting of two squares placed on a diagonal.
        # p1 p2
        # p2 p1
        p1 = [
            100, 100, 200, 100, 200, 200, 100, 200,
            100, 100, 100, 0, 0, 0, 0, 100, 100, 100
        ]
        p2 = [
            100, 100, 200, 100, 200, 0, 100, 0,
            100, 100, 100, 200, 0, 200, 0, 100, 100, 100
        ]
        m1 = masktools.convert_polygon_to_rle_masks([p1], 480, 640)[0]
        m2 = masktools.convert_polygon_to_rle_masks([p2], 480, 640)[0]

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": None, "masks": [m1], "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": None, "masks": [m2], "classes": np.array([1]), "scores": np.array([0.5])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics, task_is_detection=False)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        zero_for_all_st = {st / 100.0: 0.0 for st in range(100)}
        precision_per_st = {st / 100.0: 0.0 if st <= 50 else -1.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            1: {
                AVERAGE_PRECISION: 0.0, PRECISION: 0.0, RECALL: 0.0,
                PRECISIONS_PER_SCORE_THRESHOLD: precision_per_st, RECALLS_PER_SCORE_THRESHOLD: zero_for_all_st
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.0)
        assert metrics[PRECISION] == approx(0.0)
        assert metrics[RECALL] == approx(0.0)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == precision_per_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == zero_for_all_st

    def test_single_image_one_gt_one_pred_not_clipped(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 300, "height": 300, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[200, 200, 300, 300]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[200, 200, 400, 400]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        zero_for_all_st = {st / 100.0: 0.0 for st in range(100)}
        precision_per_st = {st / 100.0: 0.0 if st <= 75 else -1.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            1: {
                AVERAGE_PRECISION: 0.0, PRECISION: 0.0, RECALL: 0.0,
                PRECISIONS_PER_SCORE_THRESHOLD: precision_per_st, RECALLS_PER_SCORE_THRESHOLD: zero_for_all_st
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == 0.0
        assert metrics[PRECISION] == 0.0
        assert metrics[RECALL] == 0.0
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == precision_per_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == zero_for_all_st

    def test_single_image_one_gt_one_pred_degenerate(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[1, 1, 2, 2]]), "masks": None,
                "classes": np.array([2]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[0, 0, 0, 0]]), "masks": None,
                "classes": np.array([2]), "scores": np.array([0.5])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        zero_for_all_st = {st / 100.0: 0.0 for st in range(100)}
        precision_per_st = {st / 100.0: 0.0 if st <= 50 else -1.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            1: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            2: {
                AVERAGE_PRECISION: 0.0, PRECISION: 0.0, RECALL: 0.0,
                PRECISIONS_PER_SCORE_THRESHOLD: precision_per_st, RECALLS_PER_SCORE_THRESHOLD: zero_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == 0.0
        assert metrics[PRECISION] == 0.0
        assert metrics[RECALL] == 0.0
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == precision_per_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == zero_for_all_st

    def test_single_image_two_gt_two_pred_good_overlap(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False, False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [160, 120, 320, 240],
                    [320, 240, 480, 360],
                ]),
                "masks": None,
                "classes": np.array([0, 0]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([
                    [160, 120, 300, 220],
                    [320, 240, 460, 340],
                ]),
                "masks": None,
                "classes": np.array([0, 0]),
                "scores": np.array([0.999, 0.888])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        precision_per_st = {st / 100.0: approx(1.0) for st in range(100)}
        recall_per_st = {st / 100.0: approx(1.0) if st <= 88 else approx(0.5) for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0),
                PRECISIONS_PER_SCORE_THRESHOLD: precision_per_st, RECALLS_PER_SCORE_THRESHOLD: recall_per_st
            },
            1: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == precision_per_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == recall_per_st

    def test_single_image_two_gt_two_pred_good_overlap_different_class(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False, False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [160, 120, 320, 240],
                    [320, 240, 480, 360],
                ]),
                "masks": None,
                "classes": np.array([0, 0]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([
                    [160, 120, 300, 220],
                    [320, 240, 460, 340],
                ]),
                "masks": None,
                "classes": np.array([0, 1]),
                "scores": np.array([0.999, 0.888])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        zero_for_all_st = {st / 100.0: 0.0 for st in range(100)}
        p1 = {st / 100.0: approx(1.0) for st in range(100)}
        p2 = {st / 100.0: approx(0.5) if st <= 88 else approx(1.0) for st in range(100)}
        recall_per_st = {st / 100.0: approx(0.5) for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: approx(0.5), PRECISION: approx(1.0), RECALL: approx(0.5),
                PRECISIONS_PER_SCORE_THRESHOLD: p1, RECALLS_PER_SCORE_THRESHOLD: recall_per_st
            },
            1: {
                AVERAGE_PRECISION: -1.0, PRECISION: 0.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: zero_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.5)
        assert metrics[PRECISION] == approx(0.5)
        assert metrics[RECALL] == approx(0.5)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == p2
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == recall_per_st

    def test_single_image_two_gt_two_pred_one_match(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False, False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200],
                    [150, 100, 250, 200],
                ]),
                "masks": None,
                "classes": np.array([2, 2]),
                "scores": None
            }
        ]
        pred_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200],
                    [135, 100, 210, 200],
                ]),
                "masks": None,
                "classes": np.array([2, 2]),
                "scores": np.array([0.75, 0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, pred_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        precision_per_st = {st / 100.0: approx(0.5) if st <= 75 else -1.0 for st in range(100)}
        recall_per_st = {st / 100.0: approx(0.5) if st <= 75 else 0.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            1: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            2: {
                AVERAGE_PRECISION: approx(0.5), PRECISION: approx(0.5), RECALL: approx(0.5),
                PRECISIONS_PER_SCORE_THRESHOLD: precision_per_st, RECALLS_PER_SCORE_THRESHOLD: recall_per_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.5)
        assert metrics[PRECISION] == approx(0.5)
        assert metrics[RECALL] == approx(0.5)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == precision_per_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == recall_per_st

    def test_single_image_two_gt_two_pred_one_match_masks(self):
        ive = IncrementalVocEvaluator(False, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False, False])}]
        gt_objects_per_image = [
            {
                "boxes": None,
                "masks": [
                    self._rle_mask_from_bbox([100, 100, 200, 200], 480, 640),
                    self._rle_mask_from_bbox([150, 100, 250, 200], 480, 640),
                ],
                "classes": np.array([2, 2]),
                "scores": None
            }
        ]
        pred_objects_per_image = [
            {
                "boxes": None,
                "masks": [
                    self._rle_mask_from_bbox([100, 100, 200, 200], 480, 640),
                    self._rle_mask_from_bbox([135, 100, 210, 200], 480, 640),
                ],
                "classes": np.array([2, 2]),
                "scores": np.array([0.75, 0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, pred_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics, task_is_detection=False)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        precision_per_st = {st / 100.0: approx(0.5) if st <= 75 else -1.0 for st in range(100)}
        recall_per_st = {st / 100.0: approx(0.5) if st <= 75 else 0.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            1: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            2: {
                AVERAGE_PRECISION: approx(0.5), PRECISION: approx(0.5), RECALL: approx(0.5),
                PRECISIONS_PER_SCORE_THRESHOLD: precision_per_st, RECALLS_PER_SCORE_THRESHOLD: recall_per_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.5)
        assert metrics[PRECISION] == approx(0.5)
        assert metrics[RECALL] == approx(0.5)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == precision_per_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == recall_per_st

    def test_single_image_1K_gt_1K_pred_random(self):
        ive = IncrementalVocEvaluator(True, 10, 0.5)

        meta_info_per_image = [{"width": 1600, "height": 1600, "iscrowd": np.array([False] * 1000)}]

        xs, ys = np.random.randint(0, 1600, size=(1000, 2)), np.random.randint(0, 1600, size=(1000, 2))
        x1, x2 = np.amin(xs, axis=1, keepdims=True), np.amax(xs, axis=1, keepdims=True)
        y1, y2 = np.amin(ys, axis=1, keepdims=True), np.amax(ys, axis=1, keepdims=True)
        boxes = np.concatenate((x1, y1, x2, y2), axis=1)
        classes = np.random.randint(0, 10, size=(1000,))
        gt_objects_per_image = [{"boxes": boxes, "masks": None, "classes": classes, "scores": None}]

        xs, ys = np.random.randint(0, 1600, size=(1000, 2)), np.random.randint(0, 1600, size=(1000, 2))
        x1, x2 = np.amin(xs, axis=1, keepdims=True), np.amax(xs, axis=1, keepdims=True)
        y1, y2 = np.amin(ys, axis=1, keepdims=True), np.amax(ys, axis=1, keepdims=True)
        boxes = np.concatenate((x1, y1, x2, y2), axis=1)
        classes = np.random.randint(0, 10, size=(1000,))
        scores = np.random.uniform(size=(1000,))
        pred_objects_per_image = [{"boxes": boxes, "masks": None, "classes": classes, "scores": scores}]

        ive.evaluate_batch(gt_objects_per_image, pred_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        for i in range(10):
            assert i in metrics[PER_LABEL_METRICS]
            m = metrics[PER_LABEL_METRICS][i]

            _check_valid_metric_value(m[AVERAGE_PRECISION])
            _check_valid_metric_value(m[PRECISION])
            _check_valid_metric_value(m[RECALL])
            for precision_per_st in m[PRECISIONS_PER_SCORE_THRESHOLD].values():
                _check_valid_metric_value(precision_per_st)
            for recall_per_st in m[RECALLS_PER_SCORE_THRESHOLD].values():
                _check_valid_metric_value(recall_per_st)

        _check_valid_metric_value(metrics[MEAN_AVERAGE_PRECISION])
        _check_valid_metric_value(metrics[PRECISION])
        _check_valid_metric_value(metrics[RECALL])
        for precision_per_st in metrics[PRECISIONS_PER_SCORE_THRESHOLD].values():
            _check_valid_metric_value(precision_per_st)
        for recall_per_st in metrics[RECALLS_PER_SCORE_THRESHOLD].values():
            _check_valid_metric_value(recall_per_st)

    def test_multi_image_one_gt_one_pred_good_overlap(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [
            {"width": 640, "height": 480, "iscrowd": np.array([False])},
            {"width": 1280, "height": 960, "iscrowd": np.array([False])}
        ]
        gt_objects_per_image = [
            # first image
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([0]), "scores": None
            },
            # second image
            {
                "boxes": np.array([[320, 240, 640, 480]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            # first image
            {
                "boxes": np.array([
                    [160, 120, 300, 220],
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": np.array([0.991])
            },
            # second image
            {
                "boxes": np.array([
                    [320, 240, 600, 440],
                ]),
                "masks": None,
                "classes": np.array([1]),
                "scores": np.array([0.995])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        o = {st / 100.0: approx(1.0) for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0),
                PRECISIONS_PER_SCORE_THRESHOLD: o, RECALLS_PER_SCORE_THRESHOLD: o
            },
            1: {
                AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0),
                PRECISIONS_PER_SCORE_THRESHOLD: o, RECALLS_PER_SCORE_THRESHOLD: o
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == o
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == o

    def test_multi_image_one_gt_one_pred_different_class(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [
            {"width": 640, "height": 480, "iscrowd": np.array([False])},
            {"width": 1280, "height": 960, "iscrowd": np.array([False])}
        ]
        gt_objects_per_image = [
            # first image
            {
                "boxes": np.array([
                    [160, 120, 320, 240],
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": None
            },
            # second image
            {
                "boxes": np.array([
                    [320, 240, 640, 480],
                ]),
                "masks": None,
                "classes": np.array([1]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            # first image
            {
                "boxes": np.array([
                    [160, 120, 300, 220],
                ]),
                "masks": None,
                "classes": np.array([1]),
                "scores": np.array([0.991])
            },
            # second image
            {
                "boxes": np.array([
                    [320, 240, 600, 440],
                ]),
                "masks": None,
                "classes": np.array([2]),
                "scores": np.array([0.995])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        zero_for_all_st = {st / 100.0: 0.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: 0.0, PRECISION: -1.0, RECALL: 0.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: zero_for_all_st
            },
            1: {
                AVERAGE_PRECISION: 0.0, PRECISION: 0.0, RECALL: 0.0,
                PRECISIONS_PER_SCORE_THRESHOLD: zero_for_all_st, RECALLS_PER_SCORE_THRESHOLD: zero_for_all_st
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: 0.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: zero_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == 0.0
        assert metrics[PRECISION] == 0.0
        assert metrics[RECALL] == 0.0
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == zero_for_all_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == zero_for_all_st

    def test_multi_image_two_gt_two_pred_perfect_match(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [
            {"width": 400, "height": 500, "iscrowd": np.array([False, False])},
            {"width": 200, "height": 300, "iscrowd": np.array([False, False])}
        ]
        gt_objects_per_image = [
            # first image
            {
                "boxes": np.array([
                    [100, 0, 200, 100],
                    [200, 0, 300, 100],
                ]),
                "masks": None,
                "classes": np.array([0, 1]),
                "scores": None
            },
            # second image
            {
                "boxes": np.array([
                    [10, 0, 20, 10],
                    [20, 0, 30, 10],
                ]),
                "masks": None,
                "classes": np.array([2, 1]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            # first image
            {
                "boxes": np.array([
                    [100, 0, 200, 100],
                    [200, 0, 300, 100],
                ]),
                "masks": None,
                "classes": np.array([0, 1]),
                "scores": np.array([0.8, 0.9])
            },
            # second image
            {
                "boxes": np.array([
                    [20, 0, 30, 10],
                    [10, 0, 20, 10],
                ]),
                "masks": None,
                "classes": np.array([1, 2]),
                "scores": np.array([0.9, 0.7])
            },
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        p0 = {st / 100.0: approx(1.0) if st <= 80 else -1.0 for st in range(100)}
        r0 = {st / 100.0: approx(1.0) if st <= 80 else 0.0 for st in range(100)}
        p1 = {st / 100.0: approx(1.0) if st <= 90 else -1.0 for st in range(100)}
        r1 = {st / 100.0: approx(1.0) if st <= 90 else 0.0 for st in range(100)}
        p2 = {st / 100.0: approx(1.0) if st <= 70 else -1.0 for st in range(100)}
        r2 = {st / 100.0: approx(1.0) if st <= 70 else 0.0 for st in range(100)}
        precision_per_st = {st / 100.0: approx(1.0) if st <= 90 else -1.0 for st in range(100)}
        recall_per_st = {
            st / 100.0:
                approx(1.0) if st <= 70
                else approx(0.75) if st <= 80
                else approx(0.5) if st <= 90
                else 0.0
            for st in range(100)
        }
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0),
                PRECISIONS_PER_SCORE_THRESHOLD: p0, RECALLS_PER_SCORE_THRESHOLD: r0
            },
            1: {
                AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0),
                PRECISIONS_PER_SCORE_THRESHOLD: p1, RECALLS_PER_SCORE_THRESHOLD: r1
            },
            2: {
                AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0),
                PRECISIONS_PER_SCORE_THRESHOLD: p2, RECALLS_PER_SCORE_THRESHOLD: r2
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == precision_per_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == recall_per_st

    def test_multi_image_three_gt_three_pred_single_match(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [
            {"width": 640, "height": 640, "iscrowd": np.array([False, False, False])},
            {"width": 6400, "height": 6400, "iscrowd": np.array([False, False, False])},
            {"width": 64000, "height": 64000, "iscrowd": np.array([False, False, False])},
        ]
        gt_objects_per_image = [
            # first image
            {
                "boxes": np.array([
                    [1, 0, 2, 100],
                    [2, 0, 3, 100],
                    [3, 0, 4, 100],
                ]),
                "masks": None,
                "classes": np.array([0, 1, 2]),
                "scores": None
            },
            # second image
            {
                "boxes": np.array([
                    [10, 0, 20, 100],
                    [20, 0, 30, 100],
                    [30, 0, 40, 100],
                ]),
                "masks": None,
                "classes": np.array([0, 1, 2]),
                "scores": None
            },
            # third image
            {
                "boxes": np.array([
                    [100, 0, 200, 100],
                    [200, 0, 300, 100],
                    [300, 0, 400, 100],
                ]),
                "masks": None,
                "classes": np.array([0, 1, 2]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            # first image
            {
                "boxes": np.array([
                    [1, 0, 2, 100],
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": np.array([0.5])
            },
            # second image
            {
                "boxes": np.array([
                    [20, 0, 30, 100],
                ]),
                "masks": None,
                "classes": np.array([1]),
                "scores": np.array([0.5])
            },
            # third image
            {
                "boxes": np.array([
                    [300, 0, 400, 100],
                ]),
                "masks": None,
                "classes": np.array([2]),
                "scores": np.array([0.5])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        _13 = 1.0 / 3.0
        precision_per_st = {st / 100.0: approx(1.0) if st <= 50 else -1.0 for st in range(100)}
        recall_per_st = {st / 100.0: approx(_13) if st <= 50 else 0.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: approx(_13), PRECISION: approx(1.0), RECALL: approx(_13),
                PRECISIONS_PER_SCORE_THRESHOLD: precision_per_st, RECALLS_PER_SCORE_THRESHOLD: recall_per_st
            },
            1: {
                AVERAGE_PRECISION: approx(_13), PRECISION: approx(1.0), RECALL: approx(_13),
                PRECISIONS_PER_SCORE_THRESHOLD: precision_per_st, RECALLS_PER_SCORE_THRESHOLD: recall_per_st
            },
            2: {
                AVERAGE_PRECISION: approx(_13), PRECISION: approx(1.0), RECALL: approx(_13),
                PRECISIONS_PER_SCORE_THRESHOLD: precision_per_st, RECALLS_PER_SCORE_THRESHOLD: recall_per_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(_13)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(_13)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == precision_per_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == recall_per_st

    def test_multi_image_three_gt_three_pred_single_match_masks(self):
        ive = IncrementalVocEvaluator(False, 3, 0.5)

        meta_info_per_image = [
            {"width": 640, "height": 640, "iscrowd": np.array([False, False, False])},
            {"width": 6400, "height": 6400, "iscrowd": np.array([False, False, False])},
            {"width": 64000, "height": 64000, "iscrowd": np.array([False, False, False])},
        ]
        gt_objects_per_image = [
            # first image
            {
                "boxes": None,
                "masks": [
                    self._rle_mask_from_bbox([1, 0, 2, 100], 640, 640),
                    self._rle_mask_from_bbox([2, 0, 3, 100], 640, 640),
                    self._rle_mask_from_bbox([3, 0, 4, 100], 640, 640),
                ],
                "classes": np.array([0, 1, 2]),
                "scores": None
            },
            # second image
            {
                "boxes": None,
                "masks": [
                    self._rle_mask_from_bbox([10, 0, 20, 100], 6400, 6400),
                    self._rle_mask_from_bbox([20, 0, 30, 100], 6400, 6400),
                    self._rle_mask_from_bbox([30, 0, 40, 100], 6400, 6400),
                ],
                "classes": np.array([0, 1, 2]),
                "scores": None
            },
            # third image
            {
                "boxes": None,
                "masks": [
                    self._rle_mask_from_bbox([100, 0, 200, 100], 64000, 64000),
                    self._rle_mask_from_bbox([200, 0, 300, 100], 64000, 64000),
                    self._rle_mask_from_bbox([300, 0, 400, 100], 64000, 64000),
                ],
                "classes": np.array([0, 1, 2]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            # first image
            {
                "boxes": None,
                "masks": [
                    self._rle_mask_from_bbox([1, 0, 2, 100], 640, 640),
                ],
                "classes": np.array([0]),
                "scores": np.array([0.5])
            },
            # second image
            {
                "boxes": None,
                "masks": [
                    self._rle_mask_from_bbox([20, 0, 30, 100], 6400, 6400),
                ],
                "classes": np.array([1]),
                "scores": np.array([0.5])
            },
            # third image
            {
                "boxes": None,
                "masks": [
                    self._rle_mask_from_bbox([300, 0, 400, 100], 64000, 64000),
                ],
                "classes": np.array([2]),
                "scores": np.array([0.5])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics, task_is_detection=False)

        _13 = 1.0 / 3.0
        precision_per_st = {st / 100.0: approx(1.0) if st <= 50 else -1.0 for st in range(100)}
        recall_per_st = {st / 100.0: approx(_13) if st <= 50 else 0.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: approx(_13), PRECISION: approx(1.0), RECALL: approx(_13),
                PRECISIONS_PER_SCORE_THRESHOLD: precision_per_st, RECALLS_PER_SCORE_THRESHOLD: recall_per_st
            },
            1: {
                AVERAGE_PRECISION: approx(_13), PRECISION: approx(1.0), RECALL: approx(_13),
                PRECISIONS_PER_SCORE_THRESHOLD: precision_per_st, RECALLS_PER_SCORE_THRESHOLD: recall_per_st
            },
            2: {
                AVERAGE_PRECISION: approx(_13), PRECISION: approx(1.0), RECALL: approx(_13),
                PRECISIONS_PER_SCORE_THRESHOLD: precision_per_st, RECALLS_PER_SCORE_THRESHOLD: recall_per_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(_13)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(_13)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == precision_per_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == recall_per_st

    @pytest.mark.parametrize("optimize_serialized_size", [False, True])
    def test_set_from_one_other(self, optimize_serialized_size):
        # First and only evaluator.
        ive1 = IncrementalVocEvaluator(True, 3, 0.5)
        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200],
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200]
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": np.array([0.5])
            }
        ]
        ive1.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        if optimize_serialized_size:
            ive1.optimize_serialized_size()

        # Combined evaluator.
        ive = IncrementalVocEvaluator(True, 3, 0.5)
        ive.set_from_others([ive1])
        metrics = ive.compute_metrics()

        # Check combined evaluator.
        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        precision_per_st = {st / 100.0: approx(1.0) if st <= 50 else -1.0 for st in range(100)}
        recall_per_st = {st / 100.0: approx(1.0) if st <= 50 else 0.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0),
                PRECISIONS_PER_SCORE_THRESHOLD: precision_per_st, RECALLS_PER_SCORE_THRESHOLD: recall_per_st
            },
            1: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == precision_per_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == recall_per_st

        assert _image_level_base(metrics) == {
            AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0)
        }

        cm1 = [[1, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
        cm2 = [[0, 0, 0, 1], [0, 0, 0, 0], [0, 0, 0, 0]]
        assert metrics[CONFUSION_MATRICES_PER_SCORE_THRESHOLD] == {
            st: cm1 if st <= 0.5 else cm2
            for st in np.arange(0, 10) / 10.0
        }

    @pytest.mark.parametrize("optimize_serialized_size", [False, True])
    def test_set_from_two_others(self, optimize_serialized_size):
        # First evaluator.
        ive1 = IncrementalVocEvaluator(True, 3, 0.5)
        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200],
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200]
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": np.array([0.5])
            }
        ]
        ive1.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        # Second evaluator. Note that the labels and predictions refer to different images in different evaluators.
        ive2 = IncrementalVocEvaluator(True, 3, 0.5)
        meta_info_per_image = [{"width": 512, "height": 384, "iscrowd": np.array([False, False, False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200],
                    [300, 300, 400, 400],
                    [400, 400, 450, 450],
                ]),
                "masks": None,
                "classes": np.array([0, 1, 2]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200],
                    [300, 300, 320, 320],
                    [300, 300, 380, 380],
                    [400, 400, 425, 425],
                ]),
                "masks": None,
                "classes": np.array([0, 1, 1, 2]),
                "scores": np.array([0.5, 0.25, 0.75, 1.0])
            }
        ]
        ive2.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        if optimize_serialized_size:
            ive1.optimize_serialized_size()
            ive2.optimize_serialized_size()

        # Combined evaluator.
        ive = IncrementalVocEvaluator(True, 3, 0.5)
        ive.set_from_others([ive1, ive2])
        metrics = ive.compute_metrics()

        # Check combined evaluator.
        _check_metrics_keys(metrics)

        p0 = {st / 100.0: approx(1.0) if st <= 50 else -1.0 for st in range(100)}
        r0 = {st / 100.0: approx(1.0) if st <= 50 else 0.0 for st in range(100)}
        p1 = {st / 100.0: approx(0.5) if st <= 25 else approx(1.0) if st <= 75 else -1.0 for st in range(100)}
        r1 = {st / 100.0: approx(1.0) if st <= 75 else 0.0 for st in range(100)}
        p2 = {st / 100.0: 0.0 for st in range(100)}
        r2 = {st / 100.0: 0.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0),
                PRECISIONS_PER_SCORE_THRESHOLD: p0, RECALLS_PER_SCORE_THRESHOLD: r0
            },
            1: {
                AVERAGE_PRECISION: approx(1.0), PRECISION: approx(0.5), RECALL: approx(1.0),
                PRECISIONS_PER_SCORE_THRESHOLD: p1, RECALLS_PER_SCORE_THRESHOLD: r1
            },
            2: {
                AVERAGE_PRECISION: approx(0.0), PRECISION: approx(0.0), RECALL: approx(0.0),
                PRECISIONS_PER_SCORE_THRESHOLD: p2, RECALLS_PER_SCORE_THRESHOLD: r2
            },
        }

        _23 = 2.0 / 3.0
        precision_per_st = {
            st / 100.0:
                approx(3.0 / 5.0) if st <= 25
                else approx(3.0 / 4.0) if st <= 50
                else approx(1.0 / 2.0) if st <= 75
                else 0.0 for st in range(100)
        }
        recall_per_st = {
            st / 100.0: approx(3.0 / 4.0) if st <= 50 else approx(1.0 / 4.0) if st <= 75 else 0.0 for st in range(100)
        }
        assert metrics[MEAN_AVERAGE_PRECISION] == approx(_23)
        assert metrics[PRECISION] == approx(0.5)
        assert metrics[RECALL] == approx(_23)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == precision_per_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == recall_per_st

        assert _image_level_base(metrics) == {
            AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0)
        }

        cm1 = [[2, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]]
        cm2 = [[0, 0, 0, 2], [0, 1, 0, 0], [0, 0, 0, 1]]
        cm3 = [[0, 0, 0, 2], [0, 0, 0, 1], [0, 0, 0, 1]]
        assert metrics[CONFUSION_MATRICES_PER_SCORE_THRESHOLD] == {
            st: cm1 if st <= 0.5 else cm2 if st <= 0.7 else cm3
            for st in np.arange(0, 10) / 10.0
        }

    @pytest.mark.parametrize("optimize_serialized_size", [False, True])
    def test_set_from_ten_others(self, optimize_serialized_size):
        # Ten evaluators.
        ives = [IncrementalVocEvaluator(True, 3, 0.5) for _ in range(10)]

        meta_info_per_image1 = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image1 = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200],
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": None
            }
        ]
        predicted_objects_per_image1 = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200]
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": np.array([0.5])
            }
        ]

        meta_info_per_image2 = [
            {"width": 640, "height": 480, "iscrowd": np.array([False])},
            {"width": 512, "height": 384, "iscrowd": np.array([False])}
        ]
        gt_objects_per_image2 = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200],
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": None
            },
            {
                "boxes": np.array([
                    [200, 200, 300, 300],
                ]),
                "masks": None,
                "classes": np.array([1]),
                "scores": None
            }
        ]
        predicted_objects_per_image2 = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200]
                ]),
                "masks": None,
                "classes": np.array([1]),
                "scores": np.array([0.5])
            },
            {
                "boxes": np.array([
                    [190, 190, 210, 210]
                ]),
                "masks": None,
                "classes": np.array([1]),
                "scores": np.array([0.5])
            }
        ]

        for i, ive in enumerate(ives):
            if i % 2 == 0:
                ive.evaluate_batch(gt_objects_per_image1, predicted_objects_per_image1, meta_info_per_image1)
            elif i % 2 == 1:
                ive.evaluate_batch(gt_objects_per_image2, predicted_objects_per_image2, meta_info_per_image2)

        if optimize_serialized_size:
            for ive in ives:
                ive.optimize_serialized_size()

        # Combined evaluator.
        ive = IncrementalVocEvaluator(True, 3, 0.5)
        ive.set_from_others(ives)
        metrics = ive.compute_metrics()

        # Check combined evaluator.
        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        p0 = {st / 100.0: approx(1.0) if st <= 50 else -1.0 for st in range(100)}
        r0 = {st / 100.0: approx(0.5) if st <= 50 else 0.0 for st in range(100)}
        p1 = {st / 100.0: 0.0 if st <= 50 else -1.0 for st in range(100)}
        r1 = {st / 100.0: 0.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: approx(0.5), PRECISION: approx(1.0), RECALL: approx(0.5),
                PRECISIONS_PER_SCORE_THRESHOLD: p0, RECALLS_PER_SCORE_THRESHOLD: r0
            },
            1: {
                AVERAGE_PRECISION: approx(0.0), PRECISION: approx(0.0), RECALL: approx(0.0),
                PRECISIONS_PER_SCORE_THRESHOLD: p1, RECALLS_PER_SCORE_THRESHOLD: r1
            },
            2: {
                AVERAGE_PRECISION: approx(-1.0), PRECISION: approx(-1.0), RECALL: approx(-1.0),
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            },
        }

        precision_per_st = {st / 100.0: approx(1.0 / 3.0) if st <= 50 else -1.0 for st in range(100)}
        recall_per_st = {st / 100.0: approx(1.0 / 3.0) if st <= 50 else 0.0 for st in range(100)}
        assert metrics[MEAN_AVERAGE_PRECISION] == approx(0.25)
        assert metrics[PRECISION] == approx(0.5)
        assert metrics[RECALL] == approx(0.25)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == precision_per_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == recall_per_st

        assert _image_level_base(metrics) == {
            AVERAGE_PRECISION: approx(1.0 / 9.0), PRECISION: approx(1.0 / 3.0), RECALL: approx(1.0 / 3.0)
        }

        cm1 = [[5, 5, 0, 0], [0, 0, 0, 5], [0, 0, 0, 0]]
        cm2 = [[0, 0, 0, 10], [0, 0, 0, 5], [0, 0, 0, 0]]
        assert metrics[CONFUSION_MATRICES_PER_SCORE_THRESHOLD] == {
            st: cm1 if st <= 0.5 else cm2
            for st in np.arange(0, 10) / 10.0
        }

    def test_efficient_pickling(self):
        num_images = 10_000
        max_num_bytes = 500_000

        ive = IncrementalVocEvaluator(True, 10, 0.5)
        meta_info_per_image = [
            {"width": 640, "height": 480, "iscrowd": np.array([False])}
            for _ in range(num_images)
        ]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200],
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": None
            }
            for _ in range(num_images)
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([
                    [100, 100, 200, 200]
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": np.array([0.5])
            }
            for _ in range(num_images)
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        ive.optimize_serialized_size()

        buffer = pickle.dumps(ive)
        assert len(buffer) < max_num_bytes

    @pytest.mark.usefixtures("new_clean_dir")
    @pytest.mark.parametrize("iou_threshold", [0.5, 0.2])
    def test_compare_random_against_vocmap(self, iou_threshold):
        np.random.seed(42)

        # Set the number of images etc.
        num_images, num_boxes_per_image = 1000, 250
        num_classes = 10
        width, height = 900, 600
        eps = 1e-4

        # Make the incremental VOC evaluator object.
        ive = IncrementalVocEvaluator(True, num_classes, iou_threshold)

        # Make random ground truth objects (boxes, labels) and predicted objects (boxes, labels, scores).
        gt_objects_per_image, predicted_objects_per_image = [], []
        for _ in range(num_images):
            gt_objects = _make_random_objects(
                width, height, num_classes, num_boxes_per_image, is_ground_truth=True
            )
            predicted_objects = _make_random_objects(
                width, height, num_classes, num_boxes_per_image, is_ground_truth=False
            )
            gt_objects_per_image.append(gt_objects)
            predicted_objects_per_image.append(predicted_objects)

        # Compute metrics with incremental VOC evaluator.
        # a. make meta info per image
        meta_info_per_image = [
            {"width": width, "height": height, "iscrowd": np.array([False] * num_boxes_per_image)}
        ] * num_images
        # run calculations
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)
        metrics = ive.compute_metrics()

        # Values computed with the original VOC evaluator (non-incremental) for seed 42.
        if iou_threshold == 0.5:
            vocmap_metrics = {
                "per_label_metrics": {
                    0: {"precision": 0.1356, "recall": 0.1345, "average_precision": 0.0210},
                    1: {"precision": 0.1343, "recall": 0.1344, "average_precision": 0.0206},
                    2: {"precision": 0.1310, "recall": 0.1338, "average_precision": 0.0198},
                    3: {"precision": 0.1334, "recall": 0.1329, "average_precision": 0.0199},
                    4: {"precision": 0.1365, "recall": 0.1381, "average_precision": 0.0210},
                    5: {"precision": 0.1349, "recall": 0.1345, "average_precision": 0.0203},
                    6: {"precision": 0.1368, "recall": 0.1344, "average_precision": 0.0210},
                    7: {"precision": 0.1341, "recall": 0.1341, "average_precision": 0.0203},
                    8: {"precision": 0.1360, "recall": 0.1356, "average_precision": 0.0203},
                    9: {"precision": 0.1347, "recall": 0.1351, "average_precision": 0.0210}
                },
                "precision": 0.13473094999790192,
                "recall": 0.1347283124923706,
                "mean_average_precision": 0.02052048221230507
            }
        elif iou_threshold == 0.2:
            vocmap_metrics = {
                "per_label_metrics": {
                    0: {"precision": 0.3930, "recall": 0.3900, "average_precision": 0.2025},
                    1: {"precision": 0.3898, "recall": 0.3899, "average_precision": 0.2018},
                    2: {"precision": 0.3865, "recall": 0.3948, "average_precision": 0.2019},
                    3: {"precision": 0.3900, "recall": 0.3885, "average_precision": 0.1989},
                    4: {"precision": 0.3920, "recall": 0.3965, "average_precision": 0.2049},
                    5: {"precision": 0.3923, "recall": 0.3909, "average_precision": 0.2030},
                    6: {"precision": 0.3952, "recall": 0.3882, "average_precision": 0.2038},
                    7: {"precision": 0.3906, "recall": 0.3906, "average_precision": 0.2027},
                    8: {"precision": 0.3915, "recall": 0.3905, "average_precision": 0.2001},
                    9: {"precision": 0.3925, "recall": 0.3936, "average_precision": 0.2058}
                },
                "precision": 0.391350656747818,
                "recall": 0.39135509729385376,
                "mean_average_precision": 0.20254068076610565
            }
        else:
            vocmap_metrics = None

        # Check global metrics.
        assert approx(metrics[MEAN_AVERAGE_PRECISION], abs=eps) == approx(
            vocmap_metrics[MEAN_AVERAGE_PRECISION], abs=eps
        )
        assert approx(metrics[PRECISION], abs=eps) == approx(vocmap_metrics[PRECISION], abs=eps)
        assert approx(metrics[RECALL], abs=eps) == approx(vocmap_metrics[RECALL], abs=eps)

        # Check per-class metrics.
        for c in range(num_classes):
            m = metrics[PER_LABEL_METRICS][c]
            vm = vocmap_metrics[PER_LABEL_METRICS][c]
            assert approx(m[AVERAGE_PRECISION], abs=eps) == approx(vm[AVERAGE_PRECISION], abs=eps)
            assert approx(m[PRECISION], abs=eps) == approx(vm[PRECISION], abs=eps)
            assert approx(m[RECALL], abs=eps) == approx(vm[RECALL], abs=eps)

    def test_single_image_two_gt_one_pred_image_level(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False, False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [160, 120, 320, 240],
                    [320, 240, 480, 360],
                ]),
                "masks": None,
                "classes": np.array([1, 1]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert _image_level_base(metrics) == {
            AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0)
        }

    def test_single_image_one_gt_two_pred_image_level(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [320, 240, 480, 360],
                ]),
                "masks": None,
                "classes": np.array([2]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([
                    [160, 120, 300, 220],
                    [320, 240, 460, 340],
                ]),
                "masks": None,
                "classes": np.array([2, 2]),
                "scores": np.array([0.64, 0.88])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert _image_level_base(metrics) == {
            AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0)
        }

    def test_single_image_one_gt_one_pred_no_match_image_level(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([2]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert _image_level_base(metrics) == {
            AVERAGE_PRECISION: approx(0.0), PRECISION: approx(0.0), RECALL: approx(0.0)
        }

    def test_two_images_multi_gt_multi_pred_image_level(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [
            {"width": 640, "height": 480, "iscrowd": np.array([False, False])},
            {"width": 640, "height": 480, "iscrowd": np.array([False])}
        ]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [160, 120, 320, 240],
                    [320, 240, 480, 360],
                ]),
                "masks": None,
                "classes": np.array([1, 1]),
                "scores": None
            },
            {
                "boxes": np.array([
                    [320, 240, 480, 360],
                ]),
                "masks": None,
                "classes": np.array([1]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.25])
            },
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert _image_level_base(metrics) == {
            AVERAGE_PRECISION: approx(0.25), PRECISION: approx(0.5), RECALL: approx(0.5)
        }

    def test_four_images_multi_gt_multi_pred_image_level(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [
            {"width": 640, "height": 480, "iscrowd": np.array([False])},
            {"width": 640, "height": 480, "iscrowd": np.array([])},
            {"width": 640, "height": 480, "iscrowd": np.array([False, False])},
            {"width": 640, "height": 480, "iscrowd": np.array([False])}
        ]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [160, 120, 320, 240],
                ]),
                "masks": None,
                "classes": np.array([0]),
                "scores": None
            },
            {
                "boxes": np.array([]),
                "masks": None,
                "classes": np.array([]),
                "scores": None
            },
            {
                "boxes": np.array([
                    [160, 120, 320, 240],
                    [320, 240, 480, 360],
                ]),
                "masks": None,
                "classes": np.array([2, 2]),
                "scores": None
            },
            {
                "boxes": np.array([
                    [0, 0, 640, 480],
                ]),
                "masks": None,
                "classes": np.array([1]),
                "scores": None
            },
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([0]), "scores": np.array([0.5])
            },
            {
                "boxes": np.array([[0, 0, 640, 480]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.5])
            },
            {
                "boxes": np.array([]), "masks": None,
                "classes": np.array([]), "scores": np.array([])
            },
            {
                "boxes": np.array([]), "masks": None,
                "classes": np.array([]), "scores": np.array([])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert _image_level_base(metrics) == {
            AVERAGE_PRECISION: approx(1.0 / 6.0), PRECISION: approx(0.5), RECALL: approx(1.0 / 3.0)
        }

    @pytest.mark.parametrize("num_classes", [0, 1])
    def test_three_images_no_gt_no_pred(self, num_classes):
        ive = IncrementalVocEvaluator(True, num_classes, 0.5)

        meta_info_per_image = [
            {"width": 640, "height": 480, "iscrowd": np.array([], dtype=bool)}
            for _ in range(3)
        ]
        gt_objects_per_image = [
            {"boxes": np.zeros((0, 4)), "masks": None, "classes": np.zeros((0,))}
            for _ in range(3)
        ]
        predicted_objects_per_image = [
            {"boxes": np.zeros((0, 4)), "masks": None, "classes": np.zeros((0,)), "scores": np.zeros((0,))}
            for _ in range(3)
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        undefined_for_all_st = {st / 100.0: -1.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            i: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: undefined_for_all_st, RECALLS_PER_SCORE_THRESHOLD: undefined_for_all_st
            }
            for i in range(num_classes)
        }

        assert metrics[MEAN_AVERAGE_PRECISION] == -1.0
        assert metrics[PRECISION] == -1.0
        assert metrics[RECALL] == -1.0
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == undefined_for_all_st
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == undefined_for_all_st

        assert _image_level_base(metrics) == {
            AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0
        }

        assert metrics[CONFUSION_MATRICES_PER_SCORE_THRESHOLD] == {
            -1.0: [] if num_classes == 0 else [[0, 0]]
        }

    def test_hundred_images_multi_gt_multi_pred_image_level(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [
            {"width": 640, "height": 480, "iscrowd": np.array([])} for _ in range(98)
        ] + [
            {"width": 640, "height": 480, "iscrowd": np.array([False])}
            for _ in range(2)
        ]
        gt_objects_per_image = [
            {"boxes": np.array([]), "masks": None, "classes": np.array([]), "scores": None} for _ in range(98)
        ] + [
            {
                "boxes": np.array([[160, 120, 320, 240]]),
                "masks": None,
                "classes": np.array([1]),
                "scores": None
            }
            for _ in range(2)
        ]
        predicted_objects_per_image = [
            # TN
            {
                "boxes": np.array([]), "masks": None, "classes": np.array([]), "scores": np.array([])
            }
            for _ in range(90)
        ] + [
            # FP
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([2]), "scores": np.array([0.66])
            }
            for _ in range(90, 98)
        ] + [
            # FN
            {
                "boxes": np.array([]), "masks": None, "classes": np.array([]), "scores": np.array([])
            }
        ] + [
            # TP
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.33])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert _image_level_base(metrics) == {
            AVERAGE_PRECISION: approx(0.5 / 9.0), PRECISION: approx(1.0 / 9.0), RECALL: approx(0.5)
        }

    def test_multi_image_random_gt_pred_image_level(self):
        np.random.seed(42)

        num_images, num_boxes_per_image = 40_000, 25
        num_classes = 10
        width, height = 64, 48

        ive = IncrementalVocEvaluator(True, num_classes, 0.5)

        # Make random ground truth objects (boxes, labels) and predicted objects (boxes, labels, scores).
        gt_objects_per_image, predicted_objects_per_image = [], []
        for _ in range(num_images):
            gt_objects = _make_random_objects(
                width, height, num_classes, num_boxes_per_image, is_ground_truth=True
            )
            predicted_objects = _make_random_objects(
                width, height, num_classes, num_boxes_per_image, is_ground_truth=False
            )
            gt_objects_per_image.append(gt_objects)
            predicted_objects_per_image.append(predicted_objects)

        meta_info_per_image = [
            {"width": width, "height": height, "iscrowd": np.array([False] * num_boxes_per_image)}
        ] * num_images

        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        def check_within_bounds(image_level_metric_name):
            v = metrics[IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS][image_level_metric_name]
            assert (v > 0.0) and (v < 1.0)

        check_within_bounds(AVERAGE_PRECISION)
        check_within_bounds(PRECISION)
        check_within_bounds(RECALL)

    def test_single_image_one_gt_one_pred_perfect_match_confusion_matrix(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        cm1 = [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]]
        cm2 = [[0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0]]
        assert metrics[CONFUSION_MATRICES_PER_SCORE_THRESHOLD] == {
            st: cm1 if st <= 0.7 else cm2
            for st in np.arange(0, 10) / 10.0
        }

    def test_single_image_one_gt_one_pred_different_class_confusion_matrix(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([2]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        cm1 = [[0, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 0]]
        cm2 = [[0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0]]
        assert metrics[CONFUSION_MATRICES_PER_SCORE_THRESHOLD] == {
            st: cm1 if st <= 0.7 else cm2
            for st in np.arange(0, 10) / 10.0
        }

    def test_single_image_one_gt_one_pred_no_overlap_confusion_matrix(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[320, 240, 480, 360]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.75])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        assert metrics[CONFUSION_MATRICES_PER_SCORE_THRESHOLD] == {
            -1.0: [[0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0]]
        }

    def test_single_image_three_gt_three_pred_partial_match_confusion_matrix(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False, False, False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [160, 120, 320, 240],
                    [320, 120, 480, 240],
                    [480, 120, 640, 240]
                ]),
                "masks": None,
                "classes": np.array([0, 1, 2]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([
                    [160, 120, 320, 240],
                    [320, 120, 480, 240],
                    [480, 120, 640, 240]
                ]),
                "masks": None,
                "classes": np.array([2, 1, 1]),
                "scores": np.array([0.5, 0.5, 0.5])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        cm1 = [[0, 0, 1, 0], [0, 1, 0, 0], [0, 1, 0, 0]]
        cm2 = [[0, 0, 0, 1], [0, 0, 0, 1], [0, 0, 0, 1]]
        assert metrics[CONFUSION_MATRICES_PER_SCORE_THRESHOLD] == {
            st: cm1 if st <= 0.5 else cm2
            for st in np.arange(0, 10) / 10.0
        }

    def test_single_image_three_gt_four_pred_partial_match_confusion_matrix(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False, False, False])}]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [160, 120, 320, 240],
                    [320, 120, 480, 240],
                    [480, 120, 640, 240]
                ]),
                "masks": None,
                "classes": np.array([0, 1, 2]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([
                    [160, 120, 320, 240],
                    [320, 120, 480, 240],
                    [480, 120, 640, 240],
                    [0, 120, 160, 240]
                ]),
                "masks": None,
                "classes": np.array([2, 1, 1, 0]),
                "scores": np.array([0.5, 0.5, 0.5, 0.5])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        cm1 = [[0, 0, 1, 0], [0, 1, 0, 0], [0, 1, 0, 0]]
        cm2 = [[0, 0, 0, 1], [0, 0, 0, 1], [0, 0, 0, 1]]
        assert metrics[CONFUSION_MATRICES_PER_SCORE_THRESHOLD] == {
            st: cm1 if st <= 0.5 else cm2
            for st in np.arange(0, 10) / 10.0
        }

    def test_single_image_seven_gt_seven_pred_partial_match_confusion_matrix(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [{"width": 640, "height": 480, "iscrowd": np.array([False] * 7)}]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [0, 120, 160, 240],
                    [160, 120, 320, 240],
                    [320, 120, 480, 240],
                    [480, 120, 640, 240],
                    [0, 240, 160, 360],
                    [160, 240, 320, 360],
                    [320, 240, 480, 360]
                ]),
                "masks": None,
                "classes": np.array([0, 1, 1, 1, 0, 2, 2]),
                "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([
                    [0, 120, 160, 240],
                    [160, 120, 320, 240],
                    [320, 120, 480, 240],
                    [480, 120, 640, 240],
                    [0, 240, 160, 360],
                    [160, 240, 320, 360],
                    [320, 240, 480, 360]
                ]),
                "masks": None,
                "classes": np.array([0, 1, 1, 1, 2, 1, 1]),
                "scores": np.array([0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        cm1 = [[1, 0, 1, 0], [0, 3, 0, 0], [0, 2, 0, 0]]
        cm2 = [[0, 0, 0, 2], [0, 0, 0, 3], [0, 0, 0, 2]]
        assert metrics[CONFUSION_MATRICES_PER_SCORE_THRESHOLD] == {
            st: cm1 if st <= 0.5 else cm2
            for st in np.arange(0, 10) / 10.0
        }

    def test_two_images_three_gt_three_pred_partial_match_confusion_matrix(self):
        ive = IncrementalVocEvaluator(True, 3, 0.5)

        meta_info_per_image = [
            {"width": 640, "height": 480, "iscrowd": np.array([False, False])},
            {"width": 640, "height": 480, "iscrowd": np.array([False])}
        ]
        gt_objects_per_image = [
            {
                "boxes": np.array([
                    [160, 120, 320, 240],
                    [320, 240, 480, 360],
                ]),
                "masks": None,
                "classes": np.array([1, 2]),
                "scores": None
            },
            {
                "boxes": np.array([[320, 240, 480, 360]]), "masks": None,
                "classes": np.array([0]), "scores": None
            }
        ]
        predicted_objects_per_image = [
            {
                "boxes": np.array([[160, 120, 320, 240]]), "masks": None,
                "classes": np.array([1]), "scores": np.array([0.5])
            },
            {
                "boxes": np.array([[160, 120, 320, 240], [320, 240, 480, 360]]), "masks": None,
                "classes": np.array([1, 0]), "scores": np.array([1.0, 1.0])
            }
        ]
        ive.evaluate_batch(gt_objects_per_image, predicted_objects_per_image, meta_info_per_image)

        metrics = ive.compute_metrics()

        _check_metrics_keys(metrics)

        cm1 = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1]]
        cm2 = [[1, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 1]]
        assert metrics[CONFUSION_MATRICES_PER_SCORE_THRESHOLD] == {
            st: cm1 if st <= 0.5 else cm2
            for st in np.arange(0, 10) / 10.0
        }
