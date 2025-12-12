import numpy as np
import os
import pytest
import tempfile
import torch
import unittest.mock as mock

import azureml.automl.dnn.vision.object_detection.common.object_detection_utils as od_utils

from azureml.automl.dnn.vision.common.constants import MetricsLiterals
from azureml.automl.dnn.vision.object_detection.data.datasets import AmlDatasetObjectDetection
from azureml.automl.dnn.vision.object_detection.data.dataset_wrappers import \
    CommonObjectDetectionDatasetWrapper, DatasetProcessingType
from azureml.automl.dnn.vision.object_detection.eval.incremental_voc_evaluator import IncrementalVocEvaluator

from ..common.run_mock import DatasetMock, RunMock, ExperimentMock, DatastoreMock, WorkspaceMock
from .test_datasets import _build_aml_dataset_object_detection


def _convert_numbers_to_tensors(m):
    return {
        k: torch.tensor(v) if isinstance(v, float)
        else [torch.tensor(x) for x in v] if isinstance(v, list)
        else _convert_numbers_to_tensors(v)
        for k, v in m.items()
    }


@pytest.mark.usefixtures('new_clean_dir')
class TestObjectDetectionUtils:

    @staticmethod
    def _setup_wrapper(only_one_file=False):
        ws_mock, mock_dataset, _, _ = _build_aml_dataset_object_detection(only_one_file)
        AmlDatasetObjectDetection.download_image_files(mock_dataset)
        dataset_mock = AmlDatasetObjectDetection(mock_dataset)
        wrapper_mock = CommonObjectDetectionDatasetWrapper(dataset_mock, DatasetProcessingType.IMAGES)
        return ws_mock, mock_dataset, wrapper_mock

    @staticmethod
    def _write_output_file(output_file, only_one_file=False):
        with open(output_file, 'w') as f:
            line1 = '{"filename": "a7c014ec-474a-49f4-8ae3-09049c701913-1.txt", ' \
                    '"boxes": [{"box": {"topX": 0.1, "topY": 0.9, "bottomX": 0.2, "bottomY": 0.8}, ' \
                    '"label": "cat", "score": 0.7}]}'
            line2 = '{"filename": "a7c014ec-474a-49f4-8ae3-09049c701913-2", ' \
                    '"boxes": [{"box": {"topX": 0.5, "topY": 0.5, "bottomX": 0.6, "bottomY": 0.4}, '\
                    '"label": "dog", "score": 0.8}]}'
            f.write(line1 + '\n')
            f.write(line2 + '\n')

    @pytest.mark.parametrize("data_type", ["numbers", "tensors"])
    def test_update_with_voc_metrics_simple(self, data_type):
        current_metrics = {}
        cumulative_per_label_metrics = {}

        voc_metrics = {
            MetricsLiterals.PRECISION: 0.35,
            MetricsLiterals.RECALL: 0.65,
            MetricsLiterals.MEAN_AVERAGE_PRECISION: 0.5,
            MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD: {0.2: 0.5, 0.4: 0.6, 0.6: 0.7, 0.8: 0.8},
            MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD: {0.2: 0.5, 0.4: 0.4, 0.6: 0.3, 0.8: 0.2},
            MetricsLiterals.PER_LABEL_METRICS: {
                0: {
                    MetricsLiterals.PRECISION: 0.3,
                    MetricsLiterals.RECALL: 0.7,
                    MetricsLiterals.AVERAGE_PRECISION: 0.25,
                    MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD: {0.1: 0.2, 0.3: 0.4},
                    MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD: {0.1: 0.5, 0.3: 0.6},
                },
                1: {
                    MetricsLiterals.PRECISION: 0.4,
                    MetricsLiterals.RECALL: 0.6,
                    MetricsLiterals.AVERAGE_PRECISION: 0.75,
                    MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD: {0.1: 0.7, 0.3: 0.8},
                    MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD: {0.1: 0.9, 0.3: 1.0},
                }
            },
            MetricsLiterals.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS: {
                MetricsLiterals.PRECISION: 0.7,
                MetricsLiterals.RECALL: 0.8,
                MetricsLiterals.AVERAGE_PRECISION: 0.6
            },
            MetricsLiterals.CONFUSION_MATRICES_PER_SCORE_THRESHOLD: {
                0.15: [[3, 1, 0], [1, 2, 0]],
                0.4: [[2, 0, 1], [0, 1, 1]]
            }
        }
        if data_type == "tensors":
            voc_metrics = _convert_numbers_to_tensors(voc_metrics)

        od_utils._update_with_voc_metrics(current_metrics, cumulative_per_label_metrics, voc_metrics)

        assert current_metrics == {
            MetricsLiterals.PRECISION: 0.35,
            MetricsLiterals.RECALL: 0.65,
            MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD: {0.2: 0.5, 0.4: 0.6, 0.6: 0.7, 0.8: 0.8},
            MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD: {0.2: 0.5, 0.4: 0.4, 0.6: 0.3, 0.8: 0.2},
            MetricsLiterals.PER_LABEL_METRICS: {
                0: {
                    MetricsLiterals.PRECISION: 0.3,
                    MetricsLiterals.RECALL: 0.7,
                    MetricsLiterals.AVERAGE_PRECISION: 0.25,
                    MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD: {0.1: 0.2, 0.3: 0.4},
                    MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD: {0.1: 0.5, 0.3: 0.6},
                },
                1: {
                    MetricsLiterals.PRECISION: 0.4,
                    MetricsLiterals.RECALL: 0.6,
                    MetricsLiterals.AVERAGE_PRECISION: 0.75,
                    MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD: {0.1: 0.7, 0.3: 0.8},
                    MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD: {0.1: 0.9, 0.3: 1.0},
                }
            },
            MetricsLiterals.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS: {
                MetricsLiterals.PRECISION: 0.7,
                MetricsLiterals.RECALL: 0.8,
                MetricsLiterals.AVERAGE_PRECISION: 0.6
            },
            MetricsLiterals.CONFUSION_MATRICES_PER_SCORE_THRESHOLD: {
                0.15: [[3, 1, 0], [1, 2, 0]],
                0.4: [[2, 0, 1], [0, 1, 1]]
            }
        }

        assert cumulative_per_label_metrics == {
            0: {
                MetricsLiterals.PRECISION: [0.3],
                MetricsLiterals.RECALL: [0.7],
                MetricsLiterals.AVERAGE_PRECISION: [0.25]
            },
            1: {
                MetricsLiterals.PRECISION: [0.4],
                MetricsLiterals.RECALL: [0.6],
                MetricsLiterals.AVERAGE_PRECISION: [0.75]
            },
        }

    @pytest.mark.parametrize("data_type", ["numbers", "tensors"])
    def test_update_with_voc_metrics_complex(self, data_type):
        current_metrics = {}
        cumulative_per_label_metrics = {
            0: {
                MetricsLiterals.PRECISION: [0.3],
                MetricsLiterals.RECALL: [0.7],
                MetricsLiterals.AVERAGE_PRECISION: [0.25]
            },
            1: {
                MetricsLiterals.PRECISION: [0.4],
                MetricsLiterals.RECALL: [0.6],
                MetricsLiterals.AVERAGE_PRECISION: [0.75]
            }
        }
        if data_type == "tensors":
            cumulative_per_label_metrics = _convert_numbers_to_tensors(cumulative_per_label_metrics)

        voc_metrics = {
            MetricsLiterals.PRECISION: 0.4287317322877335,
            MetricsLiterals.RECALL: 0.3727672265,
            MetricsLiterals.MEAN_AVERAGE_PRECISION: 0.609,
            # precisions per threshold missing but no crash
            MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD: {
                0.25349234: 0.89432452, 0.49456456: 0.41, 0.694356456: 0.393245, 0.80000001: 0.22
            },
            MetricsLiterals.PER_LABEL_METRICS: {
                1: {
                    MetricsLiterals.PRECISION: 0.12321,
                    MetricsLiterals.RECALL: 0.456,
                    MetricsLiterals.AVERAGE_PRECISION: 0.55,
                    MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD: {
                        0.0001: 0.12345, 0.001: 0.1234, 0.01: 0.123, 0.1: 0.12, 1.0: 0.1
                    },
                    MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD: {
                        0.0001: 0.745893534534534423, 0.001: 0.5, 0.01: 0.63, 0.1: 0.631, 1.0: 0.631001
                    },
                },
                2: {
                    MetricsLiterals.PRECISION: 0.734253464575467,
                    MetricsLiterals.RECALL: 0.289534453,
                    MetricsLiterals.AVERAGE_PRECISION: 0.668,
                    MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD: {
                        0.1: 0.9534053, 0.2: 0.09453245, 0.5: 0.853451, 0.8: 0.84354, 0.9: 1.0
                    },
                    MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD: {
                        0.1: 0.13, 0.2: 0.1313, 0.5: 0.131313, 0.8: 0.13131313, 0.9: 0.131313131313
                    },
                }
            },
            MetricsLiterals.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS: {
                MetricsLiterals.PRECISION: 0.7539893453945,
                MetricsLiterals.RECALL: 0.8549328534,
                MetricsLiterals.AVERAGE_PRECISION: 0.6235478395734,
                # _update_with_voc_metrics() ignores precisions and recalls per score threshold at image level.
                MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD: {0.2: 0.75, 0.3: 0.25},
                MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD: {0.2: 0.25, 0.3: 0.75},
            },
            MetricsLiterals.CONFUSION_MATRICES_PER_SCORE_THRESHOLD: {
                0.85647: [[4, 0, 0, 0, 12], [0, 9, 0, 0, 7], [0, 0, 9, 0, 10], [0, 0, 0, 8, 8]],
                0.85188: [[7, 0, 0, 0, 9], [0, 9, 0, 0, 7], [0, 0, 12, 0, 7], [0, 0, 0, 8, 8]],
                0.84831: [[8, 0, 0, 0, 8], [0, 11, 0, 0, 5], [0, 0, 14, 0, 5], [0, 0, 0, 9, 7]],
                0.84128: [[10, 0, 0, 0, 6], [0, 12, 0, 0, 4], [0, 0, 15, 0, 4], [0, 0, 0, 11, 5]],
                0.83179: [[10, 0, 0, 0, 6], [0, 14, 0, 0, 2], [0, 0, 17, 0, 2], [0, 0, 0, 13, 3]]
            }
        }
        if data_type == "tensors":
            voc_metrics = _convert_numbers_to_tensors(voc_metrics)

        od_utils._update_with_voc_metrics(current_metrics, cumulative_per_label_metrics, voc_metrics)

        assert current_metrics == {
            MetricsLiterals.PRECISION: 0.42873,
            MetricsLiterals.RECALL: 0.37277,
            MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD: {
                0.25349: 0.89432, 0.49456: 0.41, 0.69436: 0.39325, 0.8: 0.22
            },
            MetricsLiterals.PER_LABEL_METRICS: {
                1: {
                    MetricsLiterals.PRECISION: 0.12321,
                    MetricsLiterals.RECALL: 0.456,
                    MetricsLiterals.AVERAGE_PRECISION: 0.55,
                    MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD: {
                        0.0001: 0.12345, 0.001: 0.1234, 0.01: 0.123, 0.1: 0.12, 1.0: 0.1
                    },
                    MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD: {
                        0.0001: 0.74589, 0.001: 0.5, 0.01: 0.63, 0.1: 0.631, 1.0: 0.631
                    }
                },
                2: {
                    MetricsLiterals.PRECISION: 0.73425,
                    MetricsLiterals.RECALL: 0.28953,
                    MetricsLiterals.AVERAGE_PRECISION: 0.668,
                    MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD: {
                        0.1: 0.95341, 0.2: 0.09453, 0.5: 0.85345, 0.8: 0.84354, 0.9: 1.0
                    },
                    MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD: {
                        0.1: 0.13, 0.2: 0.1313, 0.5: 0.13131, 0.8: 0.13131, 0.9: 0.13131
                    }
                }
            },
            MetricsLiterals.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS: {
                MetricsLiterals.PRECISION: 0.75399,
                MetricsLiterals.RECALL: 0.85493,
                MetricsLiterals.AVERAGE_PRECISION: 0.62355
            },
            MetricsLiterals.CONFUSION_MATRICES_PER_SCORE_THRESHOLD: {
                0.85647: [[4, 0, 0, 0, 12], [0, 9, 0, 0, 7], [0, 0, 9, 0, 10], [0, 0, 0, 8, 8]],
                0.85188: [[7, 0, 0, 0, 9], [0, 9, 0, 0, 7], [0, 0, 12, 0, 7], [0, 0, 0, 8, 8]],
                0.84831: [[8, 0, 0, 0, 8], [0, 11, 0, 0, 5], [0, 0, 14, 0, 5], [0, 0, 0, 9, 7]],
                0.84128: [[10, 0, 0, 0, 6], [0, 12, 0, 0, 4], [0, 0, 15, 0, 4], [0, 0, 0, 11, 5]],
                0.83179: [[10, 0, 0, 0, 6], [0, 14, 0, 0, 2], [0, 0, 17, 0, 2], [0, 0, 0, 13, 3]]
            }
        }

        assert cumulative_per_label_metrics == {
            0: {
                MetricsLiterals.PRECISION: [0.3],
                MetricsLiterals.RECALL: [0.7],
                MetricsLiterals.AVERAGE_PRECISION: [0.25]
            },
            1: {
                MetricsLiterals.PRECISION: [0.4, 0.12321],
                MetricsLiterals.RECALL: [0.6, 0.456],
                MetricsLiterals.AVERAGE_PRECISION: [0.75, 0.55]
            },
            2: {
                MetricsLiterals.PRECISION: [0.73425],
                MetricsLiterals.RECALL: [0.28953],
                MetricsLiterals.AVERAGE_PRECISION: [0.668]
            }
        }

    @mock.patch(od_utils.__name__ + '.CommonObjectDetectionDatasetWrapper')
    @mock.patch(od_utils.__name__ + '.AmlDatasetObjectDetection')
    @mock.patch(od_utils.__name__ + '.IncrementalVocEvaluator')
    @mock.patch(od_utils.__name__ + '._evaluate_predictions_incrementally')
    @mock.patch(od_utils.__name__ + '._evaluate_and_log')
    def test_validate_score_run(
        self, mock_eval, mock_eval_pred_inc, mock_incremental_voc_evaluator, mock_dataset, mock_wrapper
    ):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            # Patch functions
            ws_mock, ds_mock, wrapper_mock = self._setup_wrapper()
            incremental_voc_evaluator_obj = IncrementalVocEvaluator(True, len(wrapper_mock.dataset.classes), 0.5)

            mock_dataset.return_value = wrapper_mock.dataset
            mock_wrapper.return_value = wrapper_mock
            mock_incremental_voc_evaluator.return_value = incremental_voc_evaluator_obj
            mock_eval_pred_inc.return_value = None
            mock_eval.return_value = None

            # Setup mock objects
            predictions_file = 'predictions_od.txt'
            output_file = os.path.join(tmp_output_dir, predictions_file)
            experiment_mock = ExperimentMock(ws_mock)
            mock_run = RunMock(experiment_mock)

            od_utils._validate_score_run(task_is_detection=True,
                                         input_dataset=ds_mock,
                                         use_bg_label=True,
                                         iou_threshold=0.5,
                                         output_file=output_file,
                                         score_run=mock_run)

            # Assert that expected methods were called
            mock_dataset.assert_called_once_with(dataset=ds_mock, is_train=False,
                                                 ignore_data_errors=True,
                                                 use_bg_label=True,
                                                 masks_required=False)
            mock_wrapper.assert_called_once_with(dataset=wrapper_mock.dataset,
                                                 dataset_processing_type=DatasetProcessingType.IMAGES)

            mock_incremental_voc_evaluator.assert_called_once_with(True, len(wrapper_mock.dataset.classes), 0.5)
            mock_eval_pred_inc.assert_called_once_with(
                output_file, wrapper_mock.dataset, incremental_voc_evaluator_obj
            )
            mock_eval.assert_called_once_with(mock_run, incremental_voc_evaluator_obj)

    @mock.patch(od_utils.__name__ + '.IncrementalVocEvaluator.evaluate_batch')
    def test_evaluate_predictions_incrementally(self, mock_evaluate_batch):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            # Set up predictions file.
            predictions_file_name = os.path.join(tmp_output_dir, "predictions_od.txt")
            self._write_output_file(predictions_file_name)

            # Set up dataset wrapper.
            _, _, wrapper_mock = self._setup_wrapper()

            # Set up incremental evaluator.
            incremental_voc_evaluator_obj = IncrementalVocEvaluator(True, len(wrapper_mock.dataset.classes), 0.5)

            # Call _evaluate_predictions_incrementally().
            od_utils._evaluate_predictions_incrementally(
                predictions_file_name=predictions_file_name, dataset=wrapper_mock.dataset,
                incremental_evaluator=incremental_voc_evaluator_obj
            )

            # Check that two calls to evaluate_batch() were made. (one call for a batch with the first image only and
            # one call for a batch with the second image only)
            assert len(mock_evaluate_batch.call_args_list) == 2

            # Get the evaluate_batch() arguments for the first and second image.
            first_call_args = mock_evaluate_batch.call_args_list[0][0]
            second_call_args = mock_evaluate_batch.call_args_list[1][0]

            # Check the ground truth objects for the first image.
            gt_objects = first_call_args[0][0]
            np.testing.assert_array_almost_equal(
                gt_objects["boxes"], [[76.8, 921.6, 153.6, 1024.0], [384.0, 512.0, 460.8, 614.4]], decimal=4
            )
            assert gt_objects["masks"] is None
            np.testing.assert_array_equal(gt_objects["classes"], [1, 2])

            # Check the predicted objects for the first image.
            predicted_objects = first_call_args[1][0]
            np.testing.assert_array_almost_equal(predicted_objects["boxes"], [[76.8, 921.6, 153.6, 819.2]], decimal=4)
            assert predicted_objects["masks"] is None
            np.testing.assert_array_equal(predicted_objects["classes"], [1])
            np.testing.assert_array_equal(predicted_objects["scores"], [0.7])

            # Check the image info for the first image.
            image_info = first_call_args[2][0]
            np.testing.assert_array_equal(image_info["iscrowd"], [0, 0])

            # Check the ground truth objects for the second image.
            gt_objects = second_call_args[0][0]
            np.testing.assert_array_almost_equal(gt_objects["boxes"], [[423.0, 544.0, 540.0, 677.0]], decimal=4)
            assert gt_objects["masks"] is None
            np.testing.assert_array_equal(gt_objects["classes"], [3])

            # Check the predicted objects for the second image.
            predicted_objects = second_call_args[1][0]
            np.testing.assert_array_almost_equal(predicted_objects["boxes"], [[384.0, 512.0, 460.8, 409.6]], decimal=4)
            assert predicted_objects["masks"] is None
            np.testing.assert_array_equal(predicted_objects["classes"], [2])
            np.testing.assert_array_equal(predicted_objects["scores"], [0.8])

            # Check the image info for the second image.
            image_info = second_call_args[2][0]
            np.testing.assert_array_equal(image_info["iscrowd"], [0])

    @mock.patch(od_utils.__name__ + '.IncrementalVocEvaluator.compute_metrics')
    def test_evaluate_and_log(self, mock_incremental_voc_evaluator_compute):
        # Set up mock objects
        metrics = {
            MetricsLiterals.PRECISION: 0.7,
            MetricsLiterals.RECALL: 0.8,
            MetricsLiterals.MEAN_AVERAGE_PRECISION: 0.9,
            MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD: {0.1: 0.5, 0.9: 0.5},
            MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD: {0.1: 0.9, 0.9: 0.1},
            MetricsLiterals.PER_LABEL_METRICS: {
                1: {
                    'precision': 0.1, 'recall': 0.2, 'average_precision': 0.3,
                    'precisions_per_score_threshold': {0.2: 0.6, 1.0: 0.6},
                    'recalls_per_score_threshold': {0.2: 1.0, 1.0: 0.2},
                },
                2: {
                    'precision': 0.2, 'recall': 0.3, 'average_precision': 0.4,
                    'precisions_per_score_threshold': {0.1: 0.5, 0.9: 0.5},
                    'recalls_per_score_threshold': {0.1: 0.9, 0.9: 0.1},
                },
                3: {
                    'precision': 0.3, 'recall': 0.4, 'average_precision': 0.5,
                    'precisions_per_score_threshold': {0.01: 0.5, 0.09: 0.5},
                    'recalls_per_score_threshold': {0.01: 0.9, 0.09: 0.1},
                },
            },
            MetricsLiterals.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS: {
                MetricsLiterals.PRECISION: 0.2,
                MetricsLiterals.RECALL: 0.4,
                MetricsLiterals.AVERAGE_PRECISION: 0.6
            },
            MetricsLiterals.CONFUSION_MATRICES_PER_SCORE_THRESHOLD: {
                0.1: [[19, 0, 0, 0, 1], [0, 8, 0, 0, 7], [0, 0, 10, 0, 0], [0, 0, 0, 3, 2]],
                0.2: [[15, 0, 0, 0, 5], [0, 8, 0, 0, 7], [0, 0, 8, 0, 2], [0, 0, 0, 3, 2]],
                0.3: [[12, 0, 0, 0, 8], [0, 6, 0, 0, 9], [0, 0, 4, 0, 6], [0, 0, 0, 3, 2]],
                0.4: [[10, 0, 0, 0, 10], [0, 2, 0, 0, 13], [0, 0, 1, 0, 9], [0, 0, 0, 0, 5]]
            }
        }
        mock_incremental_voc_evaluator_compute.return_value = metrics

        ws_mock, _, wrapper_mock = self._setup_wrapper()
        experiment_mock = ExperimentMock(ws_mock)
        mock_run = RunMock(experiment_mock)
        incremental_voc_evaluator_obj = IncrementalVocEvaluator(True, len(wrapper_mock.dataset.classes), 0.5)

        od_utils._evaluate_and_log(score_run=mock_run, incremental_voc_evaluator=incremental_voc_evaluator_obj)

        # Validate that the right compute method was called
        mock_incremental_voc_evaluator_compute.assert_called_once_with()

        # Validate properties contain only basic metric values
        properties = mock_run.properties
        assert properties[MetricsLiterals.PRECISION] == 0.7
        assert properties[MetricsLiterals.RECALL] == 0.8
        assert properties[MetricsLiterals.MEAN_AVERAGE_PRECISION] == 0.9
        assert MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD not in properties
        assert MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD not in properties
        assert MetricsLiterals.PER_LABEL_METRICS not in properties
        assert MetricsLiterals.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS not in properties
        assert MetricsLiterals.CONFUSION_MATRICES_PER_SCORE_THRESHOLD not in properties

        # Validate metrics contain only basic metric values
        metrics = mock_run.metrics
        assert metrics[MetricsLiterals.PRECISION] == 0.7
        assert metrics[MetricsLiterals.RECALL] == 0.8
        assert metrics[MetricsLiterals.MEAN_AVERAGE_PRECISION] == 0.9
        assert MetricsLiterals.PRECISIONS_PER_SCORE_THRESHOLD not in metrics
        assert MetricsLiterals.RECALLS_PER_SCORE_THRESHOLD not in metrics
        assert MetricsLiterals.PER_LABEL_METRICS not in metrics
        assert MetricsLiterals.IMAGE_LEVEL_BINARY_CLASSIFIER_METRICS not in metrics
        assert MetricsLiterals.CONFUSION_MATRICES_PER_SCORE_THRESHOLD not in metrics


