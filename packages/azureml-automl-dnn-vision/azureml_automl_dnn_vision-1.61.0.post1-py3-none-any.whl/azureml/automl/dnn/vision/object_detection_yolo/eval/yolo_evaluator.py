# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Yolo Object detection and evaluation helper """

import numpy as np

import torch

from azureml.automl.dnn.vision.object_detection.eval.object_detection_instance_segmentation_evaluator import \
    ObjectDetectionInstanceSegmentationEvaluator
from azureml.automl.dnn.vision.object_detection_yolo.common.constants import YoloLiterals
from azureml.automl.dnn.vision.object_detection_yolo.utils.utils import unpad_bbox, xywh2xyxy


class YoloEvaluator(ObjectDetectionInstanceSegmentationEvaluator):
    """ Yolo evaluation helper"""
    def __init__(self, settings, class_names, dataset_processing_type, dataset_wrapper=None) -> None:
        """
        :param settings: Dictionary with all training and model settings
        :type settings: dict
        :param class_names: Map from numerical indices to class names
        :type class_names: List of strings
        :param dataset_processing_type: Type of processing done in dataset (eg tiling)
        :type dataset_processing_type: class DatasetProcessingType
        :param dataset_wrapper: Dataset for evaluations
        :type dataset_wrapper: class CommonObjectDetectionDatasetWrapper
        """

        self.conf_thres = settings.get(YoloLiterals.BOX_SCORE_THRESH, None)
        self.nms_iou_threshold = settings.get(YoloLiterals.NMS_IOU_THRESH, None)
        super().__init__(settings, class_names, dataset_processing_type, dataset_wrapper=dataset_wrapper)

    def _create_predictions_with_info_for_tile_grouping(self, predictions, image_info):
        predictions_with_info = {}

        # Add the image info fields.
        predictions_with_info.update(image_info)

        # Move predictions to cpu to save gpu memory.
        predictions = predictions.detach().cpu() if predictions is not None else None

        # pad is only set in eval mode. when evaluating predictions of training data pad is not set.
        if "pad" not in image_info:
            image_info["pad"] = (0, 0)

        # Unpad the bounding boxes in place and update the image width and height fields.
        height, width = unpad_bbox(predictions[:, :4] if predictions is not None else None,
                                   (image_info["height"], image_info["width"]), image_info["pad"])
        predictions_with_info["height"] = height
        predictions_with_info["width"] = width

        # Set the boxes, labels and scores fields.
        if predictions is not None:
            predictions_with_info["boxes"] = predictions[:, :4]
            predictions_with_info["labels"] = predictions[:, 5].to(dtype=torch.long)
            predictions_with_info["scores"] = predictions[:, 4]
        else:
            predictions_with_info["boxes"] = torch.empty(0, 4, dtype=torch.float, device="cpu")
            predictions_with_info["labels"] = torch.empty(0, dtype=torch.long, device="cpu")
            predictions_with_info["scores"] = torch.empty(0, dtype=torch.float, device="cpu")

        return predictions_with_info

    def _convert_targets_to_objects_per_image(self, targets_per_image, image_infos):
        gt_objects_per_image = []

        # Go through the images and convert boxes/masks, labels and scores to format consumed by incremental evaluator.
        for i in range(len(image_infos)):
            # Get the targets for the current image.
            targets = targets_per_image[i]

            # pad is only set in eval mode. when evaluating predictions of training data pad is not set.
            if "pad" not in image_infos[i]:
                image_infos[i]["pad"] = (0, 0)

            # Get boxes and convert to pixel x1, y1, x2, y2 format.
            width, height = image_infos[i]["width"], image_infos[i]["height"]
            boxes = xywh2xyxy(targets[:, 2:]) * np.array([[width, height, width, height]])
            unpad_bbox(boxes, (height, width), (image_infos[i]["pad"]))

            # Get classes.
            classes = targets[:, 1]

            # Ground truth objects have boxes and classes only.
            gt_objects = {"boxes": boxes, "masks": None, "classes": classes, "scores": None}
            gt_objects_per_image.append(gt_objects)

        return gt_objects_per_image
