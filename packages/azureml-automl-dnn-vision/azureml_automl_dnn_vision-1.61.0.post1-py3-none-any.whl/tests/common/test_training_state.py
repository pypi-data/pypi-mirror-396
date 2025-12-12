# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for training state machine."""


from azureml.automl.dnn.vision.common.training_state import TrainingState
from azureml.automl.dnn.vision.object_detection.common.od_training_state import ODTrainingState
from azureml.automl.dnn.vision.object_detection_yolo.common.od_yolo_training_state import ODYoloTrainingState


class TestTrainingState:

    def test_init(self):
        training_state = TrainingState()
        assert training_state.best_model_wts is None
        assert training_state.best_score == 0.0
        assert training_state.best_epoch == 0
        assert training_state.best_model_metrics is None
        assert training_state.no_progress_counter == 0
        assert not training_state.stop_early
        assert training_state.epoch == -1

    def test_save_load_functions(self):
        state_dict = {
            "no_progress_counter": 3,
            "stop_early": True
        }
        training_state = TrainingState()
        training_state.load_state_dict(state_dict)
        training_state_dict = training_state.state_dict()
        assert state_dict == training_state_dict

    def test_get_start_epoch(self):
        training_state = TrainingState()
        number_of_epochs = 15

        # Training not yet started/no checkpoint found to load training state
        start_epoch = training_state.get_start_epoch(number_of_epochs)
        assert start_epoch == 0

        # Training state loaded from checkpoint for epoch 3.
        training_state.epoch = 3
        start_epoch = training_state.get_start_epoch(number_of_epochs)
        assert start_epoch == 4

        # Training state loaded from checkpoint for epoch 3 and stop_early is set to True.
        training_state.stop_early = True
        start_epoch = training_state.get_start_epoch(number_of_epochs)
        assert start_epoch == number_of_epochs


class TestODTrainingState:

    def test_init(self):
        training_state = ODTrainingState()
        assert training_state.best_model_wts is None
        assert training_state.best_score == 0.0
        assert training_state.best_epoch == 0
        assert training_state.best_model_metrics is None
        assert training_state.no_progress_counter == 0
        assert not training_state.stop_early
        assert training_state.epoch == -1
        assert training_state.per_label_metrics == {}
        assert training_state.computed_metrics == {}

    def test_save_load_functions(self):
        state_dict = {
            "no_progress_counter": 3,
            "stop_early": True,
            "per_label_metrics": {
                0: {
                    "precision": [
                        0.25,
                        0.50,
                        0.75,
                        1.0
                    ],
                    "recall": [
                        0.25,
                        0.50,
                        0.75,
                        1.0
                    ],
                    "average_precision": [
                        0.25,
                        0.50,
                        0.75,
                        1.0
                    ]
                }
            },
            "computed_metrics": {
                "precision": 0.25,
                "recall": 0.50,
                "mean_average_precision": 1.0
            }
        }
        training_state = ODTrainingState()
        training_state.load_state_dict(state_dict)
        training_state_dict = training_state.state_dict()
        assert state_dict == training_state_dict


class TestODYoloTrainingState:

    def test_init(self):
        training_state = ODYoloTrainingState()
        assert training_state.best_model_wts is None
        assert training_state.best_score == 0.0
        assert training_state.best_epoch == 0
        assert training_state.best_model_metrics is None
        assert training_state.no_progress_counter == 0
        assert not training_state.stop_early
        assert training_state.epoch == -1
        assert training_state.per_label_metrics == {}
        assert training_state.computed_metrics == {}
        assert training_state.ema_updates == 0

    def test_save_load_functions(self):
        state_dict = {
            "no_progress_counter": 3,
            "stop_early": True,
            "per_label_metrics": {
                0: {
                    "precision": [
                        0.25,
                        0.50,
                        0.75,
                        1.0
                    ],
                    "recall": [
                        0.25,
                        0.50,
                        0.75,
                        1.0
                    ],
                    "average_precision": [
                        0.25,
                        0.50,
                        0.75,
                        1.0
                    ]
                }
            },
            "computed_metrics": {
                "precision": 0.25,
                "recall": 0.50,
                "mean_average_precision": 1.0
            },
            "ema_updates": 5
        }
        training_state = ODYoloTrainingState()
        training_state.load_state_dict(state_dict)
        training_state_dict = training_state.state_dict()
        assert state_dict == training_state_dict
