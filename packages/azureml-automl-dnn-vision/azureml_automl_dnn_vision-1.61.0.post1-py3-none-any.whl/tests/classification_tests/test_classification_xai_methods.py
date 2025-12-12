import json
import os
import tempfile
from io import BytesIO

import azureml.automl.core.shared.constants as shared_constants
import numpy as np
import pytest
from azureml.automl.dnn.vision.classification.common.constants import \
    ModelNames
from azureml.automl.dnn.vision.classification.models import ModelFactory
from azureml.automl.dnn.vision.common.model_export_utils import (
    _get_scoring_method, run_inference, run_inference_batch,
    run_inference_helper)
from azureml.automl.dnn.vision.explainability.constants import (
    ExplainabilityDefaults, ExplainabilityLiterals)
from azureml.automl.dnn.vision.explainability.utils import (base64_to_img,
                                                            img_to_base64)
from azureml.automl.dnn.vision.classification.common.constants import ModelLiterals
from PIL import Image

from ..common.utils import delete_model_weights


@pytest.mark.usefixtures("new_clean_dir")
class TestXaiInference:

    @staticmethod
    def multilabel_checks(model_wrapper, result):
        probs = np.array(result["probs"])
        top_classes_len = len(probs[probs > ExplainabilityDefaults.CONFIDENCE_SCORE_THRESHOLD_MULTILABEL])
        if top_classes_len == 0:
            assert result["visualizations"] is None
            assert result["attributions"] is None
        else:
            assert len(result["visualizations"]) == top_classes_len
            assert len(result["attributions"]) == top_classes_len
            assert (
                np.array(result["attributions"]).shape[-1]
                == np.array(result["attributions"]).shape[-2]
                == model_wrapper.valid_crop_size
            )
            # check len of all pred classes
            assert np.array(result["attributions"]).shape[0] == top_classes_len
            try:
                for vis_i in range(top_classes_len):
                    img = base64_to_img(result["visualizations"][vis_i])
                    Image.open(BytesIO(img))
            except Exception as e:
                assert False, str(e)

    @staticmethod
    def multiclass_checks(model_wrapper, result,
                          output_visualizations=True,
                          output_attributions=True):
        # test visualizations
        if output_visualizations:
            assert result["visualizations"] is not None
            try:
                img = base64_to_img(result["visualizations"])
                Image.open(BytesIO(img))
            except Exception as e:
                assert False, str(e)
        else:
            assert result["visualizations"] is None
        # test attributions
        if output_attributions:
            assert result["attributions"] is not None
            assert (
                np.array(result["attributions"]).shape[-1]
                == np.array(result["attributions"]).shape[-2]
                == model_wrapper.valid_crop_size
            )
        else:
            assert result["attributions"] is None

    # excluding following models to save testing time as their behavior is similar to the selected ones
    # ModelNames.RESNET18, ModelNames.RESNET34,
    # ModelNames.RESNEST101,
    # ModelNames.RESNET101, ModelNames.RESNET152,
    # ModelNames.VITB16R224, ModelNames.VITL16R224
    @pytest.mark.parametrize("model_name", [ModelNames.MOBILENETV2,
                                            ModelNames.RESNET50,
                                            ModelNames.RESNEST50,
                                            ModelNames.SERESNEXT,
                                            ModelNames.VITS16R224])
    @pytest.mark.parametrize("xai_method_name", [ExplainabilityLiterals.INTEGRATEDGRADIENTS_METHOD_NAME,
                                                 ExplainabilityLiterals.GUIDEDBACKPROP_METHOD_NAME,
                                                 ExplainabilityLiterals.GUIDEDGRADCAM_METHOD_NAME,
                                                 ExplainabilityLiterals.XRAI_METHOD_NAME])
    @pytest.mark.parametrize("multilabel", [False, True])
    def test_xai_batch_inference_cpu(self, image_dir, model_name, xai_method_name, multilabel):        
        if not ("vit" in model_name and xai_method_name == ExplainabilityLiterals.GUIDEDGRADCAM_METHOD_NAME):
            if multilabel:
                task_type = shared_constants.Tasks.IMAGE_CLASSIFICATION_MULTILABEL
            else:
                task_type = shared_constants.Tasks.IMAGE_CLASSIFICATION
            number_of_classes = 10
            model_wrapper = ModelFactory().get_model_wrapper(model_name,
                                                             number_of_classes,
                                                             multilabel=multilabel,
                                                             device="cpu",
                                                             distributed=False,
                                                             local_rank=0)
            
            model_wrapper.labels = ["class_" + str(i + 1) for i in range(number_of_classes)]
            score_with_model = _get_scoring_method(task_type=task_type)

            image_path = os.path.join(image_dir, "crack_1.jpg")
            input_bytes = open(image_path, "rb").read()
            response = run_inference(model_wrapper,
                                     request_body=input_bytes,
                                     score_with_model=score_with_model,
                                     model_explainability=True,
                                     **{"xai_algorithm": xai_method_name, "attributions": True})
            result = json.loads(response)
            # keys in result: "filename", "probs", "labels", "visualizations", "attributions"
            if multilabel:
                self.multilabel_checks(model_wrapper, result)

            else:
                self.multiclass_checks(model_wrapper, result)

            delete_model_weights()

    # Test for run_inference method as well as attributions, visualizations
    # adding separate method in the class to reduce no of combinations
    @pytest.mark.parametrize("model_name", [ModelNames.SERESNEXT])
    @pytest.mark.parametrize("xai_method_name", [ExplainabilityLiterals.GUIDEDBACKPROP_METHOD_NAME])
    @pytest.mark.parametrize("output_attributions", [False, True])
    @pytest.mark.parametrize("output_visualizations", [False, True])
    def test_xai_inference_cpu(self, image_dir, model_name,
                               xai_method_name,
                               output_attributions,
                               output_visualizations):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            task_type = shared_constants.Tasks.IMAGE_CLASSIFICATION
            number_of_classes = 10
            model_wrapper = ModelFactory().get_model_wrapper(model_name,
                                                             number_of_classes,
                                                             multilabel=False,
                                                             device="cpu",
                                                             distributed=False,
                                                             local_rank=0)

            model_wrapper.labels = ["class_" + str(i + 1) for i in range(number_of_classes)]
            score_with_model = _get_scoring_method(task_type=task_type)

            sample_image = open(os.path.join(image_dir, "crack_1.jpg"), "rb").read()
            response = run_inference(model_wrapper,
                                     request_body=sample_image,
                                     score_with_model=score_with_model,
                                     model_explainability=True,
                                     **{"xai_algorithm": xai_method_name,
                                        "attributions": output_attributions,
                                        "visualizations": output_visualizations})

            result = json.loads(response)
            # keys in result: "filename", "probs", "labels", "visualizations", "attributions"
            self.multiclass_checks(model_wrapper, result, output_visualizations, output_attributions)
            delete_model_weights()

    # Test for run_inference_helper method for scoring and XAI
    # adding separate method in the class to reduce no of combinations
    @pytest.mark.parametrize("model_name", [ModelNames.SERESNEXT])
    @pytest.mark.parametrize("model_explainability", [False, True])
    def test_xai_inference_helper_cpu(self, image_dir, model_name,
                                      model_explainability):
        with tempfile.TemporaryDirectory() as tmp_output_dir:
            task_type = shared_constants.Tasks.IMAGE_CLASSIFICATION
            number_of_classes = 10
            model_wrapper = ModelFactory().get_model_wrapper(model_name,
                                                             number_of_classes,
                                                             multilabel=False,
                                                             device="cpu",
                                                             distributed=False,
                                                             local_rank=0)

            model_wrapper.labels = ["class_" + str(i + 1) for i in range(number_of_classes)]
            score_with_model = _get_scoring_method(task_type=task_type)
            sample_image = os.path.join(image_dir, "crack_1.jpg")
            # format 1
            input_bytes = open(sample_image, "rb").read()
            response = run_inference_helper(model_wrapper,
                                            request_body=input_bytes,
                                            score_with_model=score_with_model,
                                            task_type=task_type)
            result = json.loads(response)
            # keys in result: "filename", "probs", "labels", "visualizations", "attributions"
            self.multiclass_checks(model_wrapper, result, False, False)

            # format 2
            xai_parameters = {'xai_algorithm': ExplainabilityLiterals.GUIDEDBACKPROP_METHOD_NAME}
            json_data_in_bytes = json.dumps({"image": img_to_base64(sample_image),
                                             "model_explainability": model_explainability,
                                             "xai_parameters": xai_parameters}).encode("utf-8")
            response = run_inference_helper(model_wrapper,
                                            request_body=json_data_in_bytes,
                                            score_with_model=score_with_model,
                                            task_type=task_type)
            result = json.loads(response)
            # keys in result: "filename", "probs", "labels", "visualizations", "attributions"
            if model_explainability:
                self.multiclass_checks(model_wrapper, result, True, False)
            else:
                self.multiclass_checks(model_wrapper, result, False, False)
            delete_model_weights()