@pytest.mark.usefixtures('new_clean_dir')
def test_score_validation_data(monkeypatch):
    def mock_fetch_model(run_id, device, model_settings):
        assert run_id == 'mock_run_id'
        expected_model_settings = {"dummySetting": "dummyVal"}
        assert model_settings == expected_model_settings
        return 'mock_model'

    def mock_score(model_wrapper, run, target_path, device,
                   output_file, root_dir, image_list_file,
                   batch_size, ignore_data_errors, input_dataset,
                   num_workers, validate_score, log_output_file_info, download_image_files):
        assert model_wrapper == 'mock_model'
        assert target_path.startswith('automl/datasets/')
        assert batch_size == 20
        assert input_dataset.id == '123'
        assert num_workers == 8
        assert device == 'cpu'
        assert log_output_file_info

        data_folder = os.path.join(tmp_output_dir, 'dummyFolder')
        expected_root_dir = os.path.join(data_folder, '.')
        assert root_dir == expected_root_dir

        with open(image_list_file, 'w') as f:
            f.write('testcontent')

    with tempfile.TemporaryDirectory() as tmp_output_dir:
        ds_mock = DatastoreMock('datastore_mock')
        dataset_mock = DatasetMock('123')
        ws_mock = WorkspaceMock(ds_mock)
        experiment_mock = ExperimentMock(ws_mock)
        run_mock = RunMock(experiment_mock)
        model_settings = {"dummySetting": "dummyVal"}
        settings = {
            'validation_dataset_id': '123',
            'validation_batch_size': 20,
            'validation_labels_file': 'test.csv',
            'labels_file_root': tmp_output_dir,
            'data_folder': os.path.join(tmp_output_dir, 'dummyFolder'),
            'num_workers': 8,
            'validate_scoring': False,
            'images_folder': '.',
            'log_scoring_file_info': True
        }

        with monkeypatch.context() as m:
            m.setattr(od_utils, '_fetch_model_from_artifacts', mock_fetch_model)
            od_utils.score_validation_data(run=run_mock, model_settings=model_settings,
                                           settings=settings, device='cpu',
                                           score_with_model=mock_score, val_dataset=dataset_mock)
            expected_val_labels_file = os.path.join(tmp_output_dir, 'test.csv')
            assert os.path.exists(expected_val_labels_file)
