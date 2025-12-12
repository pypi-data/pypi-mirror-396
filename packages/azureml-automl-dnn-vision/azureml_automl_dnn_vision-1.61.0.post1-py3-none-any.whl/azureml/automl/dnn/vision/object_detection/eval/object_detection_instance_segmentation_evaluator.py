# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Object detection and segmentation evaluation helper """

import copy

import torch

from typing import Dict, List, Optional, Union

from azureml.automl.core.shared.constants import Tasks
from azureml.automl.dnn.vision.common import distributed_utils
from azureml.automl.dnn.vision.common.average_meter import AverageMeter
from azureml.automl.dnn.vision.common.constants import SettingsLiterals as CommonSettingsLiterals, \
    TrainingLiterals as CommonTrainingLiterals, LogParamsType
from azureml.automl.dnn.vision.object_detection.common import masktools
from azureml.automl.dnn.vision.object_detection.common.coco_eval_box_converter import COCOEvalBoxConverter
from azureml.automl.dnn.vision.object_detection.common.constants import ValidationMetricType, \
    TrainingLiterals, TilingLiterals
from azureml.automl.dnn.vision.object_detection.common.tiling_helper import SameImageTilesVisitor
from azureml.automl.dnn.vision.object_detection.data.dataset_wrappers import DatasetProcessingType
from azureml.automl.dnn.vision.object_detection.eval import cocotools
from azureml.automl.dnn.vision.object_detection.eval.incremental_voc_evaluator import IncrementalVocEvaluator


