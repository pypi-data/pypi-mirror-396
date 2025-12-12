# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for common methods."""
import argparse
import copy
import json
from operator import truediv
import logging
import os
import sys
import tempfile
from pathlib import Path
from unittest import mock
from unittest.mock import MagicMock, patch, call

import azureml
import numpy as np
import pandas as pd
import pytest
import torch.utils.data as data
from azureml.automl.core.inference.inference import AutoMLInferenceArtifactIDs
from azureml.automl.core.shared.constants import MLTableDataLabel
from azureml._common._error_definition import AzureMLError
from azureml.automl.core.shared._diagnostics.automl_error_definitions import InsufficientMemory, InsufficientGPUMemory
from azureml.automl.core.shared.exceptions import ResourceException
from azureml.automl.dnn.vision.classification.runner import _parse_argument_settings as mc_parser
from azureml.automl.dnn.vision.common import utils
from azureml.automl.dnn.vision.common.aml_dataset_base_wrapper import AmlDatasetBaseWrapper
from azureml.automl.dnn.vision.common.constants import SettingsLiterals, RunPropertyLiterals, \
    TrainingCommonSettings, DistributedLiterals, TrainingLiterals, MetricsLiterals
from azureml.automl.dnn.vision.common.data_utils import validate_labels_files_paths
from azureml.automl.dnn.vision.common.dataloaders import RobustDataLoader, _RobustCollateFn
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionValidationException, AutoMLVisionDataException, \
    AutoMLVisionSystemException
from azureml.automl.dnn.vision.common.utils import _merge_settings_args_defaults, _exception_handler, \
    _read_image, is_aml_dataset_input, _set_train_run_properties, _save_image_df, get_dataset_from_mltable, \
    launch_training_with_retries
from azureml.automl.dnn.vision.object_detection.common.constants import TilingLiterals
from azureml.automl.dnn.vision.object_detection.runner import _parse_argument_settings as od_parser
from azureml.automl.dnn.vision.object_detection_yolo.runner import _parse_argument_settings as od_yolo_parser
from azureml.automl.dnn.vision.object_detection_yolo.common.constants import ModelSize, YoloLiterals
from azureml.core import Run, Experiment
from azureml.exceptions import UserErrorException
from azureml.automl.dnn.vision.common.sku_validation import validate_gpu_sku, MEGABYTE
from types import SimpleNamespace
from .run_mock import RunMock, ExperimentMock, WorkspaceMock, DatastoreMock

import azureml.automl.dnn.vision.classification.runner as classification_runner

_THIS_FILES_DIR = Path(os.path.dirname(__file__))
_PARENT_DIR = _THIS_FILES_DIR.parent
_VALID_PATH = "data/classification_data/multiclass.csv"
_INVALID_PATH = "invalid_path"


class MissingFilesDataset(data.Dataset):
    def __init__(self):
        self._labels = ['label_1', 'label_2', 'label_3']
        self._images = [1, None, 2]

    def __getitem__(self, index):
        return self._images[index], self._labels[index]

    def __len__(self):
        return len(self._labels)


class TestRobustDataLoader:
    def _test_data_loader(self, loader):
        all_data_len = 0
        for images, label in loader:
            all_data_len += images.shape[0]
        assert all_data_len == 2

    def _test_data_loader_with_exception_safe_iterator(self, loader):
        all_data_len = 0
        for images, label in utils._data_exception_safe_iterator(iter(loader)):
            all_data_len += images.shape[0]
        assert all_data_len == 2

    def test_robust_dataloader(self):
        dataset = MissingFilesDataset()
        dataloader = RobustDataLoader(dataset, batch_size=10, num_workers=0)
        self._test_data_loader(dataloader)
        self._test_data_loader_with_exception_safe_iterator(dataloader)

    def test_robust_dataloader_invalid_batch(self):
        dataset = MissingFilesDataset()
        dataloader = RobustDataLoader(dataset, batch_size=1, num_workers=0)
        with pytest.raises(AutoMLVisionDataException) as exc_info:
            self._test_data_loader(dataloader)
        assert exc_info.value.message == _RobustCollateFn.EMPTY_BATCH_ERROR_MESSAGE
        self._test_data_loader_with_exception_safe_iterator(dataloader)

        # Dataloader with multiple workers should raise the exception
        dataloader = RobustDataLoader(dataset, batch_size=1, num_workers=4)
        with pytest.raises(AutoMLVisionDataException) as exc_info:
            self._test_data_loader(dataloader)
        assert _RobustCollateFn.EMPTY_BATCH_ERROR_MESSAGE in exc_info.value.message
        self._test_data_loader_with_exception_safe_iterator(dataloader)


def test_config_merge():
    settings = {"a": "a_s", "b": 1, "c": "c_s"}

    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument('--b')
    parser.add_argument('--d')
    parser.add_argument('--f')
    args = parser.parse_args(args=["--b", "b_a", "--d", "d_a", "--f", "f_a"])

    defaults = {"b": "b_d", "d": "d_d", "g": 10}

    merged_settings = _merge_settings_args_defaults(settings, vars(args), defaults)

    assert merged_settings["a"] == "a_s"
    assert merged_settings["b"] == 1
    assert merged_settings["c"] == "c_s"
    assert merged_settings["d"] == "d_a"
    assert merged_settings["f"] == "f_a"
    assert merged_settings["g"] == 10


@pytest.mark.parametrize(
    "parameter_type, passed_value, parsed_value",
    ([bool, "True", True],
     [bool, "False", False],
     [bool, "true", True],
     [bool, "false", False],
     [bool, "1", True],
     [bool, "0", False],
     [int, "1", 1],
     [int, "1.0", 1],
     [float, "1.2", 1.2],
     [float, "1", 1.0],
     [str, "test_str", "test_str"],
     [str, "10", "10"],
     [str, "1.99", "1.99"],
     [str, "1.0", "1.0"],
     [str, "true", "true"],
     [str, "false", "false"],
     [str, "1", "1"],
     [str, "0", "0"],
     ))
