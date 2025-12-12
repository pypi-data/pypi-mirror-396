from azureml.automl.dnn.vision.object_detection_yolo.models.yolo_wrapper import YoloV5Wrapper
from azureml.automl.dnn.vision.object_detection.common.constants import ModelNames
from azureml.automl.dnn.vision.object_detection_yolo.common.constants import ModelSize
from ..common.utils import delete_model_weights


class TestYoloWrapper:
    def test_yolo_wrapper_create(self):
        settings = {'device': 'cpu'}

        for model_size in ModelSize.ALL_TYPES:
            settings.update({
                "model_size": model_size
            })

            model_wrapper = YoloV5Wrapper(
                model_name=ModelNames.YOLO_V5, number_of_classes=4, specs=settings)
            assert model_wrapper is not None

        delete_model_weights()