class ObjectDetectionInstanceSegmentationEvaluator:
    """Object detection and instance segmentation evaluator.

    Evaluates the predictions of an object detection or an instance segmentation model on a dataset with ground truth.
    Can be configured to compute COCO-style or VOC-style metrics.

    Typical usage:

        evaluator = ObjectDetectionInstanceSegmentationEvaluator(
            settings, class_names, dataset_processing_type, dataset_wrapper
        )

        evaluator.start_evaluation(enable=True)

        for each batch
            evaluator.evaluate_predictions(predictions_in_batch, image_infos_in_batch, targets_in_batch)

        evaluator.finalize_evaluation()

        map_score = object_detection_utils.compute_metrics(evaluator.eval_bounding_boxes, ...)

    """

    def __init__(self, settings, class_names, dataset_processing_type, dataset_wrapper=None) -> None:
        """
        :param settings: Dictionary with all training and model settings
        :type settings: dict
        :param class_names: Map from numerical indices to class names
        :type class_names: List of strings
        :param dataset_processing_type: Type of processing done in dataset (eg tiling)
        :type dataset_processing_type: DatasetProcessingType
        :param dataset_wrapper: Dataset for evaluations
        :type dataset_wrapper: CommonObjectDetectionDatasetWrapper
        """

        # Copy the relevant parameters from the global settings.
        self.task_type = settings[CommonSettingsLiterals.TASK_TYPE]
        self.primary_metric = settings[CommonTrainingLiterals.PRIMARY_METRIC]
        self.val_metric_type = settings[TrainingLiterals.VALIDATION_METRIC_TYPE]
        self.val_iou_threshold = settings[TrainingLiterals.VALIDATION_IOU_THRESHOLD]
        self.tile_predictions_nms_thresh = settings[TilingLiterals.TILE_PREDICTIONS_NMS_THRESH]
        self.log_validation_loss = settings.get(CommonSettingsLiterals.LOG_VALIDATION_LOSS,
                                                LogParamsType.ENABLE) == LogParamsType.ENABLE

        # Copy class names and type of processing performed in the dataset class (eg tiling).
        self.class_names = class_names
        self.dataset_processing_type = dataset_processing_type

        # Turn off evaluation by default.
        self.enabled = False

        # Toggle the COCO-style and VOC-style evaluation according to the validation metric type provided by the user.
        # Note that the user may specify running one of, both or none of COCO-style and VOC-style evaluation.
        self.eval_coco = self.val_metric_type in ValidationMetricType.ALL_COCO
        self.eval_voc = self.val_metric_type in ValidationMetricType.ALL_VOC

        # Set up internal evaluation objects used for all evaluation runs.
        self.coco_index = cocotools.create_coco_index(dataset_wrapper) if self.eval_coco else None

        # Initialize the timers for COCO-style evaluation, VOC-style evaluation and tiling operations.
        self.coco_metric_time = AverageMeter()
        self.voc_metric_time = AverageMeter()
        self.tiling_merge_predictions_time = AverageMeter()
        self.tiling_nms_time = AverageMeter()

        # Initialize mechanism to group together the tiled targets and predictions for an image.
        self.tiling_visitor = SameImageTilesVisitor(
            self._do_evaluation_step, self.tile_predictions_nms_thresh,
            self.tiling_merge_predictions_time, self.tiling_nms_time
        )

        # Figure out if we're runing in a distributed context.
        self.distributed = distributed_utils.dist_available_and_initialized()

    def start_evaluation(self, enable: bool) -> None:
        """Start an evaluation run.

        Sets up internal evaluation objects specific to the current run.

        :param enable: Whether evaluation is enabled
        :type enable: bool
        """

        self.enabled = enable
        if self.enabled:
            if self.eval_voc:
                self.incremental_voc_evaluator = IncrementalVocEvaluator(
                    self.task_type == Tasks.IMAGE_OBJECT_DETECTION, len(self.class_names), self.val_iou_threshold
                )
                self.incremental_voc_evaluator_local: Optional[IncrementalVocEvaluator] = None

            if self.eval_coco:
                self.coco_eval_box_converter = COCOEvalBoxConverter(self.class_names)

    def evaluate_predictions(self, predictions_per_image: Union[List[Dict], List[torch.tensor]],
                             image_infos: List[Dict],
                             targets_per_image: List[Dict]) -> None:
        """Evaluate the predictions for a set of images with ground truth.

        predictions_per_image:
        example for object detection:
            [{
                "boxes": torch.tensor([[1, 0, 2, 100]], dtype=torch.float32),
                "labels": torch.tensor([0]),
                "scores": torch.tensor([0.5]),
                "filename": "image_1.jpg",
            },]
        example for yolo:
            [torch.tensor with shape: nx6 (x, y, w, h, conf, cls)]]
            x,y,w,h should be normalized coefficients.
        example for instance segmentation:
        [{
                "boxes": torch.tensor([[1, 0, 2, 100]], dtype=torch.float32),
                "masks": torch.Size([1, height, width]),
                "labels": torch.tensor([0]),
                "scores": torch.tensor([0.5]),
                "filename": "image_1.jpg",
            },]

        image_infos:
        example:
            [{
                "width": 640, "height": 640,
                "original_width": 640, "original_height": 640,
                "filename": "image_1.jpg", "areas": [60000],
                "iscrowd": np.array([False, False, False])
            },]
        targets_per_image:
        example for object detection and yolo:
                [ {
                    "boxes": torch.tensor([[1, 0, 2, 100]], dtype=torch.float32),
                    "labels": torch.tensor([0]),
                    "scores": None,
                },]
        example for instance segmentation:
                [ {
                    "boxes": torch.tensor([[1, 0, 2, 100]], dtype=torch.float32),
                    "masks": torch.Size([1, height, width]),
                    "labels": torch.tensor([0]),
                    "scores": None,
                },]

        :param predictions_per_image: Predicted info for each image
        :type:  Union[list of dict, list of torch.tensors]
        :param image_infos: Meta information for each image.
        :type: list of dict
        :param targets_per_image: Ground truth objects for each image.
        :type: list of dict
        """

        if self.enabled:
            # If VOC-style evaluation, then initialize the local copy of the incremental VOC evaluator the first time
            # `evaluate_predictions()` is called.
            if self.eval_voc and (self.incremental_voc_evaluator_local is None):
                # If distributed computation, make copy of original evaluator; otherwise, use original evaluator.
                self.incremental_voc_evaluator_local = copy.deepcopy(self.incremental_voc_evaluator) \
                    if self.distributed else self.incremental_voc_evaluator

            # Convert predictions to format suitable for tile grouping.
            predictions_with_info_per_image = [
                self._create_predictions_with_info_for_tile_grouping(predictions, image_info)
                for predictions, image_info in zip(predictions_per_image, image_infos)
            ]

            if self.dataset_processing_type == DatasetProcessingType.IMAGES_AND_TILES:
                # Feed targets and predictions to the tiling visitor, which will group by image and run evaluation.
                self.tiling_visitor.visit_batch(targets_per_image, predictions_with_info_per_image, image_infos)
            else:
                # Evaluate current batch.
                self._do_evaluation_step(targets_per_image, predictions_with_info_per_image, image_infos)

    def finalize_evaluation(self) -> None:
        """End the current evaluation run, storing results."""

        if self.enabled:
            if self.dataset_processing_type == DatasetProcessingType.IMAGES_AND_TILES:
                # Do evaluation for the tiles of the last image.
                self.tiling_visitor.finalize()

            # Initialize the bounding boxes for COCO-style evaluation to empty.
            eval_bounding_boxes = []

            # If required, convert predicted boxes to format used in COCO-style evaluation.
            if self.eval_coco:
                eval_bounding_boxes = self.coco_eval_box_converter.get_boxes()

            # If distributed computation, aggregate evaluation data.
            if self.distributed:
                if self.eval_coco:
                    # Gather eval bounding boxes from all processes.
                    eval_bounding_boxes_list = distributed_utils.all_gather(eval_bounding_boxes)
                    eval_bounding_boxes = COCOEvalBoxConverter.aggregate_boxes(eval_bounding_boxes_list)

                # Aggregate the partial results of all evaluators and save them in the main evaluator.
                if self.eval_voc and (self.incremental_voc_evaluator_local is not None):
                    # Flush the GPU cache so we use as much GPU memory as possible for broadcasting partial results.
                    torch.cuda.empty_cache()

                    # Broadcast partial results of all evaluators to all evaluators. Ensure size of data structure
                    # holding partial results is minimized, as broadcasting uses GPU memory.
                    self.incremental_voc_evaluator_local.optimize_serialized_size()
                    incremental_voc_evaluators = distributed_utils.all_gather(self.incremental_voc_evaluator_local)

                    # Aggregate the partial results and save them.
                    self.incremental_voc_evaluator.set_from_others(incremental_voc_evaluators)

            self.eval_bounding_boxes = eval_bounding_boxes

        else:
            self.eval_bounding_boxes = []

    def _do_evaluation_step(self, targets_per_image, predictions_with_info_per_image, image_infos):
        # Convert labels and predictions to input format of incremental evaluator.
        gt_objects_per_image = self._convert_targets_to_objects_per_image(targets_per_image, image_infos)
        predicted_objects_per_image = self._convert_predictions_to_objects_per_image(
            predictions_with_info_per_image)

        # If required, save the current batch of predictions. The COCO-style evaluation code needs all the predictions
        # for a dataset.
        if self.eval_coco:
            self.coco_eval_box_converter.add_predictions(predictions_with_info_per_image)

        # If required, run the incremental VOC evaluator on the current batch of labels and predictions. Unlike for the
        # COCO-style evaluation code, there is no need to save the current predictions.
        if self.eval_voc and (self.incremental_voc_evaluator_local is not None):
            self.incremental_voc_evaluator_local.evaluate_batch(
                gt_objects_per_image, predicted_objects_per_image, image_infos
            )

    def _create_predictions_with_info_for_tile_grouping(self, predictions, image_info):
        predictions_with_info = {}
        predictions_with_info.update(image_info)
        predictions_with_info.update(predictions)

        # move predicted labels to cpu to save gpu memory
        predictions_with_info["boxes"] = predictions_with_info["boxes"].detach().cpu()
        predictions_with_info["labels"] = predictions_with_info["labels"].detach().cpu()
        predictions_with_info["scores"] = predictions_with_info["scores"].detach().cpu()

        # encode masks as rle to save memory
        masks = predictions_with_info.get("masks", None)
        if masks is not None:
            masks = masks.detach().cpu()
            masks = (masks > 0.5)
            rle_masks = []
            for mask in masks:
                rle = masktools.encode_mask_as_rle(mask)
                rle_masks.append(rle)
            predictions_with_info["masks"] = rle_masks

        return predictions_with_info

    def _convert_targets_to_objects_per_image(self, targets_per_image, image_infos):
        # Note: image_infos is needed in inherited class YoloEvaluator
        gt_objects_per_image = [
            {
                "boxes": targets["boxes"].detach().cpu().numpy(),
                "masks": [
                    masktools.encode_mask_as_rle(mask.detach().cpu()) for mask in targets["masks"]
                ] if "masks" in targets else None,
                "classes": targets["labels"].detach().cpu().numpy(),
                "scores": None
            }
            for targets in targets_per_image
        ]

        return gt_objects_per_image

    def _convert_predictions_to_objects_per_image(self, predictions_with_info_per_image):
        # Go through the images and convert the boxes, labels and scores to format consumed by incremental evaluator.
        predicted_objects_per_image = [
            {
                "boxes": predictions["boxes"].numpy(), "masks": predictions.get("masks", None),
                "classes": predictions["labels"].numpy(),
                "scores": predictions["scores"].numpy()
            }
            for predictions in predictions_with_info_per_image
        ]
        return predicted_objects_per_image