def test_args_parse(parameter_type, passed_value, parsed_value):
    bool_args = [TrainingLiterals.EARLY_STOPPING,
                 TrainingLiterals.NESTEROV,
                 TrainingLiterals.AMSGRAD,
                 DistributedLiterals.DISTRIBUTED,
                 SettingsLiterals.ENABLE_ONNX_NORMALIZATION,
                 SettingsLiterals.SAVE_MLFLOW,
                 SettingsLiterals.ENABLE_CODE_GENERATION]
    int_args = [TrainingLiterals.NUMBER_OF_EPOCHS,
                TrainingLiterals.TRAINING_BATCH_SIZE,
                TrainingLiterals.VALIDATION_BATCH_SIZE,
                TrainingLiterals.GRAD_ACCUMULATION_STEP,
                TrainingLiterals.EARLY_STOPPING_PATIENCE,
                TrainingLiterals.EARLY_STOPPING_DELAY,
                TrainingLiterals.STEP_LR_STEP_SIZE,
                TrainingLiterals.WARMUP_COSINE_LR_WARMUP_EPOCHS,
                TrainingLiterals.EVALUATION_FREQUENCY,
                TrainingLiterals.CHECKPOINT_FREQUENCY,
                TrainingLiterals.LAYERS_TO_FREEZE]
    float_args = [TrainingLiterals.LEARNING_RATE,
                  TrainingLiterals.STEP_LR_GAMMA,
                  TrainingLiterals.WARMUP_COSINE_LR_CYCLES,
                  TrainingLiterals.MOMENTUM,
                  TrainingLiterals.WEIGHT_DECAY,
                  TrainingLiterals.BETA1,
                  TrainingLiterals.BETA2,
                  TrainingLiterals.SPLIT_RATIO]
    str_args = [SettingsLiterals.DEVICE,
                SettingsLiterals.CHECKPOINT_RUN_ID,
                SettingsLiterals.CHECKPOINT_DATASET_ID,
                SettingsLiterals.CHECKPOINT_FILENAME]

    def _test_arg(arg, yolo_only):
        for scenario in ["simple", "conditional"]:

            if scenario == "simple":
                prefixed_arg = '--' + arg
                sys.argv = ['hd_image_classification_dnn_driver.py',
                            '--data-folder', '',
                            '--labels-file-root', '',
                            prefixed_arg, passed_value]
            else:
                sys.argv = ['hd_image_classification_dnn_driver.py',
                            '--data-folder', '',
                            '--labels-file-root', '',
                            '--model', json.dumps({arg: passed_value})]

            if not yolo_only:
                settings, unknown = mc_parser(automl_settings={}, multilabel=False)
                assert settings[arg] == parsed_value
                assert not unknown

                settings, unknown = mc_parser(automl_settings={}, multilabel=True)
                assert settings[arg] == parsed_value
                assert not unknown

                settings, unknown = od_parser(automl_settings={})
                assert settings[arg] == parsed_value
                assert not unknown

            settings, unknown = od_yolo_parser(automl_settings={})
            assert settings[arg] == parsed_value
            assert not unknown

    if parameter_type == bool:
        args = bool_args
        _test_arg(YoloLiterals.MULTI_SCALE, True)
    elif parameter_type == int:
        args = int_args
    elif parameter_type == float:
        args = float_args
    elif parameter_type == str:
        args = str_args
    for arg in args:
        _test_arg(arg, False)


def test_tmp_parser():
    # get model_name from argument SettingsLiterals.MODEL_NAME
    parser = argparse.ArgumentParser(allow_abbrev=False, add_help=False)
    utils.add_model_arguments(parser)
    input_mn = [f"--{SettingsLiterals.MODEL_NAME}", "model_a"]
    args_mn, _ = parser.parse_known_args(input_mn)
    args_dict_mn, _ = utils.parse_model_conditional_space(vars(args_mn), parser)
    model_name = args_dict_mn[SettingsLiterals.MODEL_NAME]
    assert model_name == "model_a"

    # get model_name from argument SettingsLiterals.MODEL
    input_m = [f"--{SettingsLiterals.MODEL}", f'{{"{SettingsLiterals.MODEL_NAME}": "model_b"}}']
    args_m, _ = parser.parse_known_args(input_m)
    args_dict_m, _ = utils.parse_model_conditional_space(vars(args_m), parser)
    model_name = args_dict_m[SettingsLiterals.MODEL_NAME]
    assert model_name == "model_b"


def test_arg_parser():
    # Test codegen flag
    settings, unknown = mc_parser(automl_settings={}, multilabel=False)
    assert settings.get(SettingsLiterals.ENABLE_CODE_GENERATION)

    settings, unknown = mc_parser(automl_settings={}, multilabel=True)
    assert settings.get(SettingsLiterals.ENABLE_CODE_GENERATION)

    settings, unknown = od_parser(automl_settings={})
    assert settings.get(SettingsLiterals.ENABLE_CODE_GENERATION)

    settings, unknown = od_yolo_parser(automl_settings={})
    assert settings.get(SettingsLiterals.ENABLE_CODE_GENERATION)


def test_yolo_model_size_args_parse():
    for model_size in ModelSize.ALL_TYPES:
        arg = '--' + YoloLiterals.MODEL_SIZE
        sys.argv = ['hd_image_object_detection_dnn_driver.py',
                    '--data-folder', '',
                    '--labels-file-root', '',
                    arg, model_size]

        settings, unknown = od_yolo_parser(automl_settings={})
        assert settings[YoloLiterals.MODEL_SIZE] == model_size
        assert not unknown


def test_labels_files_paths_val_not_aml_dataset_both_paths_valid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _VALID_PATH,
        SettingsLiterals.VALIDATION_LABELS_FILE: _VALID_PATH
    }

    validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_both_paths_invalid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _INVALID_PATH,
        SettingsLiterals.VALIDATION_LABELS_FILE: _INVALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_labels_valid_val_invalid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _VALID_PATH,
        SettingsLiterals.VALIDATION_LABELS_FILE: _INVALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_labels_invalid_val_valid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _INVALID_PATH,
        SettingsLiterals.VALIDATION_LABELS_FILE: _VALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_only_labels_valid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _VALID_PATH
    }

    validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_only_labels_invalid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.LABELS_FILE: _INVALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_only_val_valid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.VALIDATION_LABELS_FILE: _VALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_only_val_invalid():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: _PARENT_DIR,
        SettingsLiterals.VALIDATION_LABELS_FILE: _INVALID_PATH
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_not_aml_dataset_with_no_paths():
    settings = {
        SettingsLiterals.LABELS_FILE_ROOT: "",
        SettingsLiterals.LABELS_FILE: "",
        SettingsLiterals.VALIDATION_LABELS_FILE: ""
    }

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)

    settings[SettingsLiterals.DATASET_ID] = ""

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)

    settings[SettingsLiterals.DATASET_ID] = None

    with pytest.raises(AutoMLVisionValidationException):
        validate_labels_files_paths(settings)


def test_labels_files_paths_val_aml_dataset_with_no_paths():
    settings = {
        SettingsLiterals.DATASET_ID: "some_dataset_id",
        SettingsLiterals.LABELS_FILE_ROOT: "",
        SettingsLiterals.LABELS_FILE: "",
        SettingsLiterals.VALIDATION_LABELS_FILE: ""
    }

    validate_labels_files_paths(settings)


def test_is_aml_dataset_input():
    assert not is_aml_dataset_input({})
    assert not is_aml_dataset_input({SettingsLiterals.DATASET_ID: ""})
    assert not is_aml_dataset_input({SettingsLiterals.DATASET_ID: None})
    assert is_aml_dataset_input({SettingsLiterals.DATASET_ID: "some_dataset_id"})


