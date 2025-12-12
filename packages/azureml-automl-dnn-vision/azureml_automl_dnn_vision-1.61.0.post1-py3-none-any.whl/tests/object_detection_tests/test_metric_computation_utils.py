import pytest

import numpy as np
import torch

from pytest import approx

from azureml.automl.dnn.vision.common.constants import MetricsLiterals
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionSystemException
from azureml.automl.dnn.vision.object_detection.common import masktools
from azureml.automl.dnn.vision.object_detection.eval.metric_computation_utils import _map_score_voc_11_point_metric, \
    _map_score_voc_auc, _SCORE_THRESHOLDS_FINE, _SCORE_THRESHOLDS_COARSE, calculate_pr_metrics, \
    calculate_confusion_matrices, match_objects


PRECISION, RECALL = MetricsLiterals.PRECISION, MetricsLiterals.RECALL
AVERAGE_PRECISION, MEAN_AVERAGE_PRECISION = MetricsLiterals.AVERAGE_PRECISION, MetricsLiterals.MEAN_AVERAGE_PRECISION
PRECISIONS_PER_SCORE_THRESHOLD = MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD
RECALLS_PER_SCORE_THRESHOLD = MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD


def _xyxy2xywh(box):
    return [
        float(box[0]), float(box[1]), float(box[2]) - float(box[0]), float(box[3]) - float(box[1])
    ]


def _fill_prpst_100_points(precisions_recalls_per_score_threshold):
    new_precisions_per_score_threshold, new_recalls_per_score_threshold = {}, {}

    precisions_per_score_threshold = {st: pr[0] for st, pr in precisions_recalls_per_score_threshold.items()}
    recalls_per_score_threshold = {st: pr[1] for st, pr in precisions_recalls_per_score_threshold.items()}
    for i in range(100):
        score_threshold = i / 100.0

        first_greater_equal_score_threshold = None
        for st in precisions_recalls_per_score_threshold:
            if st >= score_threshold:
                if (first_greater_equal_score_threshold is None) or (st < first_greater_equal_score_threshold):
                    first_greater_equal_score_threshold = st

        new_precisions_per_score_threshold[score_threshold] = precisions_per_score_threshold.get(
            first_greater_equal_score_threshold, -1.0
        )
        new_recalls_per_score_threshold[score_threshold] = recalls_per_score_threshold.get(
            first_greater_equal_score_threshold, 0.0
        )

    return new_precisions_per_score_threshold, new_recalls_per_score_threshold


def _check_prpst_equal(
    precisions_per_score_threshold1, recalls_per_score_threshold1,
    precisions_per_score_threshold2, recalls_per_score_threshold2
):
    score_thresholds1 = set(precisions_per_score_threshold1.keys()).union(recalls_per_score_threshold1.keys())
    score_thresholds2 = set(precisions_per_score_threshold2.keys()).union(recalls_per_score_threshold2.keys())
    assert score_thresholds1 == score_thresholds2

    for st in score_thresholds1:
        p1, r1 = precisions_per_score_threshold1[st], recalls_per_score_threshold1[st]
        p2, r2 = precisions_per_score_threshold2[st], recalls_per_score_threshold2[st]
        np.testing.assert_almost_equal(p1, p2, decimal=6)
        np.testing.assert_almost_equal(r1, r2, decimal=6)


def _fill_cmpst_10_points(num_gt_objects_per_class, confusion_matrices_per_score_threshold):
    num_classes = len(num_gt_objects_per_class)

    new_confusion_matrices_per_score_threshold = {}
    for i in range(10):
        score_threshold = i / 10.0

        first_greater_equal_score_threshold = None
        for st in confusion_matrices_per_score_threshold:
            if st >= score_threshold:
                if (first_greater_equal_score_threshold is None) or (st < first_greater_equal_score_threshold):
                    first_greater_equal_score_threshold = st

        if first_greater_equal_score_threshold is None:
            new_confusion_matrices_per_score_threshold[score_threshold] = [
                [0 for _ in range(num_classes)] + [num_gt_objects_per_class[c]]
                for c in range(num_classes)
            ]
        else:
            new_confusion_matrices_per_score_threshold[score_threshold] = confusion_matrices_per_score_threshold[
                first_greater_equal_score_threshold
            ]

    return new_confusion_matrices_per_score_threshold


