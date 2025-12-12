# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Class to store/load the state of training for restarts."""


from typing import Any, Dict, Optional


class TrainingState:
    """Class to store/load training state. The training state is stored as part of the checkpoint at
    checkpoint_frequency intervals. In cases where we can restart the training while handling certain exceptions, this
    state is loaded from the checkpoint and is used to restart training.
    This class stores anything that is needed to restart the training. Currently, it stores
        - Epochs completed
        - Best model details
        - Early stopping details
    """

    def __init__(self) -> None:
        """Init method."""
        # Best model details
        self.best_model_wts: Optional[Dict[str, Any]] = None
        self.best_score: float = 0.0
        self.best_epoch: int = 0
        self.best_model_metrics: Optional[Any] = None

        # Early stopping details
        self.no_progress_counter: int = 0
        self.stop_early: bool = False

        # Epoch
        self.epoch: int = -1

    def get_start_epoch(self, number_of_epochs: int) -> int:
        """Get the start epoch when training for the first time/in case of restarts.

        :param number_of_epochs: Total number of epochs.
        :type number_of_epochs: int
        :return: Start epoch.
        :rtype: int
        """
        if self.epoch == -1:
            return 0

        if self.stop_early:
            # Training stopping early. Return number_of_epochs to skip training loop.
            return number_of_epochs

        # Start from next epoch
        return self.epoch + 1

    def state_dict(self) -> Dict[str, Any]:
        """Get state dictionary.

        :return: State dictionary
        :rtype: dict
        """
        # Best model details are not stored as part of training_state.
        # In case of a restart, they are loaded from model.pt file in output directory.
        # See artifact_utils.load_state_from_latest_checkpoint
        # Epoch is already saved as part of checkpoint
        state_dict = {
            "no_progress_counter": self.no_progress_counter,
            "stop_early": self.stop_early,
        }
        return state_dict

    def load_state_dict(self, state_dict: Dict[str, Any]) -> None:
        """Load from state dictionary.

        :param state_dict: State dictionary.
        :type state_dict: dict
        """
        # Best model details are not stored as part of training_state.
        # In case of a restart, they are loaded from model.py file in output directory.
        # See artifact_utils.load_state_from_latest_checkpoint
        self.no_progress_counter = state_dict["no_progress_counter"]
        self.stop_early = state_dict["stop_early"]