@mock.patch.object(azureml._restclient.JasmineClient, '__init__', lambda x, y, z, t, **kwargs: None)
@mock.patch.object(azureml._restclient.experiment_client.ExperimentClient, '__init__', lambda x, y, z, **kwargs: None)
@mock.patch('azureml._restclient.experiment_client.ExperimentClient', autospec=True)
@mock.patch('azureml._restclient.metrics_client.MetricsClient', autospec=True)
def test_exception_handler(mock_experiment_client, mock_metrics_client):
    mock_run = MagicMock(spec=Run)
    mock_workspace = MagicMock()
    mock_run.experiment = MagicMock(return_value=Experiment(mock_workspace, "test", _create_in_cloud=False))

    RANDOM_RUNTIME_ERROR = "random system error"
    DATA_RUNTIME_ERROR = "dataset issue"

    @_exception_handler
    def system_error_method(err):
        raise RuntimeError(err)

    @_exception_handler
    def user_error_method():
        raise AutoMLVisionDataException()

    @_exception_handler
    def shm_mem_error_method():
        raise Exception("This might be caused by insufficient shared memory")

    @_exception_handler
    def cuda_error1_method():
        raise RuntimeError(
            "CUDA error: device-side assert triggered\nCUDA kernel errors might be asynchronously reported at some "
            "other API call, so the stacktrace below might be incorrect.\nFor debugging consider passing "
            "CUDA_LAUNCH_BLOCKING=1."
        )

    @_exception_handler
    def cuda_error2_method():
        raise RuntimeError(
            "CUDA error: no kernel image is available for execution on the device\nCUDA kernel errors might be "
            "asynchronously reported at some other API call,so the stacktrace below might be incorrect.\nFor "
            "debugging consider passing CUDA_LAUNCH_BLOCKING=1."
        )

    @_exception_handler
    def cuda_error3_method():
        raise RuntimeError("cuDNN error: CUDNN_STATUS_NOT_INITIALIZED")

    with patch.object(Run, 'get_context', return_value=mock_run):
        with pytest.raises(RuntimeError):
            system_error_method(RANDOM_RUNTIME_ERROR)
        mock_run.fail.assert_called_once()
        assert mock_run.fail.call_args[1]['error_details'].error_type == 'SystemError'
        assert mock_run.fail.call_args[1]['error_details'].error_code == 'AutoMLVisionInternal'
        assert "Additional information: [Hidden as it may contain PII]" not in \
               mock_run.fail.call_args[1]['error_details'].message

        with pytest.raises(RuntimeError):
            system_error_method(DATA_RUNTIME_ERROR)
        assert mock_run.fail.call_args[1]['error_details'].error_type == 'SystemError'
        assert mock_run.fail.call_args[1]['error_details'].error_code == 'AutoMLVisionInternal'
        assert "Additional information: [Hidden as it may contain PII]" in \
               mock_run.fail.call_args[1]['error_details'].message

        with pytest.raises(AutoMLVisionDataException):
            user_error_method()
        assert mock_run.fail.call_args[1]['error_details'].error_type == 'UserError'

        with pytest.raises(Exception):
            shm_mem_error_method()
        assert mock_run.fail.call_args[1]['error_details'].error_type == 'UserError'
        assert mock_run.fail.call_args[1]['error_details'].error_code == 'InvalidData'

        for m in [cuda_error1_method, cuda_error2_method, cuda_error3_method]:
            with pytest.raises(Exception):
                m()
            assert mock_run.fail.call_args[1]['error_details'].error_type == 'SystemError'
            assert mock_run.fail.call_args[1]['error_details'].error_code == 'AutoMLVisionInternal'
            assert \
                "Potential temporary hardware failure - please resubmit the run. If that does not solve the " \
                "problem, please file a support ticket for further investigation." in \
                mock_run.fail.call_args[1]['error_details'].message


@pytest.mark.parametrize('use_cv2', [False, True])
@pytest.mark.parametrize('image_url', ["../data/object_detection_data/images/invalid_image_file.jpg",
                                       "../data/object_detection_data/images/corrupt_image_file.png",
                                       "nonexistent_image_file.png",
                                       "../data/object_detection_data/images/000001679.png"])
def test_read_non_existing_image(use_cv2, image_url):
    image_full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), image_url)
    img = _read_image(ignore_data_errors=True,
                      image_url=image_full_path,
                      use_cv2=use_cv2)
    if any(prefix in image_url for prefix in ['invalid', 'corrupt', 'nonexistent']):
        # PIL manages to load corrupt images
        if 'corrupt' in image_url and not use_cv2:
            return
        assert img is None, image_url
    else:
        assert img is not None, image_url


@patch("azureml.automl.dnn.vision.common.utils.should_log_metrics_to_parent")
@mock.patch('azureml.automl.dnn.vision.common.utils._get_model_name')
def test_set_train_run_properties(mock_fun, should_log_metrics_mock):
    ds_mock = DatastoreMock('some_ds')
    ws_mock = WorkspaceMock(ds_mock)
    exp_mock = ExperimentMock(ws_mock)
    run_mock = RunMock(exp_mock)
    model_name = "some_model_name"
    best_metric = 95

    # Non pipeline run
    should_log_metrics_mock.return_value = None
    _set_train_run_properties(run_mock, model_name, best_metric)

    run_properties = run_mock.properties

    mock_fun.assert_called_once_with(run_mock.id)
    assert run_properties['runTemplate'] == 'automl_child'
    assert run_properties['run_algorithm'] == model_name
    assert run_properties[RunPropertyLiterals.PIPELINE_SCORE] == best_metric
    assert run_properties[AutoMLInferenceArtifactIDs.ModelName] is not None
    assert AutoMLInferenceArtifactIDs.ModelName in run_properties

    mock_fun.reset_mock()
    should_log_metrics_mock.reset_mock(return_value=True)

    # Pipeline run
    run_mock = RunMock(exp_mock)
    pipeline_run_mock = RunMock(exp_mock)
    should_log_metrics_mock.return_value = pipeline_run_mock
    _set_train_run_properties(run_mock, model_name, best_metric)

    run_properties = run_mock.properties
    pipeline_run_properties = pipeline_run_mock.properties
    mock_fun.assert_called_once_with(run_mock.id)
    assert run_properties == pipeline_run_properties
    assert pipeline_run_properties['runTemplate'] == 'automl_child'
    assert pipeline_run_properties['run_algorithm'] == model_name
    assert pipeline_run_properties[RunPropertyLiterals.PIPELINE_SCORE] == best_metric
    assert pipeline_run_properties[AutoMLInferenceArtifactIDs.ModelName] is not None
    assert AutoMLInferenceArtifactIDs.ModelName in run_properties


def test_round_numeric_values():
    assert utils.round_numeric_values({}, 3) == {}
    assert utils.round_numeric_values({"a": 1.11111}, 2)["a"] == 1.11
    assert utils.round_numeric_values({"a": 1.11111}, 3)["a"] == 1.111
    assert utils.round_numeric_values({"a": 1.11111}, 4)["a"] == 1.1111

    res_dict = utils.round_numeric_values({"a": 1.11111, "b": "val"}, 4)
    assert res_dict["a"] == 1.1111
    assert res_dict["b"] == "val"

    res_dict = utils.round_numeric_values({"a": "a", "b": "b"}, 1)
    assert res_dict["a"] == "a"
    assert res_dict["b"] == "b"


@patch('azureml.automl.dnn.vision.common.utils.get_dataset_from_mltable')
@patch('azureml.automl.dnn.vision.common.utils.get_dataset_from_id')
def test_get_scoring_dataset(mock_get_id, mock_get_mltable):
    datastore_name = "TestDatastoreName"
    datastore_mock = DatastoreMock(datastore_name)
    workspace_mock = WorkspaceMock(datastore_mock)
    experiment_mock = ExperimentMock(workspace_mock)
    run_mock = RunMock(experiment_mock)

    validation_id = 'validation_dataset_id'

    # MLTable
    mltable_json = 'dummy_mltable'

    with patch.object(Run, 'get_context', return_value=run_mock):

        # Call with dataset id
        expected_calls = [((validation_id, workspace_mock),)]
        dataset = utils.get_scoring_dataset(validation_id, mltable_json=None)
        assert dataset is not None
        assert mock_get_id.call_args_list == expected_calls

        # Call with both mltable and dataset id, mltable should be used
        mock_get_id.reset_mock()
        expected_calls = [
            ((mltable_json, workspace_mock, MLTableDataLabel.TestData),)]
        mock_get_mltable.return_value = dataset
        dataset = utils.get_scoring_dataset(
            validation_id, mltable_json=mltable_json)
        assert dataset is not None
        assert mock_get_mltable.call_args_list == expected_calls
        assert mock_get_id.call_args is None

        # Call with mltable TestData
        mock_get_id.reset_mock()
        mock_get_mltable.reset_mock()
        expected_calls = [
            ((mltable_json, workspace_mock, MLTableDataLabel.TestData),)]
        mock_get_mltable.return_value = dataset
        dataset = utils.get_scoring_dataset(None, mltable_json=mltable_json)
        assert dataset is not None
        assert mock_get_mltable.call_args_list == expected_calls
        assert mock_get_id.call_args is None

        # Call with mltable Valid Data
        mock_get_mltable.reset_mock()
        expected_calls = [
            ((mltable_json, workspace_mock, MLTableDataLabel.TestData),),
            ((mltable_json, workspace_mock, MLTableDataLabel.ValidData),)]
        mock_get_mltable.return_value = None
        dataset = utils.get_scoring_dataset(None, mltable_json=mltable_json)
        assert dataset is None
        assert mock_get_mltable.call_args_list == expected_calls
        assert mock_get_id.call_args is None


