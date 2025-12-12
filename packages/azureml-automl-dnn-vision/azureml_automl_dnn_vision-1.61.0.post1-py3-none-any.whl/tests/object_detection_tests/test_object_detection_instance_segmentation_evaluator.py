import numpy as np
import pytest
import torch

from pytest import approx

from azureml.automl.core.shared.constants import Tasks
from azureml.automl.dnn.vision.common.constants import MetricsLiterals
from azureml.automl.dnn.vision.object_detection.common.constants import ValidationMetricType, \
    TrainingLiterals, training_settings_defaults
from azureml.automl.dnn.vision.object_detection.common import masktools
import azureml.automl.dnn.vision.object_detection.common.object_detection_utils as od_utils
from azureml.automl.dnn.vision.object_detection.data.dataset_wrappers \
    import CommonObjectDetectionDatasetWrapper, DatasetProcessingType
from azureml.automl.dnn.vision.object_detection.eval.object_detection_instance_segmentation_evaluator import \
    ObjectDetectionInstanceSegmentationEvaluator
from azureml.automl.dnn.vision.object_detection_yolo.eval.yolo_evaluator import YoloEvaluator
from azureml.automl.dnn.vision.object_detection_yolo.utils.utils import xyxy2xywh
from tests.common.run_mock import ObjectDetectionDatasetMock


PRECISION, RECALL = MetricsLiterals.PRECISION, MetricsLiterals.RECALL
AVERAGE_PRECISION, MEAN_AVERAGE_PRECISION = MetricsLiterals.AVERAGE_PRECISION, MetricsLiterals.MEAN_AVERAGE_PRECISION
PRECISIONS_PER_SCORE_THRESHOLD = MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD
RECALLS_PER_SCORE_THRESHOLD = MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD
PER_LABEL_METRICS = MetricsLiterals.PER_LABEL_METRICS
IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS = MetricsLiterals.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS
CONFUSION_MATRICES_PER_SCORE_THRESHOLD = MetricsLiterals.CONFUSION_MATRICES_PER_SCORE_THRESHOLD


def convert_to_yolo_format(predicted_objects_per_image, gt_objects_per_image, meta_info_per_image):
    yolo_predtictions = []
    for prediction in predicted_objects_per_image:
        cur_predictions = torch.zeros(len(prediction['labels']), 6)
        cur_predictions[:, :4] = prediction['boxes']
        cur_predictions[:, 4] = prediction['scores']
        cur_predictions[:, 5] = prediction['labels']
        yolo_predtictions.append(cur_predictions)

    yolo_targets = []
    for gt_obj, info in zip(gt_objects_per_image, meta_info_per_image):
        width, height = info['width'], info['height']
        cur_targets = torch.empty(len(gt_obj['labels']), 6)
        cur_targets[:, 2:] = xyxy2xywh(gt_obj['boxes']) * \
            np.array([[1 / width, 1 / height, 1 / width, 1 / height]])
        cur_targets[:, 1] = gt_obj['labels']
        yolo_targets.append(cur_targets.numpy())

    return yolo_predtictions, yolo_targets


def get_mask_from_bbox(bbox, height, width):
    x1, y1, x2, y2 = bbox
    polygon = [[x1, y1, x2, y1, x2, y2, x1, y2, x1, y1]]
    rle_masks = masktools.convert_polygon_to_rle_masks(polygon, height, width)

    mask = masktools.decode_rle_masks_as_binary_mask(rle_masks)

    return torch.tensor(mask).unsqueeze(dim=0)


@pytest.mark.parametrize("dataset_processing_type",
                         [DatasetProcessingType.IMAGES, DatasetProcessingType.IMAGES_AND_TILES])
