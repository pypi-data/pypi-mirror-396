# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Functions to help save the artifacts at the end of the training."""

import os
import json
import time
import tempfile

import torch
from torch.nn.modules import Module
from torch.optim.optimizer import Optimizer

import azureml.automl.core.shared.constants as shared_constants
from azureml.automl.dnn.vision.common.constants import ArtifactLiterals, SettingsLiterals, CommonSettings
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException, \
    AutoMLVisionRuntimeUserException
from azureml.automl.dnn.vision.common.model_export_utils import prepare_model_export
from azureml.automl.dnn.vision.common.torch_utils import intersect_dicts
from azureml.automl.dnn.vision.common.trainer.lrschedule import BaseLRSchedulerWrapper
from azureml.automl.dnn.vision.common.training_state import TrainingState
from azureml.automl.dnn.vision.common.utils import logger, \
    _set_train_run_properties, _distill_run_from_experiment, should_log_metrics_to_parent
from azureml.automl.dnn.vision.object_detection.common.constants import ModelNames
from azureml.automl.dnn.vision.object_detection.models.object_detection_model_wrappers \
    import BaseObjectDetectionModelWrapper
from azureml.core.run import Run, _OfflineRun
from typing import Union, Any, Dict, Optional, List, Tuple
from azureml.exceptions import AzureMLAggregatedException


def write_artifacts(model_wrapper: Union[BaseObjectDetectionModelWrapper, Module],
                    best_model_weights: Dict[str, Any], labels: List[str],
                    output_dir: str, run: Run, best_metric: float,
                    task_type: str, device: Optional[str] = None,
                    enable_onnx_norm: Optional[bool] = False,
                    model_settings: Dict[str, Any] = {},
                    save_as_mlflow: bool = False, is_yolo: bool = False) -> None:
    """Export onnx model and write artifacts at the end of training.

    :param model_wrapper: Model wrapper or model
    :type model_wrapper: Union[CommonObjectDetectionModelWrapper, Model]
    :param best_model_weights: weights of the best model
    :type best_model_weights: dict
    :param labels: list of classes
    :type labels: List[str]
    :param output_dir: Name of dir to save model files. If it does not exist, it will be created.
    :type output_dir: String
    :param run: azureml run object
    :type run: azureml.core.run.Run
    :param best_metric: best metric value to store in properties
    :type best_metric: float
    :param task_type: task type
    :type task_type: str
    :param device: device where model should be run (usually 'cpu' or 'cuda:0' if it is the first gpu)
    :type device: str
    :param enable_onnx_norm: enable normalization when exporting onnx
    :type enable_onnx_norm: bool
    :param model_settings: Settings for the model
    :type model_settings: dict
    :param save_as_mlflow: Flag that indicates whether to save in mlflow format
    :type save_as_mlflow: bool
    :param is_yolo: Flag that indicates if the model is a yolo model
    :type is_yolo: bool
    """
    os.makedirs(output_dir, exist_ok=True)

    model_wrapper.load_state_dict(best_model_weights)

    # Export and save the torch onnx model.
    onnx_file_path = os.path.join(output_dir, ArtifactLiterals.ONNX_MODEL_FILE_NAME)
    model_wrapper.export_onnx_model(file_path=onnx_file_path, device=device, enable_norm=enable_onnx_norm)

    # Explicitly Save the labels to a json file.
    if labels is None:
        raise AutoMLVisionValidationException('No labels were found in the dataset wrapper', has_pii=False)
    label_file_path = os.path.join(output_dir, ArtifactLiterals.LABEL_FILE_NAME)
    with open(label_file_path, 'w') as f:
        json.dump(labels, f)

    _set_train_run_properties(run, model_wrapper.model_name, best_metric)

    folder_name = os.path.basename(output_dir)
    try:
        run.upload_folder(name=folder_name, path=output_dir)
    except AzureMLAggregatedException as e:
        if "Resource Conflict" in e.message:
            parsed_message = e.message.replace("UserError: ", "")
            logger.warning("Resource conflict when uploading artifacts to run.")
            logger.warning(parsed_message)
        else:
            raise
    parent_run = should_log_metrics_to_parent(run)
    if parent_run:
        try:
            parent_run.upload_folder(name=folder_name, path=output_dir)
        except AzureMLAggregatedException as e:
            if "Resource Conflict" in e.message:
                parsed_message = e.message.replace("UserError: ", "")
                logger.warning("Resource conflict when uploading artifacts to parent run.")
                logger.warning(parsed_message)
            else:
                raise
    model_settings.update(model_wrapper.inference_settings)
    # to be dumped in MLFlow MLmodel file.
    metadata = {
        shared_constants.MLFlowMetaLiterals.BASE_MODEL_NAME : model_wrapper.model_name,
        shared_constants.MLFlowMetaLiterals.FINETUNING_TASK : task_type,
        shared_constants.MLFlowMetaLiterals.IS_AUTOML_MODEL : True,
        shared_constants.MLFlowMetaLiterals.TRAINING_RUN_ID : run.id
    }
    try:
        prepare_model_export(run=run,
                             output_dir=output_dir,
                             task_type=task_type,
                             model_settings=model_settings,
                             save_as_mlflow=save_as_mlflow,
                             is_yolo=is_yolo,
                             metadata=metadata)
    except AzureMLAggregatedException as e:
        if "Resource Conflict" in e.message:
            parsed_message = e.message.replace("UserError: ", "")
            logger.warning("Resource conflict when preparing model export.")
            logger.warning(parsed_message)
        else:
            raise