def test_get_dataset_from_mltable():

    datastore_name = "TestDatastoreName"
    datastore_mock = DatastoreMock(datastore_name)
    workspace_mock = WorkspaceMock(datastore_mock)

    mltable_data = dict()
    mltable_data['ResolvedUri'] = "azureml://resolveduri/uri/train"

    mltable_json = dict()
    mltable_json['Type'] = 'MLTable'
    mltable_json['TrainData'] = mltable_data

    # When get_dataset_from_mltable_data_json throws UserErrorException, ValueError
    # AutoMLVisionDataException should be thrown
    with pytest.raises(AutoMLVisionDataException) as e:
        with patch("azureml.automl.dnn.vision.common.utils.get_dataset_from_mltable_data_json",
                   side_effect=UserErrorException("Invalid MLTable.")):
            get_dataset_from_mltable(json.dumps(mltable_json), workspace_mock,
                                     MLTableDataLabel.TrainData)
    assert "MLTable input is invalid." in str(e)

    # For all other exceptions from get_dataset_from_mltable_data_json
    # AutoMLVisionSystemException should be thrown
    with pytest.raises(AutoMLVisionSystemException) as e:
        with patch("azureml.automl.dnn.vision.common.utils.get_dataset_from_mltable_data_json",
                   side_effect=Exception("Error in loading MLTable.")):
            get_dataset_from_mltable(json.dumps(mltable_json), workspace_mock,
                                     MLTableDataLabel.TrainData)
    assert "Error in loading MLTable." in str(e)


@patch('azureml.automl.dnn.vision.common.utils.get_dataset_from_mltable')
@patch('azureml.automl.dnn.vision.common.utils.get_dataset_from_id')
def test_get_tabular_dataset(mock_get_id, mock_get_mltable):

    datastore_name = "TestDatastoreName"
    datastore_mock = DatastoreMock(datastore_name)
    workspace_mock = WorkspaceMock(datastore_mock)
    experiment_mock = ExperimentMock(workspace_mock)
    run_mock = RunMock(experiment_mock)

    train_id = 'train_id'
    validation_id = 'validation_dataset_id'

    # Settings
    settings = {SettingsLiterals.DATASET_ID: train_id,
                SettingsLiterals.VALIDATION_DATASET_ID: validation_id}
    mltable_json = 'dummy_mltable'

    with patch.object(Run, 'get_context', return_value=run_mock):

        # Called with dataset ids in settings
        expected_calls = [((train_id, workspace_mock),),
                          ((validation_id, workspace_mock),)]
        train_ds, val_ds = utils.get_tabular_dataset(
            settings=settings, mltable_json=None)
        assert mock_get_id.call_args_list == expected_calls
        assert train_ds is not None
        assert val_ds is not None

        # Called with only train dataset id in settings
        mock_get_id.reset_mock()
        expected_calls = [((train_id, workspace_mock),),
                          ((None, workspace_mock),)]
        train_ds, valid_ds = utils.get_tabular_dataset(
            settings={SettingsLiterals.DATASET_ID: train_id}, mltable_json=None)
        assert train_ds is not None
        assert mock_get_id.call_args_list == expected_calls

        # Called with mltable
        mock_get_mltable.reset_mock()
        expected_calls = [((mltable_json, workspace_mock, MLTableDataLabel.TrainData),),
                          ((mltable_json, workspace_mock, MLTableDataLabel.ValidData),)]
        train_ds, valid_ds = utils.get_tabular_dataset(
            settings={}, mltable_json=mltable_json)
        assert mock_get_mltable.call_args_list == expected_calls

        # Called with both mltable and settings, mltable should be used
        mock_get_mltable.reset_mock()
        mock_get_id.reset_mock()
        expected_calls = [((mltable_json, workspace_mock, MLTableDataLabel.TrainData),),
                          ((mltable_json, workspace_mock, MLTableDataLabel.ValidData),)]
        train_ds, valid_ds = utils.get_tabular_dataset(
            settings={SettingsLiterals.DATASET_ID: train_id}, mltable_json=mltable_json)
        assert mock_get_mltable.call_args_list == expected_calls
        assert mock_get_id.call_args is None


def test_fix_tiling_settings_in_args_dict():
    # tile_grid_size not present in args_dict
    args_dict = {}
    utils.fix_tiling_settings(args_dict)
    assert TilingLiterals.TILE_GRID_SIZE not in args_dict

    # tile_grid_size present in args_dict, but None
    args_dict = {TilingLiterals.TILE_GRID_SIZE: None}
    utils.fix_tiling_settings(args_dict)
    assert args_dict[TilingLiterals.TILE_GRID_SIZE] is None

    # tile_grid_size present in args_dict and is a tuple
    args_dict = {TilingLiterals.TILE_GRID_SIZE: (3, 2)}
    utils.fix_tiling_settings(args_dict)
    assert args_dict[TilingLiterals.TILE_GRID_SIZE] == (3, 2)

    # tile_grid_size present in args_dict and is a string
    args_dict = {TilingLiterals.TILE_GRID_SIZE: "(3, 2)"}
    utils.fix_tiling_settings(args_dict)
    assert args_dict[TilingLiterals.TILE_GRID_SIZE] == (3, 2)

    # tile_grid_size present in args_dict and is in 3x2 format
    args_dict = {TilingLiterals.TILE_GRID_SIZE: "3x2"}
    utils.fix_tiling_settings(args_dict)
    assert args_dict[TilingLiterals.TILE_GRID_SIZE] == (3, 2)

    # tile_grid_size present in args_dict and is in 3X2 format
    args_dict = {TilingLiterals.TILE_GRID_SIZE: "3X2"}
    utils.fix_tiling_settings(args_dict)
    assert args_dict[TilingLiterals.TILE_GRID_SIZE] == (3, 2)


def compare_dataframes(df1, df2):
    assert len(df1) == len(df2)
    # comparing the image_url column
    assert df1.iloc[:, 0].to_list() == df2.iloc[:, 0].to_list()

    # comparing the labels column
    # since we are reading from csv, the data is stored as string and we need to convert string to json for comparison
    for i in df1.index:
        assert json.loads(df1.iloc[i, 1].replace("'", '"')) == df2.iloc[i, 1]