@pytest.mark.parametrize("yolo", [True, False])
@pytest.mark.parametrize("eval_type", [ValidationMetricType.COCO, ValidationMetricType.VOC])
def test_single_image_onegt_onepred_exact_match(dataset_processing_type, yolo, eval_type):

    dataset_items = [(None,
                     {"boxes": torch.tensor([[160, 120, 320, 240]], dtype=torch.float32),
                      "labels": torch.tensor([1])},
                     {"areas": [60000], "iscrowd": [0], "filename": "image_1.jpg",
                      "height": 640, "width": 480,
                      "original_width": 640, "original_height": 480
                      }
                      )]
    if eval_type == ValidationMetricType.COCO:
        dataset = ObjectDetectionDatasetMock(dataset_items, 3)
        dataset_wrapper = CommonObjectDetectionDatasetWrapper(dataset, DatasetProcessingType.IMAGES)
        val_index_map = dataset._classes
    else:
        dataset_wrapper = None
        val_index_map = ['1', '2', '3']

    training_settings_defaults['task_type'] = 'image-object-detection'
    training_settings_defaults[TrainingLiterals.VALIDATION_METRIC_TYPE] = eval_type
    if yolo:
        evaluator = YoloEvaluator(training_settings_defaults, class_names=val_index_map,
                                  dataset_processing_type=dataset_processing_type,
                                  dataset_wrapper=dataset_wrapper)
    else:
        evaluator = ObjectDetectionInstanceSegmentationEvaluator(
            training_settings_defaults, class_names=val_index_map, dataset_processing_type=dataset_processing_type,
            dataset_wrapper=dataset_wrapper
        )

    evaluator.start_evaluation(enable=True)

    meta_info_per_image = [x[2] for x in dataset_items]
    gt_objects_per_image = [x[1] for x in dataset_items]
    predicted_objects_per_image = [
        {
            "boxes": torch.tensor([[160, 120, 320, 240]], dtype=torch.float32),
            "masks": None, "labels": torch.tensor([1]), "scores": torch.tensor([0.75])
        }
    ]

    if yolo:
        predicted_objects_per_image, gt_objects_per_image = \
            convert_to_yolo_format(predicted_objects_per_image, gt_objects_per_image, meta_info_per_image)

    evaluator.evaluate_predictions(predictions_per_image=predicted_objects_per_image,
                                   image_infos=meta_info_per_image,
                                   targets_per_image=gt_objects_per_image)

    evaluator.finalize_evaluation()

    metrics = {}
    ive = evaluator.incremental_voc_evaluator if evaluator.eval_voc else None
    od_utils.compute_metrics(evaluator.eval_bounding_boxes,
                             evaluator.val_metric_type,
                             evaluator.coco_index, ive,
                             metrics, {},
                             evaluator.coco_metric_time, evaluator.voc_metric_time,
                             evaluator.primary_metric, is_train=False)

    assert metrics[MEAN_AVERAGE_PRECISION] == approx(1.0)
    if eval_type == ValidationMetricType.VOC:
        p = {st / 100.0: approx(1.0) if st <= 75 else -1.0 for st in range(100)}
        r = {st / 100.0: approx(1.0) if st <= 75 else 0.0 for st in range(100)}
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(1.0)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == p
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == r

        u = {st / 100.0: -1.0 for st in range(100)}
        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: u, RECALLS_PER_SCORE_THRESHOLD: u,
            },
            1: {
                AVERAGE_PRECISION: approx(1.0), PRECISION: approx(1.0), RECALL: approx(1.0),
                PRECISIONS_PER_SCORE_THRESHOLD: p, RECALLS_PER_SCORE_THRESHOLD: r,
            },
            2: {
                AVERAGE_PRECISION: -1.0, PRECISION: -1.0, RECALL: -1.0,
                PRECISIONS_PER_SCORE_THRESHOLD: u, RECALLS_PER_SCORE_THRESHOLD: u,
            },
        }

        assert metrics[IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS] == {
            PRECISION: approx(1.0), RECALL: approx(1.0), AVERAGE_PRECISION: approx(1.0)
        }

        cm1 = [[0, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0]]
        cm2 = [[0, 0, 0, 0], [0, 0, 0, 1], [0, 0, 0, 0]]
        assert metrics[CONFUSION_MATRICES_PER_SCORE_THRESHOLD] == {
            st: cm1 if st <= 0.7 else cm2
            for st in np.arange(0, 10) / 10.0
        }


@pytest.mark.parametrize("dataset_processing_type",
                         [DatasetProcessingType.IMAGES, DatasetProcessingType.IMAGES_AND_TILES])
