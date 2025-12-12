# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Class to store/load the state of object detection training for restarts."""


from typing import Dict, Any

from azureml.automl.dnn.vision.common.training_state import TrainingState


class ODTrainingState(TrainingState):
    """Class to store/load object detection training state.
    This class stores the following details needed to restart the training.
        - Aggregated metrics stored across epochs (per_label_metrics, computed_metrics)
    """

    def __init__(self) -> None:
        """Init method."""
        super().__init__()
        # Aggregate metrics
        self.per_label_metrics: Dict[str, Any] = {}
        self.computed_metrics: Dict[str, Any] = {}

    def state_dict(self) -> Dict[str, Any]:
        """Get state dictionary.

        :return: State dictionary
        :rtype: dict
        """
        save_dict = super().state_dict()
        save_dict.update({
            "per_label_metrics": self.per_label_metrics,
            "computed_metrics": self.computed_metrics
        })
        return save_dict

    def load_state_dict(self, state_dict: Dict[str, Any]) -> None:
        """Load from state dictionary.

        :param state_dict: State dictionary.
        :type state_dict: dict
        """
        self.per_label_metrics = state_dict["per_label_metrics"]
        self.computed_metrics = state_dict["computed_metrics"]
        super().load_state_dict(state_dict)