def _check_cmpst_equal(confusion_matrices_per_score_threshold1, confusion_matrices_per_score_threshold2):
    assert sorted(list(confusion_matrices_per_score_threshold1.keys())) == sorted(list(
        confusion_matrices_per_score_threshold2.keys())
    )

    for score_threshold, confusion_matrix1 in confusion_matrices_per_score_threshold1.items():
        confusion_matrix2 = confusion_matrices_per_score_threshold2[score_threshold]
        confusion_matrix1 = np.array(confusion_matrix1)
        confusion_matrix2 = np.array(confusion_matrix2)
        assert confusion_matrix1.shape == confusion_matrix2.shape
        assert (confusion_matrix1 == confusion_matrix2).all()


class TestMetricComputationUtils:
    @staticmethod
    def _rle_mask_from_bbox(bbox, height, width):
        x1, y1, x2, y2 = bbox
        polygon = [[x1, y1, x2, y1, x2, y2, x1, y2, x1, y1]]
        rle_masks = masktools.convert_polygon_to_rle_masks(polygon, height, width)
        return rle_masks[0]

    def setup(self):
        np.random.seed(42)

    def test_map11_different_size(self):
        # Precision list and recall list of different size.
        precision_list = torch.rand(10, dtype=torch.float)
        recall_list = torch.rand(5, dtype=torch.float)

        with pytest.raises(AutoMLVisionSystemException):
            _map_score_voc_11_point_metric(precision_list.numpy(), recall_list.numpy())

    def test_map11_empty_lists(self):
        # Empty lists.
        precision_list = torch.tensor([], dtype=torch.float)
        recall_list = torch.tensor([], dtype=torch.float)

        _map_score_voc_11_point_metric(precision_list.numpy(), recall_list.numpy())

    def test_map11_random(self):
        # Random precision and recall values.
        precision_list = torch.rand(100, dtype=torch.float)
        recall_list, _ = torch.sort(torch.rand(100, dtype=torch.float))

        map_score = _map_score_voc_11_point_metric(precision_list.numpy(), recall_list.numpy())
        assert map_score.ndim == 0
        assert (map_score >= 0.0) and (map_score <= 1.0)

    def test_map11_three_points(self):
        # Three points on the PR curve: (0.15, 0.7), (0.5, 0.6), (0.85, 0.4).
        precision_list = torch.tensor([0.7, 0.6, 0.4])
        recall_list = torch.tensor([0.15, 0.5, 0.85])

        map_score = _map_score_voc_11_point_metric(precision_list.numpy(), recall_list.numpy())
        assert map_score == approx(5.0 / 11.0)

    def test_map11_lin_dec_prec(self):
        # Precision linearly decreasing from 1.0 to 0.0 over 20 steps.
        precision_list = torch.arange(1.0, -0.05, -0.05, dtype=torch.float)
        recall_list = torch.arange(0.0, 1.05, 0.05, dtype=torch.float)

        map_score = _map_score_voc_11_point_metric(precision_list.numpy(), recall_list.numpy())
        assert map_score == approx(0.5)

    def test_map11_duplicates(self):
        # Recall list with duplicate values.
        recall_list = torch.arange(0.0, 1.1, 0.1, dtype=torch.float)
        recall_list, _ = torch.sort(torch.cat((recall_list, recall_list, recall_list)))
        orig_precision_list = torch.rand(11, dtype=torch.float)
        precision_list, _ = torch.sort(torch.cat((orig_precision_list, orig_precision_list, orig_precision_list)),
                                       descending=True)

        # Since precision list is sorted, max precision at 11 recall points corresponding entry in orig_precision_list.
        # map score would be the average of the orig_precision_list.
        expected_map_score = orig_precision_list.sum() / orig_precision_list.nelement()
        expected_map_score = expected_map_score.item()

        map_score = _map_score_voc_11_point_metric(precision_list.numpy(), recall_list.numpy())
        assert round(map_score, 3) == round(expected_map_score, 3)

    def test_map_auc_different_size(self):
        # Precision list and recall list of different size.
        precision_list = torch.rand(10, dtype=torch.float)
        recall_list = torch.rand(5, dtype=torch.float)

        with pytest.raises(AutoMLVisionSystemException):
            _map_score_voc_auc(precision_list.numpy(), recall_list.numpy())

    def test_map_auc_recall_not_sorted(self):
        # Recall list not sorted.
        precision_list = torch.rand(10, dtype=torch.float)
        recall_list = torch.arange(1.0, 0.0, -0.1, dtype=torch.float)

        with pytest.raises(AutoMLVisionSystemException):
            _map_score_voc_auc(precision_list.numpy(), recall_list.numpy())

    def test_map_auc_empty_lists(self):
        # Empty lists.

        _map_score_voc_auc(np.array([]), np.array([]))

    def test_map_auc_random(self):
        # Random precision and recall values.
        precision_list = torch.rand(10, dtype=torch.float)
        recall_list, _ = torch.sort(torch.rand(10, dtype=torch.float))

        map_score = _map_score_voc_auc(precision_list.numpy(), recall_list.numpy())
        assert map_score.ndim == 0
        assert (map_score >= 0.0) and (map_score <= 1.0)

    def test_map_auc_five_points(self):
        # Five points on the PR curve: (0.1, 0.8), (0.35, 0.9), (0.4, 0.5), (0.55, 0.6), (0.8, 0.65).
        precision_list = torch.tensor([0.8, 0.9, 0.5, 0.6, 0.65])
        recall_list = torch.tensor([0.1, 0.35, 0.4, 0.55, 0.8])

        expected_map_score = 0.1 * 0.9 + 0.25 * 0.9 + 0.05 * 0.65 + 0.15 * 0.65 + 0.25 * 0.65

        map_score = _map_score_voc_auc(precision_list.numpy(), recall_list.numpy())
        assert map_score == approx(expected_map_score)

    def test_map_auc_five_points_one_duplicate(self):
        # Five points on the PR curve, duplicate recall: (0.1, 0.8), (0.4, 0.5), (0.4, 0.9), (0.55, 0.6), (0.8, 0.65).
        precision_list = torch.tensor([0.8, 0.5, 0.9, 0.6, 0.65])
        recall_list = torch.tensor([0.1, 0.4, 0.4, 0.55, 0.8])

        expected_map_score = 0.1 * 0.9 + 0.25 * 0.9 + 0.05 * 0.9 + 0.15 * 0.65 + 0.25 * 0.65

        map_score = _map_score_voc_auc(precision_list.numpy(), recall_list.numpy())
        assert map_score == approx(expected_map_score)

    def test_map_auc_lin_dec_prec(self):
        # Precision linearly decreasing from 1.0 to 0.0 over 100 steps.
        precision_list = torch.arange(1.0, -0.01, -0.01, dtype=torch.float)
        recall_list = torch.arange(0.0, 1.01, 0.01, dtype=torch.float)

        map_score = _map_score_voc_auc(precision_list.numpy(), recall_list.numpy())
        assert map_score == approx(0.5, abs=0.01)

    def test_map_auc_unique_recall_value(self):
        # Single recall value to verify unique recall list logic.
        precision_list = torch.rand(10, dtype=torch.float)
        recall_list = 0.5 * torch.ones(10, dtype=torch.float)

        map_score = _map_score_voc_auc(precision_list.numpy(), recall_list.numpy())
        assert map_score.ndim == 0
        assert (map_score >= 0.0) and (map_score <= 1.0)

    def test_map_auc_duplicates(self):
        # Recall list with duplicate values.
        recall_list = torch.arange(0.1, 1.1, 0.1, dtype=torch.float)
        recall_list, _ = torch.sort(torch.cat((recall_list, recall_list, recall_list)))
        orig_precision_list = torch.rand(10, dtype=torch.float)
        precision_list, _ = torch.sort(torch.cat((orig_precision_list, orig_precision_list, orig_precision_list)),
                                       descending=True)

        expected_map_score = (torch.sum(orig_precision_list) * 0.1).item()

        map_score = _map_score_voc_auc(precision_list.numpy(), recall_list.numpy())
        assert map_score.ndim == 0
        assert round(map_score.item(), 3) == round(expected_map_score, 3)

    def test_match_boxes_basic(self):
        gt_boxes = np.array([
            _xyxy2xywh([20, 20, 80, 80])
        ])
        is_crowd = np.array([False])

        predicted_boxes = np.array([
            _xyxy2xywh([25, 25, 75, 75]),
            _xyxy2xywh([90, 90, 110, 110])
        ])
        predicted_scores = np.array([1.0, 1.0])

        tp_fp_labels, predicted_assignment = match_objects(gt_boxes, is_crowd, predicted_boxes, predicted_scores, 0.5)

        assert (tp_fp_labels == np.array([1, 0])).all()
        assert (predicted_assignment == np.array([0, -1])).all()

    def test_match_boxes_crowd(self):
        gt_boxes = np.array([
            _xyxy2xywh([20, 20, 80, 80])
        ])
        is_crowd = np.array([True])

        predicted_boxes = np.array([
            _xyxy2xywh([25, 25, 75, 75]),
            _xyxy2xywh([90, 90, 110, 110])
        ])
        predicted_scores = np.array([1.0, 1.0])

        tp_fp_labels, predicted_assignment = match_objects(gt_boxes, is_crowd, predicted_boxes, predicted_scores, 0.5)

        assert (tp_fp_labels == np.array([2, 0])).all()
        assert (predicted_assignment == np.array([-1, -1])).all()

    def test_match_boxes_no_double_assignment(self):
        gt_boxes = np.array([
            _xyxy2xywh([20, 20, 80, 80])
        ])
        is_crowd = np.array([False])

        predicted_boxes = np.array([
            _xyxy2xywh([25, 25, 75, 75]),
            _xyxy2xywh([20, 20, 80, 80])
        ])
        predicted_scores = np.array([1.0, 1.0])

        tp_fp_labels, predicted_assignment = match_objects(gt_boxes, is_crowd, predicted_boxes, predicted_scores, 0.5)

        assert (tp_fp_labels == np.array([0, 1])).all()
        assert (predicted_assignment == np.array([-1, 0])).all()

    def test_match_boxes_prediction_below_threshold(self):
        gt_boxes = np.array([
            _xyxy2xywh([20, 20, 80, 80])
        ])
        is_crowd = np.array([False])

        predicted_boxes = np.array([
            _xyxy2xywh([25, 25, 75, 75]),
            _xyxy2xywh([20, 20, 80, 80])
        ])
        predicted_scores = np.array([1.0, 0.1])

        tp_fp_labels, predicted_assignment = match_objects(gt_boxes, is_crowd, predicted_boxes, predicted_scores, 0.5)

        assert (tp_fp_labels == np.array([1, 0])).all()
        assert (predicted_assignment == np.array([0, -1])).all()

    def test_match_masks_basic(self):
        width, height = 480, 640

        gt_masks = [self._rle_mask_from_bbox([20, 20, 80, 80], width, height)]
        is_crowd = np.array([False])

        predicted_masks = [
            self._rle_mask_from_bbox([25, 25, 75, 75], width, height),
            self._rle_mask_from_bbox([90, 90, 110, 110], width, height)
        ]
        predicted_scores = np.array([1.0, 1.0])

        tp_fp_labels, _ = match_objects(gt_masks, is_crowd, predicted_masks, predicted_scores, 0.5)

        assert (tp_fp_labels == np.array([1, 0])).all()

    def test_pr_metrics_no_gt_no_pred(self):
        num_gt_boxes = 0
        tp_fp_labels = np.array([])
        scores = np.array([])

        metrics = calculate_pr_metrics(num_gt_boxes, tp_fp_labels, scores, None, False, -1.0)
        assert metrics[AVERAGE_PRECISION] == -1.0
        assert metrics[PRECISION] == -1.0
        assert metrics[RECALL] == -1.0
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == {st: -1.0 for st in _SCORE_THRESHOLDS_FINE}
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == {st: -1.0 for st in _SCORE_THRESHOLDS_FINE}

    def test_pr_metrics_one_gt_no_pred(self):
        num_gt_boxes = 1
        tp_fp_labels = np.array([])
        scores = np.array([])

        metrics = calculate_pr_metrics(num_gt_boxes, tp_fp_labels, scores, None, False, -1.0)
        assert metrics[AVERAGE_PRECISION] == 0.0
        assert metrics[PRECISION] == -1.0
        assert metrics[RECALL] == 0.0
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == {st: -1.0 for st in _SCORE_THRESHOLDS_FINE}
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == {st: 0.0 for st in _SCORE_THRESHOLDS_FINE}

    def test_pr_metrics_no_gt_one_pred(self):
        num_gt_boxes = 0
        tp_fp_labels = np.array([0])
        scores = np.array([0.3])

        metrics = calculate_pr_metrics(num_gt_boxes, tp_fp_labels, scores, None, False, -1.0)
        assert metrics[AVERAGE_PRECISION] == -1.0
        assert metrics[PRECISION] == 0.0
        assert metrics[RECALL] == -1.0
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == {st: 0.0 for st in _SCORE_THRESHOLDS_FINE}
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == {st: -1.0 for st in _SCORE_THRESHOLDS_FINE}

    def test_pr_metrics_one_gt_two_pred1(self):
        num_gt_boxes = 1
        tp_fp_labels = np.array([0, 1])
        scores = np.array([0.3, 0.9])

        metrics = calculate_pr_metrics(num_gt_boxes, tp_fp_labels, scores, None, False, -1.0)
        assert metrics[AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(0.5)
        assert metrics[RECALL] == approx(1.0)
        _check_prpst_equal(
            metrics[PRECISIONS_PER_SCORE_THRESHOLD], metrics[RECALLS_PER_SCORE_THRESHOLD],
            *_fill_prpst_100_points({0.3: [0.5, 1.0], 0.9: [1.0, 1.0]})
        )

    def test_pr_metrics_one_gt_two_pred_image_level1(self):
        num_images_with_gt_boxes = 1
        tp_fp_labels = np.array([0, 1])
        scores = np.array([0.3, 0.9])
        image_indexes = np.array([0, 0])

        metrics = calculate_pr_metrics(num_images_with_gt_boxes, tp_fp_labels, scores, image_indexes, False, -1.0)
        assert metrics[AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)
        _check_prpst_equal(
            metrics[PRECISIONS_PER_SCORE_THRESHOLD], metrics[RECALLS_PER_SCORE_THRESHOLD],
            *_fill_prpst_100_points({0.3: [1.0, 1.0], 0.9: [1.0, 1.0]})
        )

    def test_pr_metrics_one_gt_two_pred_image_level2(self):
        num_images_with_gt_boxes = 1
        tp_fp_labels = np.array([0, 1])
        scores = np.array([0.9, 0.3])
        image_indexes = np.array([0, 1])

        metrics = calculate_pr_metrics(num_images_with_gt_boxes, tp_fp_labels, scores, image_indexes, False, -1.0)
        assert metrics[AVERAGE_PRECISION] == approx(0.5)
        assert metrics[PRECISION] == approx(0.5)
        assert metrics[RECALL] == approx(1.0)
        _check_prpst_equal(
            metrics[PRECISIONS_PER_SCORE_THRESHOLD], metrics[RECALLS_PER_SCORE_THRESHOLD],
            *_fill_prpst_100_points({0.3: [0.5, 1.0], 0.9: [0.0, 0.0]})
        )

    def test_pr_metrics_two_gt_two_pred(self):
        num_gt_boxes = 2
        tp_fp_labels = np.array([1, 1])
        scores = np.array([0.3, 0.9])

        metrics = calculate_pr_metrics(num_gt_boxes, tp_fp_labels, scores, None, False, -1.0)
        assert metrics[AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)
        _check_prpst_equal(
            metrics[PRECISIONS_PER_SCORE_THRESHOLD], metrics[RECALLS_PER_SCORE_THRESHOLD],
            *_fill_prpst_100_points({0.3: [1.0, 1.0], 0.9: [1.0, 0.5]})
        )

    def test_pr_metrics_two_gt_two_pred_image_level(self):
        num_images_with_gt_boxes = 2
        tp_fp_labels = np.array([1, 1])
        scores = np.array([0.3, 0.9])
        image_indexes = np.array([0, 1])

        metrics = calculate_pr_metrics(num_images_with_gt_boxes, tp_fp_labels, scores, image_indexes, False, -1.0)
        assert metrics[AVERAGE_PRECISION] == approx(1.0)
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)
        _check_prpst_equal(
            metrics[PRECISIONS_PER_SCORE_THRESHOLD], metrics[RECALLS_PER_SCORE_THRESHOLD],
            *_fill_prpst_100_points({0.3: [1.0, 1.0], 0.9: [1.0, 0.5]})
        )

    def test_pr_metrics_four_gt_one_pred_other(self):
        num_gt_boxes = 4
        tp_fp_labels = np.array([0, 1, 1, 2])
        scores = np.array([0.4, 0.2, 0.8, 0.6])

        metrics = calculate_pr_metrics(num_gt_boxes, tp_fp_labels, scores, None, False, -1.0)
        assert metrics[AVERAGE_PRECISION] == approx(0.25 * 1.0 + 0.25 * (2.0 / 3.0))
        assert metrics[PRECISION] == approx(2.0 / 3.0)
        assert metrics[RECALL] == approx(0.5)
        _check_prpst_equal(
            metrics[PRECISIONS_PER_SCORE_THRESHOLD], metrics[RECALLS_PER_SCORE_THRESHOLD],
            *_fill_prpst_100_points({0.2: [2.0 / 3.0, 0.5], 0.4: [0.5, 0.25], 0.6: [1.0, 0.25], 0.8: [1.0, 0.25]})
        )

    def test_pr_metrics_two_gt_two_pred_other(self):
        num_gt_boxes = 2
        tp_fp_labels = np.array([2, 2])
        scores = np.array([0.25, 0.75])

        metrics = calculate_pr_metrics(num_gt_boxes, tp_fp_labels, scores, None, False, -1.0)
        assert metrics[AVERAGE_PRECISION] == approx(0.0)
        assert metrics[PRECISION] == approx(0.0)
        assert metrics[RECALL] == approx(0.0)
        _check_prpst_equal(
            metrics[PRECISIONS_PER_SCORE_THRESHOLD], metrics[RECALLS_PER_SCORE_THRESHOLD],
            *_fill_prpst_100_points({0.25: [0.0, 0.0], 0.75: [0.0, 0.0]})
        )

    def test_pr_metrics_11_point(self):
        num_gt_boxes = 3

        tp_fp_labels = np.array([1, 0, 1, 0, 1])
        scores = np.array([0.1, 0.2, 0.3, 0.4, 0.5])

        tp_fp_labels, scores = np.array(tp_fp_labels), np.array(scores)

        metrics = calculate_pr_metrics(num_gt_boxes, tp_fp_labels, scores, None, True, -1.0)
        assert metrics[AVERAGE_PRECISION] == approx((4 * 1.0 + 3 * (2.0 / 3.0) + 4 * 0.6) / 11.0)
        assert metrics[PRECISION] == approx(0.6)
        assert metrics[RECALL] == approx(1.0)
        _check_prpst_equal(
            metrics[PRECISIONS_PER_SCORE_THRESHOLD], metrics[RECALLS_PER_SCORE_THRESHOLD],
            *_fill_prpst_100_points(
                {
                    0.1: [0.6, 1.0], 0.2: [0.5, 2.0 / 3.0], 0.3: [2.0 / 3.0, 2.0 / 3.0], 0.4: [0.5, 1.0 / 3.0],
                    0.5: [1.0, 1.0 / 3.0]
                }
            )
        )

    def test_confusion_matrices_diagonal(self):
        confusion_matrices_per_score_threshold = calculate_confusion_matrices(
            [1, 1, 1], np.array([[0, 0, 0.5], [1, 1, 0.6], [2, 2, 0.7]])
        )

        _check_cmpst_equal(confusion_matrices_per_score_threshold, _fill_cmpst_10_points(
            [1, 1, 1],
            {
                0.5: [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0]], 0.6: [[0, 0, 0, 1], [0, 1, 0, 0], [0, 0, 1, 0]],
                0.7: [[0, 0, 0, 1], [0, 0, 0, 1], [0, 0, 1, 0]]
            }
        ))

    def test_confusion_matrices_single_class(self):
        confusion_matrices_per_score_threshold = calculate_confusion_matrices(
            [3], np.array([[0, 0, 0.1], [0, 0, 0.2], [0, 0, 0.4]])
        )

        _check_cmpst_equal(confusion_matrices_per_score_threshold, _fill_cmpst_10_points(
            [3], {0.1: [[3, 0]], 0.2: [[2, 1]], 0.4: [[1, 2]]}
        ))

    def test_confusion_matrices_no_gt(self):
        confusion_matrices_per_score_threshold = calculate_confusion_matrices([0, 0], np.zeros((0, 3)))

        _check_cmpst_equal(confusion_matrices_per_score_threshold, {-1.0: [[0, 0, 0], [0, 0, 0]]})

    def test_confusion_matrices_no_pred(self):
        confusion_matrices_per_score_threshold = calculate_confusion_matrices([1], np.zeros((0, 3)))

        _check_cmpst_equal(confusion_matrices_per_score_threshold, {-1.0: [[0, 1]]})

    def test_confusion_matrices_diagonal_greater_than_1(self):
        confusion_matrices_per_score_threshold = calculate_confusion_matrices(
            [2, 3, 1], np.array([[0, 0, 0.5], [0, 0, 0.5], [1, 1, 0.6], [1, 1, 0.6], [1, 1, 0.6], [2, 2, 0.7]])
        )

        _check_cmpst_equal(confusion_matrices_per_score_threshold, _fill_cmpst_10_points(
            [2, 3, 1],
            {
                0.5: [[2, 0, 0, 0], [0, 3, 0, 0], [0, 0, 1, 0]], 0.6: [[0, 0, 0, 2], [0, 3, 0, 0], [0, 0, 1, 0]],
                0.7: [[0, 0, 0, 2], [0, 0, 0, 3], [0, 0, 1, 0]]
            }
        ))

    def test_confusion_matrices_full(self):
        confusion_matrices_per_score_threshold = calculate_confusion_matrices(
            [2, 2], np.array([[1, 1, 0.7999], [0, 1, 0.25], [1, 0, 0.31], [0, 0, 0.867345]])
        )

        _check_cmpst_equal(confusion_matrices_per_score_threshold, _fill_cmpst_10_points(
            [2, 2],
            {
                0.2: [[1, 1, 0], [1, 1, 0]], 0.3: [[1, 0, 1], [1, 1, 0]], 0.7: [[1, 0, 1], [0, 1, 1]],
                0.8: [[1, 0, 1], [0, 0, 2]]
            }
        ))

    def test_confusion_matrices_random(self):
        num_classes = 1_000
        num_predicted_objects = 1_000_000

        gt_classes = np.random.randint(0, num_classes, size=(num_predicted_objects, 1))
        predicted_classes = np.random.randint(0, num_classes, size=(num_predicted_objects, 1))
        predicted_scores = np.random.random(size=(num_predicted_objects, 1))

        num_gt_objects_per_class, _ = np.histogram(gt_classes, np.arange(num_classes + 1))
        num_gt_objects_per_class += np.random.randint(0, 5, size=(len(num_gt_objects_per_class),))

        confusion_matrices_per_score_threshold = calculate_confusion_matrices(
            num_gt_objects_per_class,
            np.concatenate((gt_classes, predicted_classes, predicted_scores), axis=1)
        )

        cm_min = np.zeros((num_classes, num_classes + 1), dtype=np.uint32)
        cm_max = np.concatenate((
            (10 * num_predicted_objects // (num_classes ** 2)) * np.ones((num_classes, num_classes), dtype=np.uint32),
            np.expand_dims(num_gt_objects_per_class, axis=1)
        ), axis=1)
        cm_previous = None
        for st in sorted(list(confusion_matrices_per_score_threshold.keys())):
            cm = np.array(confusion_matrices_per_score_threshold[st])
            assert (st >= 0.0) and (st <= 1.0)
            assert (cm.shape == cm_min.shape) and (cm.shape == cm_max.shape)
            assert (cm >= cm_min).all() and (cm <= cm_max).all()
            if cm_previous is not None:
                assert cm.shape == cm_previous.shape
                assert (cm[:, :-1] <= cm_previous[:, :-1]).all()
                assert (cm[:, -1] >= cm_previous[:, -1]).all()
            cm_previous = cm

    def test_score_thresholds_relation(self):
        assert set(_SCORE_THRESHOLDS_FINE).issuperset(set(_SCORE_THRESHOLDS_COARSE))