@pytest.mark.parametrize("eval_type", [ValidationMetricType.VOC, ValidationMetricType.COCO])
def test_multi_image_three_gt_three_pred_single_match_masks(dataset_processing_type, eval_type):
    meta_info_per_image = [
        {"width": 640, "height": 640,
         "original_width": 640, "original_height": 640,
         "filename": "image_1.jpg", "areas": [60000],
         "iscrowd": np.array([False, False, False])},
        {"width": 640, "height": 640,
         "original_width": 640, "original_height": 640,
         "filename": "image_2.jpg", "areas": [60000],
         "iscrowd": np.array([False, False, False])},
        {"width": 640, "height": 640,
         "original_width": 640, "original_height": 640,
         "filename": "image_3.jpg", "areas": [60000],
         "iscrowd": np.array([False, False, False])},
    ]
    gt_objects_per_image = [
        # first image
        {
            "boxes": torch.tensor([[1, 0, 2, 100], [2, 0, 3, 100], [3, 0, 4, 100]], dtype=torch.float32),
            "masks": [
                get_mask_from_bbox([1, 0, 2, 100], 640, 640),
                get_mask_from_bbox([2, 0, 3, 100], 640, 640),
                get_mask_from_bbox([3, 0, 4, 100], 640, 640),
            ],
            "labels": torch.tensor([0, 1, 2]),
            "scores": None
        },
        # second image
        {
            "boxes": torch.tensor([[10, 0, 20, 100], [20, 0, 30, 100], [30, 0, 40, 100]], dtype=torch.float32),
            "masks": [
                get_mask_from_bbox([10, 0, 20, 100], 640, 640),
                get_mask_from_bbox([20, 0, 30, 100], 640, 640),
                get_mask_from_bbox([30, 0, 40, 100], 640, 640),
            ],
            "labels": torch.tensor([0, 1, 2]),
            "scores": None
        },
        # third image
        {
            "boxes": torch.tensor([[100, 0, 200, 100], [200, 0, 300, 100], [300, 0, 400, 100]], dtype=torch.float32),
            "masks": [
                get_mask_from_bbox([100, 0, 200, 100], 640, 640),
                get_mask_from_bbox([200, 0, 300, 100], 640, 640),
                get_mask_from_bbox([300, 0, 400, 100], 640, 640),
            ],
            "labels": torch.tensor([0, 1, 2]),
            "scores": None
        }
    ]
    predicted_objects_per_image = [
        # first image
        {
            "boxes": torch.tensor([[1, 0, 2, 100]], dtype=torch.float32),
            "masks": get_mask_from_bbox([1, 0, 2, 100], 640, 640),
            "labels": torch.tensor([0]),
            "scores": torch.tensor([0.5]),
            "filename": "image_1.jpg",
        },
        # second image
        {
            "boxes": torch.tensor([[20, 0, 30, 100]], dtype=torch.float32),
            "masks": get_mask_from_bbox([20, 0, 30, 100], 640, 640),
            "labels": torch.tensor([1]),
            "scores": torch.tensor([0.5]),
            "filename": "image_2.jpg",
        },
        # third image
        {
            "boxes": torch.tensor([[300, 0, 400, 100]], dtype=torch.float32),
            "masks": get_mask_from_bbox([300, 0, 400, 100], 640, 640),
            "labels": torch.tensor([2]),
            "scores": torch.tensor([0.5]),
            "filename": "image_3.jpg",
        }
    ]

    if eval_type == ValidationMetricType.COCO:
        dataset_items = [(None, gt, info) for gt, info in zip(gt_objects_per_image, meta_info_per_image)]
        dataset = ObjectDetectionDatasetMock(dataset_items, 3)
        dataset_wrapper = CommonObjectDetectionDatasetWrapper(dataset, DatasetProcessingType.IMAGES)
        val_index_map = dataset._classes
    else:
        dataset_wrapper = None
        val_index_map = ['1', '2', '3']

    training_settings_defaults['task_type'] = Tasks.IMAGE_INSTANCE_SEGMENTATION
    training_settings_defaults[TrainingLiterals.VALIDATION_METRIC_TYPE] = eval_type

    evaluator = ObjectDetectionInstanceSegmentationEvaluator(
        training_settings_defaults, class_names=val_index_map, dataset_processing_type=dataset_processing_type,
        dataset_wrapper=dataset_wrapper
    )

    evaluator.start_evaluation(enable=True)

    evaluator.evaluate_predictions(predictions_per_image=predicted_objects_per_image,
                                   image_infos=meta_info_per_image,
                                   targets_per_image=gt_objects_per_image)

    evaluator.finalize_evaluation()

    metrics = {}
    ive = evaluator.incremental_voc_evaluator if evaluator.eval_voc else None
    od_utils.compute_metrics(evaluator.eval_bounding_boxes,
                             evaluator.val_metric_type,
                             evaluator.coco_index, ive,
                             metrics, {},
                             evaluator.coco_metric_time, evaluator.voc_metric_time,
                             evaluator.primary_metric, is_train=False)

    _13 = 1.0 / 3.0
    assert metrics[MEAN_AVERAGE_PRECISION] == approx(_13, rel=1e-2)
    if eval_type == ValidationMetricType.VOC:
        p = {st / 100.0: approx(1.0) if st <= 50 else -1.0 for st in range(100)}
        r = {st / 100.0: approx(_13, abs=1e-5) if st <= 50 else 0.0 for st in range(100)}
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(_13, abs=1e-5)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == p
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == r

        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: approx(_13, abs=1e-5), PRECISION: approx(1.0), RECALL: approx(_13, abs=1e-5),
                PRECISIONS_PER_SCORE_THRESHOLD: p, RECALLS_PER_SCORE_THRESHOLD: r,
            },
            1: {
                AVERAGE_PRECISION: approx(_13, abs=1e-5), PRECISION: approx(1.0), RECALL: approx(_13, abs=1e-5),
                PRECISIONS_PER_SCORE_THRESHOLD: p, RECALLS_PER_SCORE_THRESHOLD: r,
            },
            2: {
                AVERAGE_PRECISION: approx(_13, abs=1e-5), PRECISION: approx(1.0), RECALL: approx(_13, abs=1e-5),
                PRECISIONS_PER_SCORE_THRESHOLD: p, RECALLS_PER_SCORE_THRESHOLD: r,
            },
        }

        assert IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS not in metrics
        assert CONFUSION_MATRICES_PER_SCORE_THRESHOLD not in metrics