def upload_model_checkpoint(run: Run, model_location: str) -> None:
    """Uploads the model checkpoints to workspace.

    :param run: azureml run object
    :type run: azureml.core.Run
    :param model_location: Location of saved model file
    :type model_location: str
    """
    try:
        run.upload_files(names=[model_location],
                         paths=[model_location])
    except Exception as e:
        logger.error('Error in uploading the checkpoint: {}'.format(e))

    parent_run = should_log_metrics_to_parent(run)
    if parent_run:
        try:
            parent_run.upload_files(names=[model_location],
                                    paths=[model_location])
        except Exception as e:
            logger.error('Error in uploading the checkpoint to pipeline run: {}'.format(e))

    # Always remove the intermediate checkpoint file. If it was successfully uploaded, then it does not need to exist
    # on the local disk. If the upload failed, the only other time it would be uploaded is at the end of training,
    # when the final checkpoint supersedes it.
    os.remove(model_location)


def save_model_checkpoint(epoch: int, model_name: str, number_of_classes: int, specs: Dict[str, Any],
                          model_state: Dict[str, Any], optimizer_state: Dict[str, Any],
                          lr_scheduler_state: Dict[str, Any], score: float, metrics: Any,
                          output_dir: str, model_file_name_prefix: str = '',
                          model_file_name: str = shared_constants.PT_MODEL_FILENAME,
                          training_state: Optional[TrainingState] = None) -> str:
    """Saves a model checkpoint to a file.

    :param epoch: the training epoch
    :type epoch: int
    :param model_name: Model name
    :type model_name: str
    :param number_of_classes: number of classes for the model
    :type number_of_classes: int
    :param specs: model specifications
    :type specs: dict
    :param model_state: model state dict
    :type model_state: dict
    :param optimizer_state: optimizer state dict
    :type optimizer_state: dict
    :param lr_scheduler_state: lr scheduler state
    :type lr_scheduler_state: dict
    :param score: Primary metrics for the current model
    :type score: float
    :param metrics: Metrics for the current model
    :type metrics: Any
    :param output_dir: output folder for the checkpoint file
    :type output_dir: str
    :param model_file_name_prefix: prefix to use for the output file
    :type model_file_name_prefix: str
    :param model_file_name: name of the output file that contains the checkpoint
    :type model_file_name: str
    :param training_state: Training state.
    :type training_state: TrainingState.
    :return: Location of saved model file
    :rtype: str
    """
    checkpoint_start = time.time()

    os.makedirs(output_dir, exist_ok=True)
    model_location = os.path.join(output_dir, model_file_name_prefix + model_file_name)

    checkpoint_data = {
        'epoch': epoch,
        'model_name': model_name,
        'number_of_classes': number_of_classes,
        'specs': specs,
        'model_state': model_state,
        'optimizer_state': optimizer_state,
        'lr_scheduler_state': lr_scheduler_state,
        'score': score,
        'metrics': metrics
    }

    if training_state is not None:
        checkpoint_data.update({
            'training_state': training_state.state_dict()
        })

    torch.save(checkpoint_data, model_location)

    checkpoint_creation_time = time.time() - checkpoint_start
    logger.info('Model checkpoint creation ({}) took {:.2f}s.'
                .format(model_location, checkpoint_creation_time))

    return model_location


def _download_model_from_artifacts(run_id: str, experiment_name: Optional[str] = None) -> None:
    logger.info("Start fetching model from artifacts")
    run = _distill_run_from_experiment(run_id, experiment_name)
    run.download_file(os.path.join(ArtifactLiterals.OUTPUT_DIR, shared_constants.PT_MODEL_FILENAME),
                      shared_constants.PT_MODEL_FILENAME)
    logger.info("Finished downloading files from artifacts")