def test_save_image_df():
    train_annotations_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                          '../data/object_detection_data/train_annotations.json')
    val_annotations_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                        '../data/object_detection_data/valid_annotations.json')
    assert os.path.exists(train_annotations_path)
    assert os.path.exists(val_annotations_path)

    columns_to_save = ['image_url', 'label']
    train_df = pd.read_json(train_annotations_path, lines=True)
    val_df = pd.read_json(val_annotations_path, lines=True)
    train_df.rename(columns={'imageUrl': 'image_url'}, inplace=True)
    val_df.rename(columns={'imageUrl': 'image_url'}, inplace=True)

    with tempfile.TemporaryDirectory() as output_dir:
        train_csv = os.path.join(output_dir, 'train_df.csv')
        val_csv = os.path.join(output_dir, 'val_df.csv')

        # Test when both train_df and val_df is present
        _save_image_df(train_df=train_df, val_df=val_df, output_dir=output_dir)
        assert os.path.exists(train_csv)
        assert os.path.exists(val_csv)
        saved_train_df = pd.read_csv(train_csv, names=columns_to_save, sep='\t')
        saved_val_df = pd.read_csv(val_csv, names=columns_to_save, sep='\t')
        compare_dataframes(saved_train_df, train_df[columns_to_save])
        compare_dataframes(saved_val_df, val_df[columns_to_save])

    with tempfile.TemporaryDirectory() as output_dir:
        train_csv = os.path.join(output_dir, 'train_df.csv')
        val_csv = os.path.join(output_dir, 'val_df.csv')

        # Test when only train_df is present
        _save_image_df(train_df=train_df, output_dir=output_dir)
        assert os.path.exists(train_csv)
        assert not os.path.exists(val_csv)
        saved_train_df = pd.read_csv(train_csv, names=columns_to_save, sep='\t')
        compare_dataframes(saved_train_df, train_df[columns_to_save])

    with tempfile.TemporaryDirectory() as output_dir:
        train_csv = os.path.join(output_dir, 'train_df.csv')
        val_csv = os.path.join(output_dir, 'val_df.csv')

        # Test when only val_df is present
        _save_image_df(val_df=val_df, output_dir=output_dir)
        assert not os.path.exists(train_csv)
        assert os.path.exists(val_csv)
        saved_val_df = pd.read_csv(val_csv, names=columns_to_save, sep='\t')
        compare_dataframes(saved_val_df, val_df[columns_to_save])

    with tempfile.TemporaryDirectory() as output_dir:
        train_csv = os.path.join(output_dir, 'train_df.csv')
        val_csv = os.path.join(output_dir, 'val_df.csv')

        # Test with Train_indices and validation indices
        train_index = np.arange(0, 20)
        val_index = np.arange(20, 27)
        _save_image_df(train_df=train_df, train_index=train_index, val_index=val_index, output_dir=output_dir)
        assert os.path.exists(train_csv)
        assert os.path.exists(val_csv)
        saved_train_df = pd.read_csv(train_csv, names=columns_to_save, sep='\t')
        saved_val_df = pd.read_csv(val_csv, names=columns_to_save, sep='\t')
        train_df_split = train_df[0:20][columns_to_save]
        val_df_split = train_df[20:27][columns_to_save]
        compare_dataframes(saved_train_df, train_df_split)
        compare_dataframes(saved_val_df, val_df_split)


def test_set_validation_size_with_validation_size():
    automl_settings = {"validation_size": 0.15}
    args_dict = {"split_ratio": TrainingCommonSettings.DEFAULT_VALIDATION_SIZE}
    utils.set_validation_size(automl_settings, args_dict)
    assert automl_settings["validation_size"] == 0.15


def test_set_validation_size_with_split_ratio():
    automl_settings = {"validation_size": 0.0}
    args_dict = {"split_ratio": 0.15}
    utils.set_validation_size(automl_settings, args_dict)
    assert automl_settings["validation_size"] == 0.15

    automl_settings = {"validation_size": None}
    utils.set_validation_size(automl_settings, args_dict)
    assert automl_settings["validation_size"] == 0.15


def test_set_validation_size_with_default():
    automl_settings = {}
    args_dict = {"split_ratio": TrainingCommonSettings.DEFAULT_VALIDATION_SIZE}
    utils.set_validation_size(automl_settings, args_dict)
    assert automl_settings["validation_size"] == TrainingCommonSettings.DEFAULT_VALIDATION_SIZE


@pytest.mark.parametrize('tile_grid_size', ['3x2', '3X2', '(3,2)'])
def test_tile_grid_size_parser(tile_grid_size):
    settings = {'tile_grid_size': tile_grid_size}
    expected = (3, 2)
    merged_dict, _ = od_parser(automl_settings=settings)
    assert merged_dict['tile_grid_size'] == expected
    merged_dict, _ = od_yolo_parser(automl_settings=settings)
    assert merged_dict['tile_grid_size'] == expected


def test_unpack_advanced_settings_when_advanced_settings_not_specified():
    automl_settings = {}
    utils.unpack_advanced_settings(automl_settings)
    assert SettingsLiterals.STREAM_IMAGE_FILES not in automl_settings


def test_unpack_advanced_settings_invalid_json():
    automl_settings = {SettingsLiterals.ADVANCED_SETTINGS: "{"}
    utils.unpack_advanced_settings(automl_settings)
    assert SettingsLiterals.STREAM_IMAGE_FILES not in automl_settings


def test_unpack_advanced_settings_when_advanced_settings_is_not_dict():
    automl_settings = {SettingsLiterals.ADVANCED_SETTINGS: '"str"'}
    utils.unpack_advanced_settings(automl_settings)
    assert SettingsLiterals.STREAM_IMAGE_FILES not in automl_settings


def test_unpack_advanced_settings_stream_images_true():
    automl_settings = {SettingsLiterals.ADVANCED_SETTINGS: '{"stream_image_files": true}'}
    utils.unpack_advanced_settings(automl_settings)
    assert automl_settings[SettingsLiterals.STREAM_IMAGE_FILES] is True


@pytest.mark.parametrize('advanced_settings_parameter', [
    SettingsLiterals.APPLY_AUTOML_TRAIN_AUGMENTATIONS, SettingsLiterals.APPLY_MOSAIC_FOR_YOLO])
def test_unpack_advanced_settings_parameters(advanced_settings_parameter):
    automl_settings = {SettingsLiterals.ADVANCED_SETTINGS: json.dumps({advanced_settings_parameter: True})}
    utils.unpack_advanced_settings(automl_settings)
    assert automl_settings[advanced_settings_parameter] is True

    automl_settings = {SettingsLiterals.ADVANCED_SETTINGS: json.dumps({advanced_settings_parameter: False})}
    utils.unpack_advanced_settings(automl_settings)
    assert automl_settings[advanced_settings_parameter] is False

    automl_settings = {SettingsLiterals.ADVANCED_SETTINGS: json.dumps({advanced_settings_parameter: 'test'})}
    utils.unpack_advanced_settings(automl_settings)
    assert automl_settings[advanced_settings_parameter] is True

    automl_settings = {SettingsLiterals.ADVANCED_SETTINGS: {}}
    utils.unpack_advanced_settings(automl_settings)
    assert advanced_settings_parameter not in automl_settings


def test_unpack_advanced_settings_stream_images_non_true_input():
    automl_settings = {SettingsLiterals.ADVANCED_SETTINGS: '{"stream_image_files": "hi"}'}
    utils.unpack_advanced_settings(automl_settings)
    assert automl_settings[SettingsLiterals.STREAM_IMAGE_FILES] is False


@patch("azureml.automl.dnn.vision.common.aml_dataset_base_wrapper.AmlDatasetBaseWrapper.download_image_files")
def test_download_or_mount_image_files_download_images(mock_download_image_files):
    utils.download_or_mount_image_files(
        settings={SettingsLiterals.STREAM_IMAGE_FILES: False},
        train_ds=MagicMock(),
        validation_ds=MagicMock(),
        dataset_class=AmlDatasetBaseWrapper,
        workspace=None)
    # Assert that download invoked twice, once for train dataset and once for validation
    assert mock_download_image_files.call_count == 2