@pytest.mark.parametrize("dataset_processing_type",
                         [DatasetProcessingType.IMAGES, DatasetProcessingType.IMAGES_AND_TILES])
@pytest.mark.parametrize("yolo", [True, False])
@pytest.mark.parametrize("eval_type", [ValidationMetricType.VOC, ValidationMetricType.COCO])
def test_multi_image_three_gt_three_pred_single_match_boxes_batchwise(dataset_processing_type, yolo, eval_type):
    meta_info_per_image = [
        {"width": 640, "height": 640,
         "original_width": 640, "original_height": 640,
         "filename": "image_1.jpg", "areas": [60000],
         "iscrowd": np.array([False, False, False])},
        {"width": 640, "height": 640,
         "original_width": 640, "original_height": 640,
         "filename": "image_2.jpg", "areas": [60000],
         "iscrowd": np.array([False, False, False])},
        {"width": 640, "height": 640,
         "original_width": 640, "original_height": 640,
         "filename": "image_3.jpg", "areas": [60000],
         "iscrowd": np.array([False, False, False])},
    ]
    gt_objects_per_image = [
        # first image
        {
            "boxes": torch.tensor([[1, 0, 2, 100], [2, 0, 3, 100], [3, 0, 4, 100]], dtype=torch.float32),
            "labels": torch.tensor([0, 1, 2]),
            "scores": None
        },
        # second image
        {
            "boxes": torch.tensor([[10, 0, 20, 100], [20, 0, 30, 100], [30, 0, 40, 100]], dtype=torch.float32),
            "labels": torch.tensor([0, 1, 2]),
            "scores": None
        },
        # third image
        {
            "boxes": torch.tensor([[100, 0, 200, 100], [200, 0, 300, 100], [300, 0, 400, 100]], dtype=torch.float32),
            "labels": torch.tensor([0, 1, 2]),
            "scores": None
        }
    ]
    predicted_objects_per_image = [
        # first image
        {
            "boxes": torch.tensor([[1, 0, 2, 100]], dtype=torch.float32),
            "labels": torch.tensor([0]),
            "scores": torch.tensor([0.5]),
            "filename": "image_1.jpg",
        },
        # second image
        {
            "boxes": torch.tensor([[20, 0, 30, 100]], dtype=torch.float32),
            "labels": torch.tensor([1]),
            "scores": torch.tensor([0.5]),
            "filename": "image_2.jpg",
        },
        # third image
        {
            "boxes": torch.tensor([[300, 0, 400, 100]], dtype=torch.float32),
            "labels": torch.tensor([2]),
            "scores": torch.tensor([0.5]),
            "filename": "image_3.jpg",
        }
    ]
    if eval_type == ValidationMetricType.COCO:
        dataset_items = [(None, gt, info) for gt, info in zip(gt_objects_per_image, meta_info_per_image)]
        dataset = ObjectDetectionDatasetMock(dataset_items, 3)
        dataset_wrapper = CommonObjectDetectionDatasetWrapper(dataset, DatasetProcessingType.IMAGES)
        val_index_map = dataset._classes
    else:
        dataset_wrapper = None
        val_index_map = ['1', '2', '3']

    training_settings_defaults['task_type'] = Tasks.IMAGE_OBJECT_DETECTION
    training_settings_defaults[TrainingLiterals.VALIDATION_METRIC_TYPE] = eval_type

    if yolo:
        evaluator = YoloEvaluator(training_settings_defaults, class_names=val_index_map,
                                  dataset_processing_type=dataset_processing_type,
                                  dataset_wrapper=dataset_wrapper)
    else:
        evaluator = ObjectDetectionInstanceSegmentationEvaluator(
            training_settings_defaults, class_names=val_index_map, dataset_processing_type=dataset_processing_type,
            dataset_wrapper=dataset_wrapper
        )

    evaluator.start_evaluation(enable=True)

    for pred, info, target in \
            zip(predicted_objects_per_image, meta_info_per_image, gt_objects_per_image):

        pred, target, info = [pred], [target], [info]
        if yolo:
            pred, target = \
                convert_to_yolo_format(pred, target, info)
        evaluator.evaluate_predictions(predictions_per_image=pred,
                                       image_infos=info,
                                       targets_per_image=target)

    evaluator.finalize_evaluation()

    ive = evaluator.incremental_voc_evaluator if evaluator.eval_voc else None
    metrics = {}
    od_utils.compute_metrics(evaluator.eval_bounding_boxes,
                             evaluator.val_metric_type,
                             evaluator.coco_index, ive,
                             metrics, {},
                             evaluator.coco_metric_time, evaluator.voc_metric_time,
                             evaluator.primary_metric, is_train=False)

    _13 = 1.0 / 3.0
    assert metrics[MEAN_AVERAGE_PRECISION] == approx(_13, rel=1e-2)
    if eval_type == ValidationMetricType.VOC:
        p = {st / 100.0: approx(1.0) if st <= 50 else -1.0 for st in range(100)}
        r = {st / 100.0: approx(_13, abs=1e-5) if st <= 50 else 0.0 for st in range(100)}
        assert metrics[PRECISION] == approx(1.0)
        assert metrics[RECALL] == approx(_13, abs=1e-5)
        assert metrics[PRECISIONS_PER_SCORE_THRESHOLD] == p
        assert metrics[RECALLS_PER_SCORE_THRESHOLD] == r

        assert metrics[PER_LABEL_METRICS] == {
            0: {
                AVERAGE_PRECISION: approx(_13, abs=1e-5), PRECISION: approx(1.0), RECALL: approx(_13, abs=1e-5),
                PRECISIONS_PER_SCORE_THRESHOLD: p, RECALLS_PER_SCORE_THRESHOLD: r,
            },
            1: {
                AVERAGE_PRECISION: approx(_13, abs=1e-5), PRECISION: approx(1.0), RECALL: approx(_13, abs=1e-5),
                PRECISIONS_PER_SCORE_THRESHOLD: p, RECALLS_PER_SCORE_THRESHOLD: r,
            },
            2: {
                AVERAGE_PRECISION: approx(_13, abs=1e-5), PRECISION: approx(1.0), RECALL: approx(_13, abs=1e-5),
                PRECISIONS_PER_SCORE_THRESHOLD: p, RECALLS_PER_SCORE_THRESHOLD: r,
            },
        }

        assert metrics[IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS] == {
            PRECISION: approx(1.0), RECALL: approx(1.0), AVERAGE_PRECISION: approx(1.0)
        }

        cm1 = [[1, 0, 0, 2], [0, 1, 0, 2], [0, 0, 1, 2]]
        cm2 = [[0, 0, 0, 3], [0, 0, 0, 3], [0, 0, 0, 3]]
        assert metrics[CONFUSION_MATRICES_PER_SCORE_THRESHOLD] == {
            st: cm1 if st <= 0.5 else cm2
            for st in np.arange(0, 10) / 10.0
        }
