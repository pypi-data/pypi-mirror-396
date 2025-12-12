# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Classes that wrap training steps"""
import copy
import gc
import os
import time
import torch
from typing import Any, cast, Dict, List

from azureml.automl.dnn.vision.common import distributed_utils, utils
from azureml.automl.dnn.vision.common.artifacts_utils import save_model_checkpoint, write_artifacts, \
    upload_model_checkpoint
from azureml.automl.dnn.vision.common.average_meter import AverageMeter
from azureml.automl.dnn.vision.common.constants import ArtifactLiterals, SettingsLiterals as CommonSettingsLiterals, \
    TrainingLiterals as CommonTrainingLiterals, LogParamsType
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionSystemException, AutoMLVisionRuntimeUserException
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.system_meter import SystemMeter
from azureml.automl.dnn.vision.common.trainer.lrschedule import LRSchedulerUpdateType
from azureml.automl.dnn.vision.object_detection.common.constants import ValidationMetricType, \
    TrainingLiterals
from azureml.automl.dnn.vision.object_detection.common.object_detection_utils import compute_metrics, \
    write_per_label_metrics_file
from azureml.automl.dnn.vision.object_detection.data.dataset_wrappers import DatasetProcessingType
from azureml.automl.dnn.vision.object_detection.eval.object_detection_instance_segmentation_evaluator import \
    ObjectDetectionInstanceSegmentationEvaluator
from azureml.automl.dnn.vision.object_detection.writers.score_script_utils import write_scoring_script
from azureml.automl.runtime.shared.score import constants as scoring_constants
from contextlib import nullcontext
from torch import Tensor


logger = get_logger(__name__)


def move_images_to_device(images: List[Tensor], device: torch.device) -> List[Tensor]:
    """Convenience function to move images to device (gpu/cpu).

    :param images: Batch of images
    :type images: Pytorch tensor
    :param device: Target device
    :type device: torch.device
    :return: Batch of images moved to the device
    :rtype: List[Tensor]
    """

    return [image.to(device) for image in images]


def move_targets_to_device(targets, device: torch.device):
    """Convenience function to move training targets to device (gpu/cpu)

    :param targets: Batch Training targets (bounding boxes and classes)
    :type targets: Dictionary
    :param device: Target device
    :type device: torch.device
    """

    return [{k: v.to(device) for k, v in target.items()} for
            target in targets]


