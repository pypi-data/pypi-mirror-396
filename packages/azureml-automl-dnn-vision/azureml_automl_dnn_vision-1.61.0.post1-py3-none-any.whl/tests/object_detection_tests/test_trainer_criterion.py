from unittest.mock import Mock

import pytest
from torch import rand, tensor, float

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionRuntimeUserException
from azureml.automl.dnn.vision.object_detection.trainer.criterion import LossFromModelCriterion


class TestLossFromModelCriterion:
    @pytest.fixture()
    def _mock_model(self) -> Mock:
        model = Mock()
        model.return_value = tensor(0.1, dtype=float)
        return model

    def test_evaluate_assert_exception(self, _mock_model) -> None:
        _mock_model.side_effect = AssertionError()
        criterion: LossFromModelCriterion = LossFromModelCriterion()
        images = rand((2, 3, 3, 3))
        target = rand(2)
        with pytest.raises(AutoMLVisionRuntimeUserException) as ex_context:
            criterion.evaluate(_mock_model, images, target)
        assert ex_context.value.error_type == 'UserError'

    def test_evaluate_without_exception(self, _mock_model) -> None:
        criterion: LossFromModelCriterion = LossFromModelCriterion()
        images = rand((2, 3, 3, 3))
        target = rand(2)
        loss = criterion.evaluate(_mock_model, images, target)
        assert loss == _mock_model.return_value
        assert _mock_model.called
