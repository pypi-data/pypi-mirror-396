# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Class to store/load the state of yolo object detection training for restarts."""


from typing import Dict, Any

from azureml.automl.dnn.vision.object_detection.common.od_training_state import ODTrainingState


class ODYoloTrainingState(ODTrainingState):
    """Class to store/load yolo object detection training state.
    This class stores the following details needed to restart the training.
        - Number of EMA updates completed.
    """

    def __init__(self) -> None:
        """Init method."""
        super().__init__()
        self.ema_updates: int = 0

    def state_dict(self) -> Dict[str, Any]:
        """Get state dictionary.

        :return: State dictionary
        :rtype: dict
        """
        save_dict = super().state_dict()
        save_dict.update({
            "ema_updates": self.ema_updates
        })
        return save_dict

    def load_state_dict(self, state_dict: Dict[str, Any]) -> None:
        """Load from state dictionary.

        :param state_dict: State dictionary.
        :type state_dict: dict
        """
        self.ema_updates = state_dict["ema_updates"]
        super().load_state_dict(state_dict)
