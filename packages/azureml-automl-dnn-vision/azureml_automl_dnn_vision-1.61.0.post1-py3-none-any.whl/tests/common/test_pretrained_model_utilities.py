# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Test for pretrained model utilities for the package."""
from collections import OrderedDict
from unittest.mock import patch, call
from urllib.error import URLError

import pytest

from azureml.automl.dnn.vision.common.constants import PretrainedSettings
from azureml.automl.dnn.vision.common.pretrained_model_utilities import PretrainedModelFactory

from azureml.automl.core.shared._diagnostics.error_strings import AutoMLErrorStrings
from azureml.exceptions import UserErrorException


class TestPretrainedModelFactory:
    """The Factory class of creating the pretrained models that are used by the package."""

    @patch("azureml.automl.dnn.vision.common.pretrained_model_utilities.load_state_dict_from_url")
    def test_load_state_dict_from_url_with_retry_with_no_exception(self, mock_load_state_dict_from_url):
        mock_load_state_dict_from_url.return_value = OrderedDict()
        return_value = PretrainedModelFactory._load_state_dict_from_url_with_retry(url="https://aka.ms"
                                                                                       "/dummy_model.pth")
        assert type(return_value) == OrderedDict
        mock_load_state_dict_from_url.assert_called_once()

    @patch("random.uniform", return_value=0.5)
    @patch("time.sleep", return_value=None)
    @patch("azureml.automl.dnn.vision.common.pretrained_model_utilities.load_state_dict_from_url")
    @patch("logging.Logger.warning")
    def test_load_state_dict_from_url_with_retry_with_exceptions(
        self, mock_logger_warning, mock_load_state_dict_from_url, mock_sleep, mock_random
    ):
        mock_return_values = [ConnectionResetError(), ConnectionResetError(), ConnectionResetError(),
                              ConnectionResetError(), ConnectionResetError()]
        mock_load_state_dict_from_url.side_effect = mock_return_values

        with pytest.raises(ConnectionResetError):
            PretrainedModelFactory._load_state_dict_from_url_with_retry(url="https://aka.ms/dummy_model.pth")
        assert mock_load_state_dict_from_url.call_count == PretrainedSettings.DOWNLOAD_RETRY_COUNT

        for i in range(len(mock_return_values) - 1):
            # please note that, sleep function called one less time than load_state_dict_from_url function
            wait_time = (2 ** i) * PretrainedSettings.BACKOFF_IN_SECONDS + mock_random.return_value
            assert mock_sleep.call_args_list[i] == call(wait_time)

        mock_logger_warning.assert_any_call("Failed to load pretrained model 4 times.")

    @patch("random.uniform", return_value=0.5)
    @patch("time.sleep", return_value=None)
    @patch("azureml.automl.dnn.vision.common.pretrained_model_utilities.load_state_dict_from_url")
    @patch("logging.Logger.warning")
    def test_load_state_dict_from_url_with_retry_partial_exceptions(
        self, mock_logger_warning, mock_load_state_dict_from_url, mock_sleep, mock_random
    ):
        """Scenario where first 3 download attempt results in ConnectionResetError and eventually download succeeded"""

        mock_return_values = [ConnectionResetError(), ConnectionResetError(), ConnectionResetError(), OrderedDict()]
        mock_load_state_dict_from_url.side_effect = mock_return_values
        return_value = PretrainedModelFactory._load_state_dict_from_url_with_retry(
            url="https://aka.ms/dummy_model.pth")
        assert type(return_value) == OrderedDict
        assert mock_load_state_dict_from_url.call_count == len(mock_return_values)
        for i in range(len(mock_return_values) - 1):
            # please note that, sleep function called one less time than load_state_dict_from_url function
            wait_time = (2 ** i) * PretrainedSettings.BACKOFF_IN_SECONDS + mock_random.return_value
            assert mock_sleep.call_args_list[i] == call(wait_time)

        assert call("Failed to load pretrained model 4 times.") not in mock_logger_warning.mock_calls

    @patch("azureml.automl.dnn.vision.common.pretrained_model_utilities.load_state_dict_from_url")
    @patch("logging.Logger.warning")
    def test_load_state_dict_from_url_with_retry_runtime_exceptions(
        self, mock_logger_warning, mock_load_state_dict_from_url
    ):
        mock_return_values = [
            RuntimeError("CUDA error: out of memory"), RuntimeError("CUDA error: out of memory"),
            RuntimeError("CUDA error: out of memory"), RuntimeError("CUDA error: out of memory"),
            RuntimeError("CUDA error: uncorrectable ECC error encountered")
        ]
        mock_load_state_dict_from_url.side_effect = mock_return_values

        with pytest.raises(RuntimeError):
            PretrainedModelFactory._load_state_dict_from_url_with_retry(url="https://aka.ms/dummy_model.pth")
        assert mock_load_state_dict_from_url.call_count == PretrainedSettings.DOWNLOAD_RETRY_COUNT

        mock_logger_warning.assert_any_call(
            "Failed to load pretrained model 4 times. Suspected cause: faulty hardware."
        )

    @patch("azureml.automl.runtime.network_compute_utils.get_cluster_name", return_value="test_cluster_name")
    @patch("azureml.automl.runtime.network_compute_utils.get_vnet_name", return_value="test_vnet_name")
    @patch("azureml.automl.dnn.vision.common.pretrained_model_utilities.load_state_dict_from_url")
    @patch("logging.Logger.warning")
    def test_load_state_dict_from_url_with_retry_urlerror_exceptions(
        self, mock_logger_warning, mock_load_state_dict_from_url, mock_get_vnet_name, mock_get_cluster_name
    ):
        cluster_name, vnet_name = "test_cluster_name", "test_vnet_name"
        mock_return_values = [
            URLError("[Errno 0] Error"), URLError("[Errno 0] Error"),
            URLError("[Errno 0] Error"), URLError("[Errno 0] Error"),
            URLError("[Errno 0] Error")
        ]
        mock_load_state_dict_from_url.side_effect = mock_return_values

        with pytest.raises(UserErrorException) as exc_info:
            PretrainedModelFactory._load_state_dict_from_url_with_retry(url="https://aka.ms/dummy_model.pth")
        assert mock_load_state_dict_from_url.call_count == PretrainedSettings.DOWNLOAD_RETRY_COUNT - 1
        assert AutoMLErrorStrings.NETWORK_VNET_MISCONFIG.format(vnet=vnet_name, cluster_name=cluster_name) \
               in str(exc_info.value)

        mock_logger_warning.assert_any_call("Failed to load pretrained model 4 times. Suspected cause: network error.")
