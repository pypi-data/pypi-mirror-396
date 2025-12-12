# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for model export utils methods."""
import os
import json

import pytest
import tempfile
import unittest.mock as mock

from azureml.train.automl import constants
from azureml.automl.core.inference import inference

import azureml.automl.core.shared.constants as shared_constants
import azureml.automl.dnn.vision.common.model_export_utils as model_utils

from azureml.automl.dnn.vision.classification.models import ModelFactory as ClassificationModelFactory
from azureml.automl.dnn.vision.common.artifacts_utils import save_model_checkpoint
from azureml.automl.dnn.vision.common.constants import ScoringLiterals
from azureml.automl.dnn.vision.object_detection.models.object_detection_model_wrappers \
    import ObjectDetectionModelFactory
from azureml.automl.dnn.vision.object_detection_yolo.common.constants\
    import YoloLiterals, YoloParameters
from azureml.automl.dnn.vision.object_detection_yolo.models.yolo_wrapper import YoloV5Wrapper

from tests.common.run_mock import RunMock, ExperimentMock, WorkspaceMock, DatastoreMock


class TestModelExportUtils:

    @staticmethod
    def _setup_mock_run():
        ds_mock = DatastoreMock("test_dataset_name")
        ws_mock = WorkspaceMock(ds_mock)
        exp_mock = ExperimentMock(ws_mock)
        return RunMock(exp_mock)

    @mock.patch('azureml.train.automl.runtime._azureautomlruncontext.AzureAutoMLRunContext._get_artifact_id')
    @mock.patch('azureml.train.automl.runtime._azureautomlruncontext.AzureAutoMLRunContext.batch_save_artifacts')
    @mock.patch(model_utils.__name__ + '._get_scoring_file')
    @mock.patch(model_utils.__name__ + '._create_conda_env_file_content')
    def test_prepare_model_export(self, mock_conda_env_file, mock_get_scoring,
                                  mock_batch_save, mock_get_artifacts):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            run_mock = self._setup_mock_run()
            score_file_path = os.path.join('test_artifacts', shared_constants.SCORING_FILE_PATH)
            conda_file_path = os.path.join('test_artifacts', shared_constants.SCORING_FILE_PATH)
            model_path = os.path.join('test_artifacts', shared_constants.PT_MODEL_FILENAME)

            # set up mocked methods' return values
            mock_conda_env_file.return_value = "test_conda_env"
            mock_get_scoring.return_value = "test_score_content"
            mock_get_artifacts.side_effect = [score_file_path, conda_file_path, model_path]

            # create a model
            model_name = 'seresnext'
            model_wrapper = ClassificationModelFactory().get_model_wrapper(model_name=model_name,
                                                                           num_classes=10,
                                                                           multilabel=False,
                                                                           device='cpu',
                                                                           distributed=False,
                                                                           local_rank=0)
            # save the model wrapper
            specs = {
                'multilabel': model_wrapper.multilabel,
                'model_settings': model_wrapper.model_settings,
                'labels': model_wrapper.labels
            }
            save_model_checkpoint(epoch=1,
                                  model_name=model_name,
                                  number_of_classes=model_wrapper.number_of_classes,
                                  specs=specs,
                                  model_state=model_wrapper.state_dict(),
                                  optimizer_state={},
                                  lr_scheduler_state={},
                                  score=0.0,
                                  metrics={},
                                  output_dir=tmp_output_dir)

            # call method
            model_utils.prepare_model_export(run_mock,
                                             output_dir=tmp_output_dir,
                                             task_type=constants.Tasks.IMAGE_OBJECT_DETECTION,)

            # Assert methods called
            mock_conda_env_file.assert_called_once_with(run_mock)
            mock_get_scoring.assert_called_once_with(run=run_mock,
                                                     task_type=constants.Tasks.IMAGE_OBJECT_DETECTION,
                                                     model_settings={},
                                                     is_yolo=False)
            mock_batch_save.assert_called_once()
            mock_get_artifacts.assert_called()

            # Assert properties added to run
            expected_properties = {
                inference.AutoMLInferenceArtifactIDs.ScoringDataLocation: score_file_path,
                inference.AutoMLInferenceArtifactIDs.CondaEnvDataLocation: conda_file_path,
                inference.AutoMLInferenceArtifactIDs.ModelDataLocation: model_path
            }
            assert run_mock.properties == expected_properties

    def test_create_conda_env_file_content(self):
        run_mock = self._setup_mock_run()
        conda_file_content = model_utils._create_conda_env_file_content(run_mock)
        for package in inference.AutoMLVisionCondaPackagesList:
            assert package in conda_file_content

    @pytest.mark.parametrize('is_yolo', [True, False])
    @pytest.mark.parametrize('task_type', constants.Tasks.ALL_IMAGE)
    @pytest.mark.parametrize('model_settings', [{'test_settings': 'test_val'}, {'test_settings': None}, None])
    def test_get_scoring_file_od(self, is_yolo, task_type, model_settings):
        run_mock = self._setup_mock_run()
        score_file_content = model_utils._get_scoring_file(run_mock, task_type, model_settings, is_yolo)
        assert task_type in score_file_content
        assert json.dumps(model_settings or {}).replace('null', 'None') in score_file_content
        # this happens if model_settings is passed as None
        assert 'null' not in score_file_content

        if task_type in constants.Tasks.ALL_IMAGE_CLASSIFICATION:
            assert 'classification.inference' in score_file_content
        elif is_yolo:
            assert 'object_detection_yolo.writers' in score_file_content
        else:
            assert 'object_detection.writers' in score_file_content

    @mock.patch('azureml.automl.dnn.vision.classification.common.classification_utils._load_model_wrapper')
    @mock.patch('azureml.automl.dnn.vision.object_detection.common.object_detection_utils._load_model_wrapper')
    @pytest.mark.parametrize('task_type', constants.Tasks.ALL_IMAGE)
    def test_load_model(self, mock_od_utils, mock_classification_utils, task_type):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            model_settings = {'test_settings': 'test_val'}

            mock_classification_utils.return_value = 'classification_model_wrapper'
            mock_od_utils.return_value = 'od_model_wrapper'

            load_output = model_utils.load_model(task_type, tmp_output_dir, **model_settings)

            if task_type in constants.Tasks.ALL_IMAGE_CLASSIFICATION:
                mock_classification_utils.assert_called_once()
                mock_od_utils.assert_not_called()
                assert load_output == 'classification_model_wrapper'
            else:
                mock_od_utils.assert_called_once()
                mock_classification_utils.assert_not_called()
                assert load_output == 'od_model_wrapper'

    @pytest.mark.parametrize('task_type, is_yolo', (
        [constants.Tasks.IMAGE_CLASSIFICATION, False],
        [constants.Tasks.IMAGE_OBJECT_DETECTION, False],
        [constants.Tasks.IMAGE_OBJECT_DETECTION, True]))
    def test_inference_batch(self, task_type, is_yolo):
        image_path_list = [os.path.join(os.path.dirname(__file__),
                           '../data/object_detection_data/images/000001030.png')]
        score_with_model = model_utils._get_scoring_method(task_type, is_yolo=is_yolo)
        # create a model
        if task_type == constants.Tasks.IMAGE_CLASSIFICATION:
            model_name = 'seresnext'
            model_wrapper = ClassificationModelFactory().get_model_wrapper(model_name=model_name,
                                                                           num_classes=10,
                                                                           multilabel=False,
                                                                           device='cpu',
                                                                           distributed=False,
                                                                           local_rank=0)
        elif not is_yolo:
            model_name = 'fasterrcnn_resnet18_fpn'
            model_wrapper = ObjectDetectionModelFactory().get_model_wrapper(number_of_classes=10)
        else:
            model_name = 'yolov5'
            specs = \
                {
                    'model_size' : 'medium',
                    'device' : 'cpu',
                    YoloLiterals.IMG_SIZE : 640,
                    YoloLiterals.BOX_SCORE_THRESH : YoloParameters.DEFAULT_BOX_SCORE_THRESH,
                    YoloLiterals.NMS_IOU_THRESH : YoloParameters.DEFAULT_NMS_IOU_THRESH
                }
            model_wrapper = YoloV5Wrapper(model_name=model_name, number_of_classes=10, specs=specs)

        model_utils.run_inference_batch(model_wrapper, image_path_list, score_with_model=score_with_model)

        # run_inference_batch is used by yhe mlflow wrappper. During inference our scripts
        # should not write to any files as we dont have write permissions.
        # check all outputs are written in temporary files and below files are not created.

        output_file = os.path.join(ScoringLiterals.DEFAULT_OUTPUT_DIR,
                                   ScoringLiterals.PREDICTION_FILE_NAME)
        labeled_dataset_file = os.path.join(ScoringLiterals.DEFAULT_OUTPUT_DIR,
                                            ScoringLiterals.LABELED_DATASET_FILE_NAME)
        assert not (os.path.isfile(output_file) or os.path.isfile(labeled_dataset_file))