@patch("azureml.automl.dnn.vision.common.aml_dataset_base_wrapper.AmlDatasetBaseWrapper.mount_image_file_datastores")
def test_download_or_mount_image_files_mount_images(mock_mount_image_file_datastores):
    utils.download_or_mount_image_files(
        settings={SettingsLiterals.STREAM_IMAGE_FILES: True},
        train_ds=MagicMock(),
        validation_ds=MagicMock(),
        dataset_class=AmlDatasetBaseWrapper,
        workspace=None)
    # Assert that mount invoked twice, once for train dataset and once for validation
    assert mock_mount_image_file_datastores.call_count == 2


@patch("azureml.automl.dnn.vision.common.aml_dataset_base_wrapper.AmlDatasetBaseWrapper.download_image_files")
def test_download_or_mount_image_files_download_images_when_validation_data_absent(mock_download_image_files):
    utils.download_or_mount_image_files(
        settings={SettingsLiterals.STREAM_IMAGE_FILES: False},
        train_ds=MagicMock(),
        validation_ds=None,
        dataset_class=AmlDatasetBaseWrapper,
        workspace=None)
    # Assert that download invoked once, only for train dataset
    assert mock_download_image_files.call_count == 1


@patch("azureml.automl.dnn.vision.common.aml_dataset_base_wrapper.AmlDatasetBaseWrapper.mount_image_file_datastores")
def test_download_or_mount_image_files_mount_images_when_validation_data_absent(mock_mount_image_file_datastores):
    utils.download_or_mount_image_files(
        settings={SettingsLiterals.STREAM_IMAGE_FILES: True},
        train_ds=MagicMock(),
        validation_ds=None,
        dataset_class=AmlDatasetBaseWrapper,
        workspace=None)
    # Assert that mount invoked once, only for train dataset
    assert mock_mount_image_file_datastores.call_count == 1


@patch("azureml.automl.dnn.vision.common.aml_dataset_base_wrapper.AmlDatasetBaseWrapper.download_image_files")
def test_download_or_mount_image_files_when_train_dataset_absent(mock_download_image_files):
    utils.download_or_mount_image_files(
        settings={SettingsLiterals.STREAM_IMAGE_FILES: False},
        train_ds=None,
        validation_ds=None,
        dataset_class=AmlDatasetBaseWrapper,
        workspace=None)
    # If train dataset is None, assert that no files were downloaded
    mock_download_image_files.assert_not_called()


def test_convert_type_to_int():
    assert utils._convert_type_to_int('4.0') == 4
    assert utils._convert_type_to_int('4') == 4
    assert utils._convert_type_to_int(4) == 4
    assert utils._convert_type_to_int(4.0) == 4
    with pytest.raises(ValueError, match='4.5 is not a valid int'):
        utils._convert_type_to_int(4.5)
    with pytest.raises(ValueError, match='4.5 is not a valid int'):
        utils._convert_type_to_int('4.5')
    with pytest.raises(ValueError, match='could not convert string to float'):
        utils._convert_type_to_int('test string')
    with pytest.raises(ValueError, match='could not convert string to float'):
        utils._convert_type_to_int('false')
    with pytest.raises(ValueError, match='could not convert string to float'):
        utils._convert_type_to_int('True')


def test_set_run_traits_stream_image_files():
    azureml_run = MagicMock()

    utils.set_run_traits(azureml_run, {})
    azureml_run._client.patch_run.assert_not_called()

    utils.set_run_traits(azureml_run, {SettingsLiterals.STREAM_IMAGE_FILES: False})
    azureml_run._client.patch_run.assert_not_called()

    utils.set_run_traits(azureml_run, {SettingsLiterals.STREAM_IMAGE_FILES: True})
    azureml_run._client.patch_run.assert_called_once()
    assert azureml_run._client.patch_run.mock_calls[0][1][0].run_type_v2.traits == ['stream_image_files']


@patch("azureml.automl.core.shared.logging_utilities.log_traceback")
@patch("azureml.automl.dnn.vision.common.distributed_utils.master_process", side_effect=Exception)
def test_set_run_traits_exception(_, mock_log_traceback):
    utils.set_run_traits(MagicMock(), {})
    mock_log_traceback.assert_called()


@mock.patch("azureml.core.run.Run")
def test_should_log_metrics_to_parent(mock_run):

    datastore_name = "TestDatastoreName"
    datastore_mock = DatastoreMock(datastore_name)
    workspace_mock = WorkspaceMock(datastore_mock)
    experiment_mock = ExperimentMock(workspace_mock)

    # Setup pipeline parent mock
    pipeline_parent_run_mock = RunMock(experiment_mock)
    pipeline_parent_run_mock.type = "azureml.PipelineRun"

    # Setup hyperdrive parent mock
    hyperdrive_parent_run_mock = RunMock(experiment_mock)
    hyperdrive_parent_run_mock.type = "hyperdrive"

    # No parent run
    parent = utils.should_log_metrics_to_parent(mock_run)
    assert not parent

    # Set parent run to pipeline
    mock_run.parent = pipeline_parent_run_mock
    parent = utils.should_log_metrics_to_parent(mock_run)
    assert parent

    # Set parent run to hyperdrive
    mock_run.parent = hyperdrive_parent_run_mock
    parent = utils.should_log_metrics_to_parent(mock_run)
    assert not parent


