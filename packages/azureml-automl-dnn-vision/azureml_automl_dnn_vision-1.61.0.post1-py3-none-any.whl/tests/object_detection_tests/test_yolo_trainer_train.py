from typing import List, Tuple
from unittest.mock import Mock

import pytest
from torch import rand, tensor

from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionRuntimeUserException
from azureml.automl.dnn.vision.common.trainer.lrschedule import LRSchedulerUpdateType
from azureml.automl.dnn.vision.object_detection_yolo.common.constants import YoloLiterals
from azureml.automl.dnn.vision.object_detection_yolo.trainer.train import train_one_epoch


class TestYoloTrainerTrain:

    @staticmethod
    def get_dummy_dataloader(number_of_images: int) -> List[Tuple[tensor, tensor, tensor]]:
        images = rand((number_of_images, 3, 3, 3))
        target = rand(number_of_images)
        return list(zip(images, target, target))

    @pytest.fixture(scope="class")
    def _mock_yolo_model(self):
        model = Mock()
        model.train.return_value = None
        model.hyp = {YoloLiterals.MULTI_SCALE: False}
        return model

    @pytest.fixture(scope="class")
    def _mock_model_ema(self) -> Mock:
        ema = Mock()
        ema.update.return_value = None
        return ema

    @pytest.fixture(scope="class")
    def _mock_optimizer(self) -> Mock:
        optimizer = Mock()
        optimizer.zero_grad.return_value = None
        optimizer.step.return_value = None
        return optimizer

    @pytest.fixture(scope="class")
    def _mock_learning_rate_scheduler(self) -> Mock:
        lr_scheduler = Mock()
        lr_scheduler.update_type = LRSchedulerUpdateType.BATCH
        lr_scheduler.lr_scheduler.step.return_value = None
        return lr_scheduler

    @pytest.fixture(scope="class")
    def _mock_system_meter(self) -> Mock:
        system_meter = Mock()
        system_meter.log_system_stats.return_value = None
        return system_meter

    @pytest.fixture(scope="class")
    def _mock_yolo_evaluator(self) -> Mock:
        yolo_evaluator = Mock()
        return yolo_evaluator

    def test_train_one_epoch_for_cuda_out_of_memory(self, _mock_yolo_model, _mock_model_ema, _mock_optimizer,
                                                    _mock_learning_rate_scheduler, _mock_system_meter,
                                                    _mock_yolo_evaluator) -> None:
        train_loader = TestYoloTrainerTrain.get_dummy_dataloader(number_of_images=3)
        _mock_yolo_model.side_effect = RuntimeError("RuntimeError('CUDA out of memory. Tried to allocate 170.00 MiB "
                                                    "(GPU 0 15.75 GiB total capacity; 14.54 GiB already allocated; "
                                                    "87.62 MiB free; 14.70 GiB reserved in total by PyTorch)')")
        with pytest.raises(AutoMLVisionRuntimeUserException) as ex_context:
            train_one_epoch(_mock_yolo_model, _mock_model_ema, _mock_optimizer, _mock_learning_rate_scheduler,
                            train_loader=train_loader, epoch=1, device='cpu', system_meter=_mock_system_meter,
                            grad_accum_steps=1, grad_clip_type='norm', evaluator=_mock_yolo_evaluator)
        assert ex_context.value.error_code == 'Memory'
        assert ex_context.value.error_type == 'UserError'

    def test_train_one_epoch_for_generic_runtime_exception(self, _mock_yolo_model, _mock_model_ema, _mock_optimizer,
                                                           _mock_learning_rate_scheduler, _mock_system_meter,
                                                           _mock_yolo_evaluator) -> None:
        train_loader = TestYoloTrainerTrain.get_dummy_dataloader(number_of_images=3)
        _mock_yolo_model.side_effect = RuntimeError("This is runtime exception other than memory exhausted.")
        with pytest.raises(RuntimeError):
            train_one_epoch(_mock_yolo_model, _mock_model_ema, _mock_optimizer, _mock_learning_rate_scheduler,
                            train_loader=train_loader, epoch=1, device='cpu', system_meter=_mock_system_meter,
                            grad_accum_steps=1, grad_clip_type='norm', evaluator=_mock_yolo_evaluator)