def train_one_epoch(model, optimizer, scheduler, train_data_loader,
                    device, criterion, epoch, print_freq, system_meter, distributed, grad_accum_steps,
                    grad_clip_type: str, evaluator: ObjectDetectionInstanceSegmentationEvaluator):
    """Train a model for one epoch

    :param model: Model to be trained
    :type model: Pytorch nn.Module
    :param optimizer: Optimizer used in training
    :type optimizer: Pytorch optimizer
    :param scheduler: Learning Rate Scheduler wrapper
    :type scheduler: BaseLRSchedulerWrapper (see common.trainer.lrschedule)
    :param train_data_loader: Data loader for training data
    :type train_data_loader: Pytorch data loader
    :param device: Target device
    :type device: Pytorch device
    :param criterion: Loss function wrapper
    :type criterion: Object derived from BaseCriterionWrapper (see object_detection.train.criterion)
    :param epoch: Current training epoch
    :type epoch: int
    :param print_freq: How often you want to print the output
    :type print_freq: int
    :param system_meter: A SystemMeter to collect system properties
    :type system_meter: SystemMeter
    :param distributed: Training in distributed mode or not
    :type distributed: bool
    :param grad_accum_steps: gradient accumulation steps which is used to accumulate the gradients of those steps
     without updating model variables/weights
    :type grad_accum_steps: int
    :param clip_type: The type of gradient clipping. See GradClipType
    :type grad_clip_type: str
    :param evaluator: evaluation helper
    :type evalator: ObjectDetectionInstanceSegmentationEvaluator
    """

    batch_time = AverageMeter()
    data_time = AverageMeter()
    losses = AverageMeter()

    model.train()

    # grad_accum_steps should be positive, smaller or equal than the number of batches per epoch
    grad_accum_steps = min(len(train_data_loader), max(grad_accum_steps, 1))
    logger.info("[grad_accumulation_step: {}]".format(grad_accum_steps))
    optimizer.zero_grad()

    end = time.time()
    uneven_batches_context_manager = model.join() if distributed else nullcontext()

    with uneven_batches_context_manager:
        for i, (images, targets, info) in enumerate(utils._data_exception_safe_iterator(iter(train_data_loader))):
            # measure data loading time
            data_time.update(time.time() - end)

            images = move_images_to_device(images, device)
            targets = move_targets_to_device(targets, device)

            loss_dict = criterion.evaluate(model, images, targets)
            loss = sum(loss_dict.values())
            loss /= grad_accum_steps
            loss = cast(Tensor, loss)
            loss_value = loss.item()

            # raise an UserException if loss is too big
            utils.check_loss_explosion(loss_value)
            loss.backward()

            # evaluate metics on this batch if eval_training_metrics is set.
            if evaluator.enabled:
                model.eval()
                with torch.no_grad():
                    predictions_per_image = model(images)
                    evaluator.evaluate_predictions(predictions_per_image, info, targets)
                model.train()

            if (i + 1) % grad_accum_steps == 0 or i == len(train_data_loader) - 1:
                # gradient clipping
                utils.clip_gradient(model.parameters(), grad_clip_type)
                optimizer.step()
                optimizer.zero_grad()

            if scheduler.update_type == LRSchedulerUpdateType.BATCH:
                scheduler.lr_scheduler.step()

            # record loss and measure elapsed time
            losses.update(loss_value, len(images))
            batch_time.update(time.time() - end)
            end = time.time()

            # delete tensors which have a valid grad_fn
            del loss, loss_dict

            if i % print_freq == 0 or i == len(train_data_loader) - 1:
                mesg = "Epoch: [{0}][{1}/{2}]\t" "lr: {3}\t" "Time {batch_time.value:.4f} ({batch_time.avg:.4f})\t"\
                       "Data {data_time.value:.4f} ({data_time.avg:.4f})\t" "Loss {loss.value:.4f} " \
                       "({loss.avg:.4f})".format(epoch, i, len(train_data_loader), optimizer.param_groups[0]["lr"],
                                                 batch_time=batch_time, data_time=data_time, loss=losses)
                logger.info(mesg)

                system_meter.log_system_stats()

    if scheduler.update_type == LRSchedulerUpdateType.EPOCH:
        scheduler.lr_scheduler.step()

    evaluator.finalize_evaluation()

    return losses.avg


def validate(
    model, val_data_loader, device, system_meter, distributed, evaluator: ObjectDetectionInstanceSegmentationEvaluator
):
    """Gets predictions on validation set, evaluating incrementally if required.

    :param model: Model to score
    :type model: Pytorch nn.Module
    :param val_data_loader: Data loader for validation data
    :type val_data_loader: Pytorch Data Loader
    :param device: Target device
    :type device: Pytorch device
    :param system_meter: A SystemMeter to collect system properties
    :type system_meter: SystemMeter
    :param distributed: Training in distributed mode or not
    :type distributed: bool
    :param evaluator: evaluation helper
    :type evalator: ObjectDetectionInstanceSegmentationEvaluator
    :returns: List of detections and avg_loss
    :rtype: List of ImageBoxes (see object_detection.common.boundingbox) and a float
    """
    # to record loss and measure elapsed time
    batch_time = AverageMeter()
    losses = AverageMeter()

    # Prepare the model for inference.
    model.eval()
    # We have observed that pytorch DDP does some AllReduce calls during eval model as well.
    # When there are uneven number of batches across worker processes, there is issue with mismatch
    # of distributed calls between processes and it leads to blocked processes and hangs.
    # Using the pytorch model instead of DDP model to run validation to avoid sync calls during eval.
    # One other observation is that AllReduce calls from DDP are only seen when we use .join() during
    # training phase.
    base_torch_model = model.module if distributed else model

    end = time.time()
    with torch.no_grad():
        for i, (images, targets_per_image, image_infos) in enumerate(
            utils._data_exception_safe_iterator(iter(val_data_loader))
        ):

            images = move_images_to_device(images, device)
            targets_per_image = move_targets_to_device(targets_per_image, device)

            # Compute model predictions for the current batch of images.
            predictions_per_image = base_torch_model(images)

            # Compute loss for the current batch of images.
            # loss is computed when log_validation_loss is set to True, to reduce the switching
            # b/w eval and train mode
            if evaluator.log_validation_loss:
                model.train()
                loss_dict = base_torch_model(images, targets_per_image)
                loss = sum(loss_dict.values())
                loss = cast(Tensor, loss)
                loss_value = loss.item()
                losses.update(loss_value, len(images))
                model.eval()

            evaluator.evaluate_predictions(predictions_per_image, image_infos, targets_per_image)

            # measure elapsed time
            batch_time.update(time.time() - end)
            end = time.time()

            if i % 100 == 0 or i == len(val_data_loader) - 1:
                mesg = "Test: [{0}/{1}]\t" \
                       "Time {batch_time.value:.4f} ({batch_time.avg:.4f})".format(i, len(val_data_loader),
                                                                                   batch_time=batch_time)
                logger.info(mesg)

                system_meter.log_system_stats()

    evaluator.finalize_evaluation()

    return losses.avg


