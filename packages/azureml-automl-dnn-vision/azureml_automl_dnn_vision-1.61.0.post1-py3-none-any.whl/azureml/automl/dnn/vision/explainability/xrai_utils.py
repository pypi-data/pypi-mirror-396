# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""XRAI attributions generation methods."""

import numpy as np
import saliency.core as saliency
import torch
import torchvision.transforms as T
from azureml.automl.dnn.vision.classification.common.constants import ModelParameters
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.utils import strtobool
from azureml.automl.dnn.vision.explainability.constants import (
    ExplainabilityLiterals,
    XRAIDefaults,
)

logger = get_logger(__name__)


def preprocess_images_xrai(image_sample, device):
    """Perform normalization on image and enable gradient computation
    :param images: images from xrai
    :type images: torch.Tensor
    :param device: device to be used to attribution generation
    :type device: str
    :return: Normalized images
    :rtype: torch.Tensor
    """

    transformer = T.Compose(
        [
            T.Normalize(
                ModelParameters.DEFAULT_IMAGE_MEAN, ModelParameters.DEFAULT_IMAGE_STD
            )
        ]
    )
    image_sample = np.array(image_sample)
    image_sample = image_sample / 255
    image_sample = np.transpose(image_sample, (0, 3, 1, 2))
    image_sample = torch.tensor(image_sample, dtype=torch.float32)
    image_sample = image_sample.to(device)
    image_sample = transformer(image_sample)
    return image_sample.requires_grad_(True)


def xrai_utility_method(
    model_wrapper, images, pred_label_indices, device, xai_method, **kwargs
):
    """Generates attributons for XRAI

    :param model_wrapper: Model to use for inferencing
    :type model_wrapper: typing.Union[classification.models.BaseModelWrapper]
    :param images: preprocessed input images
    :type images: torch.Tensor
    :param pred_label_indices: predicted label indices
    :type pred_label_indices: torch.Tensor
    :param device: device to be used for XAI
    :type device: torch.device
    :param xai_method: XRAI model object
    :type xai_method: saliency.core.xrai.XRAI
    :return: attributions
    :rtype: torch.Tensor
    """
    model = model_wrapper.model
    model.eval()
    mean = np.array(ModelParameters.DEFAULT_IMAGE_MEAN)
    std = np.array(ModelParameters.DEFAULT_IMAGE_STD)
    unnormalize = T.Normalize((-mean / std).tolist(), (1.0 / std).tolist())
    input_chw_inv = unnormalize(images)
    input_hwc = np.transpose(input_chw_inv.cpu().detach().numpy(), (0, 2, 3, 1))
    input_hwc = input_hwc.astype(np.float32)

    def call_model_function(image_sample, call_model_args=None, expected_keys=None):

        image_sample = preprocess_images_xrai(image_sample, device)
        target_class_idx = call_model_args["class_idx_str"]
        with torch.enable_grad():
            output = model(image_sample)
            m = torch.nn.Softmax(dim=1)
            output = m(output)
            if saliency.base.INPUT_OUTPUT_GRADIENTS in expected_keys:
                outputs = output[:, target_class_idx]
                grads = torch.autograd.grad(
                    outputs, image_sample, grad_outputs=torch.ones_like(outputs)
                )
                grads = torch.movedim(grads[0], 1, 3)
                gradients = grads.cpu().detach().numpy()
                return {saliency.base.INPUT_OUTPUT_GRADIENTS: gradients}

    # with torch.enable_grad():
    attributions_xrai = []
    for i in range(len(images)):
        label_idx = pred_label_indices[i].item()
        call_model_args = {"class_idx_str": label_idx}
        attributions = get_explanations_xrai_saliency(
            xai_method,
            input_hwc[i],
            call_model_function,
            call_model_args,
            steps=kwargs.get(ExplainabilityLiterals.N_STEPS, XRAIDefaults.N_STEPS),
            xrai_fast=bool(
                strtobool(
                    str(
                        kwargs.get(
                            ExplainabilityLiterals.XRAI_FAST, XRAIDefaults.XRAI_FAST
                        )
                    )
                )
            ),
        )
        # if attributions array has atleast 2 dimensions
        if attributions is not None and attributions.ndim >= 2:
            # attributions array has shape
            # [model_wrapper.valid_crop_size, model_wrapper.valid_crop_size]
            attributions_xrai.append(
                torch.from_numpy(attributions)
                .expand(
                    1,
                    3,
                    attributions.shape[-2],
                    attributions.shape[-1],
                )
                .to(device)
            )
    return torch.cat(attributions_xrai)


def get_explanations_xrai_saliency(
    xai_model,
    input_numpy,
    call_model_function,
    call_model_args,
    steps=XRAIDefaults.N_STEPS,
    xrai_fast=XRAIDefaults.XRAI_FAST,
):
    """ Generates attributons based on XRAI method

    :param xai_model: XRAI model object
    :type xai_model: saliency.core.xrai.XRAI
    :param input_numpy: preprocessed input images in numpy
    :type input_numpy: numpy.ndarray
    :param call_model_function: function to be used in XRAI
    :type call_model_function: function
    :param call_model_args: arguments to the function used by XRAI
    :type call_model_args: dict
    :param target_class: predicted class index for which attribution has to be generated
    :type target_class: int
    :param steps: No of steps needed by IG within XRAI
    :type steps: int
    :param xrai_fast: whether to use faster version of XRAI
    :type xrai_fast: bool
    :return: attributions
    :rtype: torch.Tensor
    """
    logger.info(
        "Generating attributions using: XRAI with parameters\
         n_steps: {}, xrai_fast: {}".format(
            steps, xrai_fast
        )
    )

    xrai_params = saliency.XRAIParameters()
    if xrai_fast:
        xrai_params.algorithm = "fast"
    xrai_params.steps = steps
    attribution_xrai = xai_model.GetMask(
        input_numpy,
        call_model_function,
        call_model_args,
        extra_parameters=xrai_params,
        batch_size=XRAIDefaults.XRAI_SAMPLES_BATCH,
    )

    return attribution_xrai