def load_from_pretrained_checkpoint(settings: Dict[str, Any], model_wrapper: Any, distributed: bool) -> None:
    """Load model weights from pretrained checkpoint via run_id or FileDataset id

    :param settings: dictionary containing settings for training
    :type settings: dict
    :param model_wrapper: Model wrapper
    :type model_wrapper:
    :param distributed: Training in distributed mode or not
    :type distributed: bool
    """
    checkpoint_run_id = settings.get(SettingsLiterals.CHECKPOINT_RUN_ID, None)
    checkpoint_dataset_id = settings.get(SettingsLiterals.CHECKPOINT_DATASET_ID, None)
    checkpoint_filename = settings.get(SettingsLiterals.CHECKPOINT_FILENAME, None)
    ckpt_local_path = None
    if checkpoint_run_id:
        ckpt_local_path = shared_constants.PT_MODEL_FILENAME
    elif checkpoint_dataset_id and checkpoint_filename:
        ckpt_local_path = os.path.join(CommonSettings.TORCH_HUB_CHECKPOINT_DIR, checkpoint_filename)

    if ckpt_local_path:
        logger.info('Trying to load weights from a pretrained checkpoint')
        checkpoint = torch.load(ckpt_local_path, map_location='cpu', weights_only=False)
        logger.info("[checkpoint model_name: {}, number_of_classes: {}, specs: {}]"
                    .format(checkpoint['model_name'], checkpoint['number_of_classes'], checkpoint['specs']))
        load_model_from_checkpoint(checkpoint, model_wrapper, distributed)


def load_model_from_checkpoint(checkpoint: Dict[str, Any], model_wrapper: Any, distributed: bool) -> None:
    """Load model weights from checkpoint into the model wrapper

    :param checkpoint: Checkpoint
    :type checkpoint: dict
    :param model_wrapper: Model Wrapper
    :type model_wrapper: Any
    :param distributed: Distributed or not
    :type distributed: bool
    """
    if checkpoint['model_name'] == model_wrapper.model_name:
        torch_model = model_wrapper.model.module if distributed else model_wrapper.model
        # Gracefully handle size mismatch, missing and unexpected keys errors
        state_dict = intersect_dicts(checkpoint['model_state'], torch_model.state_dict())
        if len(state_dict.keys()) == 0:
            raise AutoMLVisionValidationException("Could not load pretrained model weights. "
                                                  "State dict intersection is empty.", has_pii=False)
        if model_wrapper.model_name == ModelNames.YOLO_V5:
            state_dict = {'model.' + k: v for k, v in state_dict.items()}
        torch_model.load_state_dict(state_dict, strict=False)
        logger.info('checkpoint is successfully loaded')
    else:
        msg = ("checkpoint is NOT loaded since model_name is {} while checkpoint['model_name'] is {}"
               .format(model_wrapper.model_name, checkpoint['model_name']))
        raise AutoMLVisionRuntimeUserException(msg)


def _get_latest_checkpoint_filename(checkpoint_filenames: List[str]) -> Tuple[Optional[str], int]:
    """Get latest checkpoint file name in the list of checkpoint file names."""
    latest_checkpoint_filename = None
    latest_checkpoint_epoch = -1
    # Checkpoint names are in the format "<epoch>_model.pt"
    for file_name in checkpoint_filenames:
        base_file_name = os.path.basename(file_name)
        file_name_parts = base_file_name.split("_")
        if len(file_name_parts) == 2 and file_name_parts[1] == shared_constants.PT_MODEL_FILENAME:
            try:
                checkpoint_epoch = int(file_name_parts[0])
                if checkpoint_epoch >= latest_checkpoint_epoch:
                    latest_checkpoint_filename = file_name
                    latest_checkpoint_epoch = checkpoint_epoch
            except ValueError:
                logger.warning("Found a checkpoint file with name in invalid format. Skipping it.")

    return latest_checkpoint_filename, latest_checkpoint_epoch