def train(model, optimizer, scheduler, train_data_loader, val_data_loader,
          criterion, device, settings, training_state, output_dir=None, azureml_run=None):
    """Train a model

    :param model: Model to train
    :type model: Object derived from BaseObjectDetectionModelWrapper (see object_detection.models.base_model_wrapper)
    :param optimizer: Model Optimizer
    :type optimizer: Pytorch Optimizer
    :param scheduler: Learning Rate Scheduler wrapper.
    :type scheduler: BaseLRSchedulerWrapper (see common.trainer.lrschedule)
    :param train_data_loader: Data loader with training data
    :type train_data_loader: Pytorch data loader
    :param val_data_loader: Data loader with validation data.
    :type val_data_loader: Pytorch data loader
    :param criterion: Loss function
    :type criterion: Object derived from CommonCriterionWrapper (see object_detection.train.criterion)
    :param device: Target device (gpu/cpu)
    :type device: Pytorch Device
    :param settings: dictionary containing settings for training
    :type settings: dict
    :param training_state: Training state
    :type training_state: ODTrainingState
    :param output_dir: Output directory to write checkpoints to
    :type output_dir: str
    :param azureml_run: azureml run object
    :type azureml_run: azureml.core.run.Run
    :returns: Trained model
    :rtype: Object derived from CommonObjectDetectionModelWrapper
    """

    epoch_time = AverageMeter()

    # Extract relevant parameters from training settings
    task_type = settings[CommonSettingsLiterals.TASK_TYPE]
    val_index_map = model.classes
    val_metric_type = settings[TrainingLiterals.VALIDATION_METRIC_TYPE]
    number_of_epochs = settings[CommonTrainingLiterals.NUMBER_OF_EPOCHS]
    enable_onnx_norm = settings[CommonSettingsLiterals.ENABLE_ONNX_NORMALIZATION]
    log_verbose_metrics = settings.get(CommonSettingsLiterals.LOG_VERBOSE_METRICS, False)
    log_training_metrics = settings.get(CommonSettingsLiterals.LOG_TRAINING_METRICS,
                                        LogParamsType.DISABLE) == LogParamsType.ENABLE
    log_validation_loss = settings.get(CommonSettingsLiterals.LOG_VALIDATION_LOSS,
                                       LogParamsType.ENABLE) == LogParamsType.ENABLE
    is_enabled_early_stopping = settings[CommonTrainingLiterals.EARLY_STOPPING]
    early_stopping_patience = settings[CommonTrainingLiterals.EARLY_STOPPING_PATIENCE]
    early_stopping_delay = settings[CommonTrainingLiterals.EARLY_STOPPING_DELAY]
    eval_freq = settings[CommonTrainingLiterals.EVALUATION_FREQUENCY]
    checkpoint_freq = settings.get(CommonTrainingLiterals.CHECKPOINT_FREQUENCY, None)
    grad_accum_steps = settings[CommonTrainingLiterals.GRAD_ACCUMULATION_STEP]
    grad_clip_type = settings[CommonTrainingLiterals.GRAD_CLIP_TYPE]
    save_as_mlflow = settings[CommonSettingsLiterals.SAVE_MLFLOW]

    training_dataset_processing_type = train_data_loader.dataset.dataset_processing_type
    if log_training_metrics and training_dataset_processing_type == DatasetProcessingType.IMAGES_AND_TILES:
        log_training_metrics = False
        logger.warning("Training Metrics won't be computed when \
                        small object detection is enabled by setting tile_grid_size parameter")

    val_index_map = model.classes
    base_model = model.model

    distributed = distributed_utils.dist_available_and_initialized()
    master_process = distributed_utils.master_process()

    best_model_wts = training_state.best_model_wts if training_state.best_model_wts is not None else \
        copy.deepcopy(model.state_dict())
    best_score = training_state.best_score
    best_epoch = training_state.best_epoch
    no_progress_counter = training_state.no_progress_counter
    best_model_metrics = training_state.best_model_metrics

    computed_metrics = copy.deepcopy(training_state.computed_metrics)
    per_label_metrics = copy.deepcopy(training_state.per_label_metrics)

    epoch_end = time.time()
    train_start = time.time()
    train_sys_meter = SystemMeter()
    valid_sys_meter = SystemMeter()

    # Initialize the evaluators for the training and validation subsets.
    train_evaluator = ObjectDetectionInstanceSegmentationEvaluator(
        settings=settings, class_names=val_index_map,
        dataset_processing_type=train_data_loader.dataset.dataset_processing_type,
        dataset_wrapper=train_data_loader.dataset
    )
    validation_evaluator = ObjectDetectionInstanceSegmentationEvaluator(
        settings=settings, class_names=val_index_map,
        dataset_processing_type=val_data_loader.dataset.dataset_processing_type,
        dataset_wrapper=val_data_loader.dataset
    )

    specs = {
        'model_specs': model.specs,
        'model_settings': model.model_settings.get_settings_dict(),
        'classes': model.classes,
        'inference_settings': model.inference_settings
    }

    start_epoch = training_state.get_start_epoch(number_of_epochs=number_of_epochs)
    for epoch in range(start_epoch, number_of_epochs):
        logger.info("Training epoch {}.".format(epoch))

        if distributed:
            if train_data_loader.distributed_sampler is None:
                msg = "train_data_loader.distributed_sampler is None in distributed mode. " \
                      "Cannot shuffle data after each epoch."
                logger.error(msg)
                raise AutoMLVisionSystemException(msg, has_pii=False)
            train_data_loader.distributed_sampler.set_epoch(epoch)

        enable_evaluation = log_training_metrics and epoch % eval_freq == 0 \
            and val_metric_type != ValidationMetricType.NONE
        train_evaluator.start_evaluation(enable_evaluation)
        avg_loss = \
            train_one_epoch(base_model, optimizer, scheduler,
                            train_data_loader, device, criterion, epoch,
                            print_freq=100, system_meter=train_sys_meter, distributed=distributed,
                            grad_accum_steps=grad_accum_steps, grad_clip_type=grad_clip_type,
                            evaluator=train_evaluator)

        computed_metrics[scoring_constants.LOG_LOSS + '_train'] = avg_loss
        if train_evaluator.enabled:
            incremental_voc_evaluator = train_evaluator.incremental_voc_evaluator\
                if train_evaluator.eval_voc else None
            compute_metrics(train_evaluator.eval_bounding_boxes, train_evaluator.val_metric_type,
                            train_evaluator.coco_index, incremental_voc_evaluator,
                            computed_metrics, per_label_metrics,
                            train_evaluator.coco_metric_time, train_evaluator.voc_metric_time,
                            train_evaluator.primary_metric, is_train=True)

        map_score = 0.0
        final_epoch = epoch + 1 == number_of_epochs
        if epoch % eval_freq == 0 or final_epoch:
            is_best = False
            if val_metric_type != ValidationMetricType.NONE:
                validation_evaluator.start_evaluation(enable=True)
                avg_loss = \
                    validate(model=model.model, val_data_loader=val_data_loader,
                             device=device, system_meter=valid_sys_meter,
                             distributed=distributed, evaluator=validation_evaluator
                             )
                if log_validation_loss:
                    computed_metrics[scoring_constants.LOG_LOSS] = avg_loss
                incremental_voc_evaluator = validation_evaluator.incremental_voc_evaluator\
                    if validation_evaluator.eval_voc else None
                map_score = compute_metrics(validation_evaluator.eval_bounding_boxes,
                                            validation_evaluator.val_metric_type,
                                            validation_evaluator.coco_index,
                                            incremental_voc_evaluator,
                                            computed_metrics, per_label_metrics,
                                            validation_evaluator.coco_metric_time,
                                            validation_evaluator.voc_metric_time,
                                            validation_evaluator.primary_metric, is_train=False)

                # start incrementing no progress counter only after early_stopping_delay
                if epoch >= early_stopping_delay:
                    no_progress_counter += 1

                if map_score > best_score:
                    no_progress_counter = 0

                if map_score >= best_score:
                    is_best = True
                    best_epoch = epoch
                    best_score = map_score
                    best_model_metrics = copy.deepcopy(computed_metrics)

            else:
                logger.info("val_metric_type is None. Not computing metrics.")
                is_best = True
                best_epoch = epoch

            # save best model checkpoint
            if is_best and master_process:
                best_model_wts = copy.deepcopy(model.state_dict())
                save_model_checkpoint(epoch=best_epoch,
                                      model_name=model.model_name,
                                      number_of_classes=model.number_of_classes,
                                      specs=specs,
                                      model_state=model.state_dict(),
                                      optimizer_state=optimizer.state_dict(),
                                      lr_scheduler_state=scheduler.lr_scheduler.state_dict(),
                                      score=best_score,
                                      metrics=best_model_metrics,
                                      output_dir=output_dir)

            logger.info("Current best primary metric score: {0:.3f} (at epoch {1})".format(
                round(best_score, 5), best_epoch))

        # for logging the per_label_metrics
        stop_early = is_enabled_early_stopping and no_progress_counter > early_stopping_patience

        # log to Run History every epoch with previously computed metrics, if not computed in the current epoch
        # to sync the metrics reported index with actual training epoch.
        if master_process and azureml_run is not None:
            utils.log_all_metrics(computed_metrics, azureml_run=azureml_run, add_to_logger=True)

            parent_run = utils.should_log_metrics_to_parent(azureml_run)
            if parent_run:
                utils.log_all_metrics(computed_metrics, azureml_run=parent_run, add_to_logger=True)

            # Log detailed metrics only at the end.
            if (final_epoch or stop_early) and best_model_metrics:
                utils.log_detailed_object_detection_metrics(best_model_metrics, azureml_run, val_index_map)

                # If parent is a pipeline run, log all training metrics to parent pipeline as well.
                if parent_run:
                    utils.log_detailed_object_detection_metrics(best_model_metrics, parent_run, val_index_map)

        # measure elapsed time
        epoch_time.update(time.time() - epoch_end)
        epoch_end = time.time()
        msg = "Epoch-level: [{0}]\t" \
              "Epoch-level Time {epoch_time.value:.4f} ({epoch_time.avg:.4f})".format(epoch, epoch_time=epoch_time)
        logger.info(msg)

        # save model checkpoint
        if checkpoint_freq is not None and epoch % checkpoint_freq == 0 and master_process:
            training_state.no_progress_counter = no_progress_counter
            training_state.stop_early = stop_early
            training_state.computed_metrics = copy.deepcopy(computed_metrics)
            training_state.per_label_metrics = copy.deepcopy(per_label_metrics)
            model_location = save_model_checkpoint(epoch=epoch,
                                                   model_name=model.model_name,
                                                   number_of_classes=model.number_of_classes,
                                                   specs=specs,
                                                   model_state=model.state_dict(),
                                                   optimizer_state=optimizer.state_dict(),
                                                   lr_scheduler_state=scheduler.lr_scheduler.state_dict(),
                                                   score=map_score,
                                                   metrics=computed_metrics,
                                                   output_dir=output_dir,
                                                   model_file_name_prefix=str(epoch) + '_',
                                                   training_state=training_state)

            upload_model_checkpoint(run=azureml_run, model_location=model_location)

        if stop_early:
            logger.info("No progress registered after {0} epochs. "
                        "Early stopping the run.".format(no_progress_counter))
            break

        # collect garbage after each epoch
        gc.collect()

    # measure total training time
    train_time = time.time() - train_start
    utils.log_end_training_stats(train_time, epoch_time, train_sys_meter, valid_sys_meter)

    if log_verbose_metrics:
        utils.log_verbose_metrics_to_rh(train_time, epoch_time, train_sys_meter, valid_sys_meter, azureml_run)

    if master_process:
        write_scoring_script(output_dir, task_type=task_type)

        write_per_label_metrics_file(output_dir, per_label_metrics, val_index_map)

        write_artifacts(model_wrapper=model,
                        best_model_weights=best_model_wts,
                        labels=model.classes,
                        output_dir=output_dir,
                        run=azureml_run,
                        best_metric=best_score,
                        task_type=task_type,
                        device=device,
                        enable_onnx_norm=enable_onnx_norm,
                        model_settings=model.model_settings.get_settings_dict(),
                        save_as_mlflow=save_as_mlflow
                        )