@mock.patch("azureml.core.run.Run.log_confusion_matrix")
@mock.patch("azureml.core.run.Run.log_row")
@mock.patch("azureml.core.run.Run")
@pytest.mark.parametrize("include_training", [False, True])
def test_detailed_object_detection_metrics(mock_run, mock_log_row, mock_log_confusion_matrix, include_training):
    mock_run.return_value = None
    mock_log_row.return_value = None

    metrics = {
        MetricsLiterals.PRECISION: 0.7,
        MetricsLiterals.RECALL: 0.8,
        MetricsLiterals.MEAN_AVERAGE_PRECISION: 0.9,
        MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD: {0.25: 0.33, 0.5: 0.5, 0.75: 0.66},
        MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD: {0.25: 0.66, 0.5: 0.5, 0.75: 0.33},
        MetricsLiterals.PER_LABEL_METRICS: {
            0: {
                "precision": 0.1, "recall": 0.2, "average_precision": 0.3,
                "precisions_per_score_threshold": {0.1: 1.0, 0.15: 1.0},
                "recalls_per_score_threshold": {0.1: 1.0, 0.15: 1.0},
            },
            1: {
                "precision": 0.2, "recall": 0.3, "average_precision": 0.4,
                "precisions_per_score_threshold": {0.2: 1.0, 0.25: 1.0},
                "recalls_per_score_threshold": {0.2: 1.0, 0.25: 1.0},
            },
            2: {
                "precision": 0.3, "recall": 0.4, "average_precision": 0.5,
                "precisions_per_score_threshold": {0.3: 1.0, 0.35: 1.0},
                "recalls_per_score_threshold": {0.3: 1.0, 0.35: 1.0},
            },
        },
        MetricsLiterals.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS: {
            "precision": 0.5, "recall": 0.6, "average_precision": 0.7
        },
        MetricsLiterals.CONFUSION_MATRICES_PER_SCORE_THRESHOLD: {
            0.1: [[3, 2, 3, 2], [4, 3, 4, 3], [5, 4, 5, 4]],
            0.2: [[2, 2, 3, 3], [3, 3, 4, 4], [4, 4, 5, 5]],
            0.3: [[1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6]],
        }
    }
    if include_training:
        metrics[MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD + "_train"] = {0.15: 0.33, 0.4: 0.5, 0.65: 0.66}
        metrics[MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD + "_train"] = {0.15: 0.66, 0.4: 0.5, 0.65: 0.33}
        metrics[MetricsLiterals.PER_LABEL_METRICS + "_train"] = {
            0: {
                "precision": 0.2, "recall": 0.3, "average_precision": 0.4,
                "precisions_per_score_threshold": {0.1: 0.5, 0.15: 0.5},
                "recalls_per_score_threshold": {0.1: 0.5, 0.15: 0.5},
            },
            1: {
                "precision": 0.3, "recall": 0.4, "average_precision": 0.5,
                "precisions_per_score_threshold": {0.2: 0.5, 0.25: 0.5},
                "recalls_per_score_threshold": {0.2: 0.5, 0.25: 0.5}
            },
            2: {
                "precision": 0.4, "recall": 0.5, "average_precision": 0.6,
                "precisions_per_score_threshold": {0.3: 0.5, 0.35: 0.5},
                "recalls_per_score_threshold": {0.3: 0.5, 0.35: 0.5},
            },
        }
        metrics[MetricsLiterals.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS + "_train"] = {
            "precision": 0.6, "recall": 0.7, "average_precision": 0.8
        }
        metrics[MetricsLiterals.CONFUSION_MATRICES_PER_SCORE_THRESHOLD + "_train"] = {
            0.1: [[4, 3, 4, 3], [5, 4, 5, 4], [6, 5, 6, 5]],
            0.2: [[3, 3, 4, 4], [4, 4, 5, 5], [5, 5, 6, 6]],
            0.3: [[2, 3, 4, 5], [3, 4, 5, 6], [4, 5, 6, 7]],
        }

    utils.log_detailed_object_detection_metrics(metrics, mock_run, ["dog", "cat", "axolotl"])

    global_pr_calls = [
        call("pr_curve", recall=0.66, precision=0.33, score_threshold=0.25),
        call("pr_curve", recall=0.5, precision=0.5, score_threshold=0.5),
        call("pr_curve", recall=0.33, precision=0.66, score_threshold=0.75)
    ]
    per_label_calls = [
        call(MetricsLiterals.PER_LABEL_METRICS, class_name="dog", precision=0.1, recall=0.2, average_precision=0.3),
        call("pr_curve_dog", recall=1.0, precision=1.0, score_threshold=0.1),
        call("pr_curve_dog", recall=1.0, precision=1.0, score_threshold=0.15),
        call(MetricsLiterals.PER_LABEL_METRICS, class_name="cat", precision=0.2, recall=0.3, average_precision=0.4),
        call("pr_curve_cat", recall=1.0, precision=1.0, score_threshold=0.2),
        call("pr_curve_cat", recall=1.0, precision=1.0, score_threshold=0.25),
        call(
            MetricsLiterals.PER_LABEL_METRICS, class_name="axolotl", precision=0.3, recall=0.4, average_precision=0.5
        ),
        call("pr_curve_axolotl", recall=1.0, precision=1.0, score_threshold=0.3),
        call("pr_curve_axolotl", recall=1.0, precision=1.0, score_threshold=0.35),
    ]
    image_level_calls = [
        call(MetricsLiterals.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS, precision=0.5, recall=0.6, average_precision=0.7)
    ]
    confusion_matrix_calls = [
        call(
            "confusion_matrix_score_threshold_0.1",
            {
                "schema_type": "confusion_matrix",
                "schema_version": "1.0.0",
                "data": {
                    "class_labels": ["dog", "cat", "axolotl", "Missed"],
                    "matrix": [[3, 2, 3, 2], [4, 3, 4, 3], [5, 4, 5, 4], ["N/A", "N/A", "N/A", "N/A"]]
                }
            }
        ),
        call(
            "confusion_matrix_score_threshold_0.2",
            {
                "schema_type": "confusion_matrix",
                "schema_version": "1.0.0",
                "data": {
                    "class_labels": ["dog", "cat", "axolotl", "Missed"],
                    "matrix": [[2, 2, 3, 3], [3, 3, 4, 4], [4, 4, 5, 5], ["N/A", "N/A", "N/A", "N/A"]]
                }
            }
        ),
        call(
            "confusion_matrix_score_threshold_0.3",
            {
                "schema_type": "confusion_matrix",
                "schema_version": "1.0.0",
                "data": {
                    "class_labels": ["dog", "cat", "axolotl", "Missed"],
                    "matrix": [[1, 2, 3, 4], [2, 3, 4, 5], [3, 4, 5, 6], ["N/A", "N/A", "N/A", "N/A"]]
                }
            }
        )
    ]
    if include_training:
        global_pr_calls += [
            call("pr_curve_train", recall=0.66, precision=0.33, score_threshold=0.15),
            call("pr_curve_train", recall=0.5, precision=0.5, score_threshold=0.4),
            call("pr_curve_train", recall=0.33, precision=0.66, score_threshold=0.65)
        ]
        per_label_calls += [
            call(
                MetricsLiterals.PER_LABEL_METRICS + "_train",
                class_name="dog", precision=0.2, recall=0.3, average_precision=0.4
            ),
            call("pr_curve_train_dog", recall=0.5, precision=0.5, score_threshold=0.1),
            call("pr_curve_train_dog", recall=0.5, precision=0.5, score_threshold=0.15),
            call(
                MetricsLiterals.PER_LABEL_METRICS + "_train",
                class_name="cat", precision=0.3, recall=0.4, average_precision=0.5
            ),
            call("pr_curve_train_cat", recall=0.5, precision=0.5, score_threshold=0.2),
            call("pr_curve_train_cat", recall=0.5, precision=0.5, score_threshold=0.25),
            call(
                MetricsLiterals.PER_LABEL_METRICS + "_train",
                class_name="axolotl", precision=0.4, recall=0.5, average_precision=0.6
            ),
            call("pr_curve_train_axolotl", recall=0.5, precision=0.5, score_threshold=0.3),
            call("pr_curve_train_axolotl", recall=0.5, precision=0.5, score_threshold=0.35),
        ]
        image_level_calls += [
            call(
                MetricsLiterals.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS + "_train",
                precision=0.6, recall=0.7, average_precision=0.8
            )
        ]
        confusion_matrix_calls += [
            call(
                "confusion_matrix_train_score_threshold_0.1",
                {
                    "schema_type": "confusion_matrix",
                    "schema_version": "1.0.0",
                    "data": {
                        "class_labels": ["dog", "cat", "axolotl", "Missed"],
                        "matrix": [[4, 3, 4, 3], [5, 4, 5, 4], [6, 5, 6, 5], ["N/A", "N/A", "N/A", "N/A"]]
                    }
                }
            ),
            call(
                "confusion_matrix_train_score_threshold_0.2",
                {
                    "schema_type": "confusion_matrix",
                    "schema_version": "1.0.0",
                    "data": {
                        "class_labels": ["dog", "cat", "axolotl", "Missed"],
                        "matrix": [[3, 3, 4, 4], [4, 4, 5, 5], [5, 5, 6, 6], ["N/A", "N/A", "N/A", "N/A"]]
                    }
                }
            ),
            call(
                "confusion_matrix_train_score_threshold_0.3",
                {
                    "schema_type": "confusion_matrix",
                    "schema_version": "1.0.0",
                    "data": {
                        "class_labels": ["dog", "cat", "axolotl", "Missed"],
                        "matrix": [[2, 3, 4, 5], [3, 4, 5, 6], [4, 5, 6, 7], ["N/A", "N/A", "N/A", "N/A"]]
                    }
                }
            )
        ]

    mock_log_row.assert_has_calls(global_pr_calls + per_label_calls + image_level_calls, any_order=True)
    mock_log_confusion_matrix.assert_has_calls(confusion_matrix_calls, any_order=True)