def get_latest_checkpoint(output_dir: str, run: Run) -> Optional[Dict[str, Any]]:
    """Get latest checkpoint data. Checkpoints are uploaded regularly to run artifacts and removed from local paths.
    It is possible that this upload might fail, in which case the checkpoint is available locally, but not in remote.
    This method finds the latest checkpoint from combination of local and remote paths
    and return the latest checkpoint data.

    :param output_dir: Output folder where the artifacts are stored.
    :type output_dir: str
    :param run: azureml run object
    :type run: azureml.core.Run
    :return: latest checkpoint data
    :rtype: Optional[Dict[str, Any]]
    """
    latest_checkpoint = None

    # First, find the latest checkpoint path in local files
    local_checkpoint_filename, local_checkpoint_epoch = _get_latest_checkpoint_filename(os.listdir(output_dir))
    if local_checkpoint_filename is not None:
        checkpoint_path = os.path.join(output_dir, local_checkpoint_filename)
        logger.info("Latest checkpoint from local output directory is for epoch: {}".format(local_checkpoint_epoch))
        logger.info('Loading training state from latest checkpoint at epoch: {}'.format(
            local_checkpoint_epoch))
        latest_checkpoint = torch.load(checkpoint_path, map_location='cpu', weights_only=False)
    else:
        logger.info("No checkpoints found in local output directory.")

    # Check if any checkpoints previously uploaded via upload_model_checkpoint are more recent
    if run is not None and not isinstance(run, _OfflineRun):
        logger.info("Looking for checkpoints in run artifacts.")
        run_filenames = run.get_file_names()
        checkpoint_filenames = [filename for filename in run_filenames if filename.startswith(output_dir)]
        remote_checkpoint_filename, remote_checkpoint_epoch = _get_latest_checkpoint_filename(checkpoint_filenames)
        if remote_checkpoint_filename is not None:
            logger.info(
                "Latest checkpoint from run artifacts is for epoch: {}".format(remote_checkpoint_epoch))
            if remote_checkpoint_epoch > local_checkpoint_epoch:
                logger.info("Checkpoint from run artifacts is more recent than one from local output directory. "
                            "Downloading it to a temp directory.")
                with tempfile.TemporaryDirectory() as tmp_download_dir:
                    tmp_checkpoint_path = os.path.join(tmp_download_dir, os.path.basename(remote_checkpoint_filename))
                    try:
                        run.download_file(remote_checkpoint_filename, tmp_checkpoint_path)
                    except Exception as e:
                        logger.error('Error in downloading the checkpoint: {}'.format(e))
                    else:
                        logger.info('Loading training state from latest checkpoint at epoch: {}'.format(
                            remote_checkpoint_epoch))
                        latest_checkpoint = torch.load(tmp_checkpoint_path, map_location='cpu', weights_only=False)
            else:
                logger.info("Checkpoint from local output directory is more recent than one from run artifacts.")
        else:
            logger.info("No checkpoints found in run artifacts.")

    return latest_checkpoint


def load_state_from_latest_checkpoint(output_dir: str, run: Run, model_wrapper: Any, distributed: bool,
                                      optimizer: Optimizer, scheduler: BaseLRSchedulerWrapper,
                                      training_state: TrainingState) -> None:
    """Load state dictionaries of model wrapper, optimizer, scheduler and training state from the latest checkpoint in
    output directory. If there is no checkpoint in output directory, this function would be a no-op.

    :param output_dir: Output folder where the artifacts are stored.
    :type output_dir: str
    :param run: azureml run object
    :type run: azureml.core.Run
    :param model_wrapper: Model wrapper
    :type model_wrapper: Any
    :param distributed: Distributed or not
    :type distributed: bool
    :param optimizer: Optimizer
    :type optimizer: torch.optim.optimizer.Optimizer
    :param scheduler: Lr scheduler wrapper
    :type scheduler: BaseLRSchedulerWrapper
    :param training_state: Training state
    :type training_state: TrainingState
    """

    checkpoint = get_latest_checkpoint(output_dir, run)

    if checkpoint is None:
        logger.info("Latest checkpoint not found. Skipping loading training state.")
        return

    logger.info("[checkpoint epoch: {}, model_name: {}, number_of_classes: {}, specs: {}]"
                .format(checkpoint['epoch'], checkpoint['model_name'], checkpoint['number_of_classes'],
                        checkpoint['specs']))
    if 'training_state' not in checkpoint:
        logger.info("Training state not found in latest checkpoint. Skipping loading training state.")
        return

    load_model_from_checkpoint(checkpoint, model_wrapper, distributed)
    optimizer.load_state_dict(checkpoint['optimizer_state'])
    scheduler.lr_scheduler.load_state_dict(checkpoint['lr_scheduler_state'])
    training_state.load_state_dict(checkpoint['training_state'])
    training_state.epoch = checkpoint['epoch']

    # Load best model weights from model.pt in outputs dir and update it in training_state.
    best_model_path = os.path.join(output_dir, shared_constants.PT_MODEL_FILENAME)
    if os.path.exists(best_model_path):
        logger.info('Found best model checkpoint. Will load best model weights into training state.')
        best_model_checkpoint = torch.load(best_model_path, map_location='cpu', weights_only=False)
        training_state.best_model_wts = best_model_checkpoint['model_state']
        training_state.best_epoch = best_model_checkpoint['epoch']
        training_state.best_score = best_model_checkpoint['score']
        training_state.best_model_metrics = best_model_checkpoint['metrics']
    else:
        logger.info("Best model checkpoint not found. Cannot load best model weights into training state.")

    logger.info("Training state loaded successfully from saved checkpoint at epoch {}".format(training_state.epoch))