@mock.patch("azureml.core.run.Run.log_confusion_matrix")
@mock.patch("azureml.core.run.Run.log_row")
@mock.patch("azureml.core.run.Run")
def test_detailed_object_detection_metrics_zero_classes(mock_run, mock_log_row, mock_log_confusion_matrix):
    mock_run.return_value = None
    mock_log_row.return_value = None

    metrics = {
        MetricsLiterals.PRECISION: -1.0,
        MetricsLiterals.RECALL: -1.0,
        MetricsLiterals.MEAN_AVERAGE_PRECISION: -1.0,
        MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD: {st / 100.0: -1.0 for st in range(100)},
        MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD: {st / 100.0: -1.0 for st in range(100)},
        MetricsLiterals.PER_LABEL_METRICS: {},
        MetricsLiterals.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS: {
            "precision": -1.0, "recall": -1.0, "average_precision": -1.0
        },
        MetricsLiterals.CONFUSION_MATRICES_PER_SCORE_THRESHOLD: {
            -1.0: []
        }
    }

    utils.log_detailed_object_detection_metrics(metrics, mock_run, [])

    image_level_calls = [
        call(
            MetricsLiterals.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS, precision=-1.0, recall=-1.0, average_precision=-1.0
        )
    ]

    mock_log_row.assert_has_calls(image_level_calls, any_order=True)
    assert mock_log_row.call_count == len(image_level_calls)

    mock_log_confusion_matrix.assert_not_called()


@patch("torch.cuda.is_available", return_value=True)
@patch("azureml.automl.dnn.vision.common.distributed_utils.master_process", return_value=True)
@patch("pynvml.nvmlInit")
@patch("pynvml.nvmlDeviceGetCount", return_value=1)
@patch("pynvml.nvmlDeviceGetName", return_value='test_gpu_device')
@patch("pynvml.nvmlDeviceGetHandleByIndex")
@patch("pynvml.nvmlShutdown")
def test_validate_gpu_sku(mockshutdown, mockhandle, mockdevicename, mockcount, mocknvmlinit, mock_utils, _):
    with patch("pynvml.nvmlDeviceGetMemoryInfo",
               return_value=SimpleNamespace(total=1400 * MEGABYTE, free=1320 * MEGABYTE)):
        with pytest.raises(AutoMLVisionValidationException,
                           match=r"mem_info_total:\(\d+\.\d+ MB\) is smaller than min_gpu_mem:\(\d+\.\d+ MB\)"):
            validate_gpu_sku(device='gpu')

    with patch("pynvml.nvmlDeviceGetMemoryInfo",
               return_value=SimpleNamespace(total=11400 * MEGABYTE, free=10320 * MEGABYTE)):
        with pytest.raises(AutoMLVisionValidationException,
                           match=r"mem_info_free:\(\d+\.\d+ MB\) is smaller than min_free_gpu_mem:\(\d+\.\d+ MB\)"):
            validate_gpu_sku(device='gpu')

    with patch("pynvml.nvmlDeviceGetMemoryInfo",
               return_value=SimpleNamespace(total=11400 * MEGABYTE, free=11320 * MEGABYTE)):
        validate_gpu_sku(device='gpu')


@patch('azureml.automl.dnn.vision.common.distributed_utils._get_node_count')
def test_launch_training_with_retries(node_count_mock):
    mltable_data_json = "dummy_mltable_data_json"
    multilabel = False
    logger = logging.getLogger("test_common_methods")
    additional_train_worker_args = (mltable_data_json, multilabel)
    train_worker_fn = classification_runner.train_worker
    node_count_mock.return_value = 1

    cpu_oom_exception = ResourceException._with_error(AzureMLError.create(InsufficientMemory))
    resource_exception_non_cpu = ResourceException._with_error(AzureMLError.create(InsufficientGPUMemory))
    generic_exception = Exception("dummy_exception")

    def _test(launch_settings, exception_to_raise, expected_exception, expected_modified_settings, expected_retry):
        with patch('azureml.automl.dnn.vision.common.distributed_utils.launch_single_or_distributed_training') as \
                mock_launch_fn:
            if exception_to_raise is not None:
                mock_launch_fn.side_effect = exception_to_raise

            if expected_exception is not None:
                with pytest.raises(type(expected_exception)):
                    # Use __wrapped__ to the test the function without cpu_oom_retry_handler decorator
                    launch_training_with_retries.__wrapped__(launch_settings, train_worker_fn,
                                                             additional_train_worker_args,
                                                             logger, None)
            else:
                # Use __wrapped__ to the test the function without cpu_oom_retry_handler decorator
                retry = launch_training_with_retries.__wrapped__(launch_settings, train_worker_fn,
                                                                 additional_train_worker_args, logger, None)
                mock_launch_fn.assert_called_once()
                assert launch_settings == expected_modified_settings
                assert retry == expected_retry

    # Launch doesn't raise an exception -> No exception, no retry
    settings = {
        DistributedLiterals.DISTRIBUTED: True,
        SettingsLiterals.NUM_WORKERS: 4,
    }
    expected_settings = copy.deepcopy(settings)
    _test(settings, None, None, expected_settings, False)

    # Launch raises cpu oom exception with distributed is True -> No exception, retry with distributed as False
    settings = {
        DistributedLiterals.DISTRIBUTED: True,
        SettingsLiterals.NUM_WORKERS: 4,
    }
    expected_settings = copy.deepcopy(settings)
    expected_settings[DistributedLiterals.DISTRIBUTED] = False
    expected_settings[SettingsLiterals.RESUME_FROM_STATE] = True
    _test(settings, cpu_oom_exception, None, expected_settings, True)

    # Launch raises cpu oom exception with distributed is False and num_workers > 0 ->
    # No exception, retry with num_workers as 0
    settings = {
        DistributedLiterals.DISTRIBUTED: False,
        SettingsLiterals.NUM_WORKERS: 4,
    }
    expected_settings = copy.deepcopy(settings)
    expected_settings[SettingsLiterals.NUM_WORKERS] = 0
    expected_settings[SettingsLiterals.RESUME_FROM_STATE] = True
    _test(settings, cpu_oom_exception, None, expected_settings, True)

    # Launch raises cpu oom exception with distributed is False and num_workers == 0 -> Exception
    settings = {
        DistributedLiterals.DISTRIBUTED: False,
        SettingsLiterals.NUM_WORKERS: 0,
    }
    expected_settings = copy.deepcopy(settings)
    _test(settings, cpu_oom_exception, cpu_oom_exception, expected_settings, False)

    # Launch raises generic exception with distributed is True and num_workers > 0 -> Exception
    settings = {
        DistributedLiterals.DISTRIBUTED: True,
        SettingsLiterals.NUM_WORKERS: 4,
    }
    expected_settings = copy.deepcopy(settings)
    _test(settings, generic_exception, generic_exception, expected_settings, False)

    # Launch raises non cpu resource exception with distributed is True and num_workers > 0 -> Exception
    settings = {
        DistributedLiterals.DISTRIBUTED: True,
        SettingsLiterals.NUM_WORKERS: 4,
    }
    expected_settings = copy.deepcopy(settings)
    _test(settings, resource_exception_non_cpu, resource_exception_non_cpu, expected_settings, False)

    # Launch raises cpu resource exception with distributed is True and num_workers > 0, but in multi-node setting
    # -> Exception
    node_count_mock.return_value = 4
    settings = {
        DistributedLiterals.DISTRIBUTED: True,
        SettingsLiterals.NUM_WORKERS: 4,
    }
    expected_settings = copy.deepcopy(settings)
    _test(settings, cpu_oom_exception, cpu_oom_exception, expected_settings, False)


if __name__ == "__main__":
    pytest.main([__file__])
