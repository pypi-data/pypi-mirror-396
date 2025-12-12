# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""XAI attributions generation methods."""

import numpy as np
import saliency.core as saliency
import torch
import torchvision.transforms as T
from azureml.automl.dnn.vision.classification.common.constants import (
    ModelNames,
    ModelParameters,
)
from azureml.automl.dnn.vision.common.exceptions import AutoMLVisionDataException
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.explainability.constants import (
    ExplainabilityDefaults,
    ExplainabilityLiterals,
    IntegratedGradientsDefaults,
    NoiseTunnelDefaults,
    XAIPredictionLiterals,
)
from azureml.automl.dnn.vision.explainability.utils import (
    XaiMultiLabelCustomDataset,
    save_captum_visualizations,
)
from azureml.automl.dnn.vision.explainability.xrai_utils import xrai_utility_method
from captum.attr import GuidedBackprop, GuidedGradCam, IntegratedGradients, NoiseTunnel
from torch.utils.data import DataLoader

logger = get_logger(__name__)


def get_explanations_ig(
    ig_model,
    input_final,
    pred_label_idx,
    n_steps=IntegratedGradientsDefaults.N_STEPS,
    method=IntegratedGradientsDefaults.METHOD,
):
    """Generates attributons based on integratedgradients method

    :param ig_model: Integrated gradients model object
    :type ig_model: captum.attr._core.noise_tunnel.NoiseTunnel
    :param input_final: preprocessed input images
    :type input_final: torch.Tensor
    :param pred_label_idx: predicted label
    :type pred_label_idx: torch.Tensor
    :param n_steps: No of steps needed by IG
    :type n_steps: int
    :param method: method needed by IG
    :type method: str
    :return: attributions
    :rtype: torch.Tensor
    """
    logger.info(
        "Generating attributions using: Integrated Gradients with parameters\
         n_steps: {}, method: {}".format(
            n_steps, method
        )
    )
    attributions_ig_nt = ig_model.attribute(
        inputs=input_final,
        target=pred_label_idx,
        n_steps=n_steps,
        method=method,
        internal_batch_size=IntegratedGradientsDefaults.INTERNAL_BATCH_SIZE,
        return_convergence_delta=IntegratedGradientsDefaults.RETURN_CONVERGENCE_DELTA,
        nt_type=NoiseTunnelDefaults.NT_TYPE,
        nt_samples=NoiseTunnelDefaults.NT_SAMPLES,
        stdevs=NoiseTunnelDefaults.STDEVS,
        nt_samples_batch_size=NoiseTunnelDefaults.NT_SAMPLES_BATCH_SIZE,
    )

    return attributions_ig_nt


def get_explanations_guidedbackprop(gbp_model, input_final, pred_label_idx):
    """Generates attributons based on guidedbackprop method

    :param gbp_model: Guided backprop model object
    :type gbp_model: captum.attr._core.noise_tunnel.NoiseTunnel
    :param input_final: preprocessed input images
    :type input_final: torch.Tensor
    :param pred_label_idx: predicted label
    :type pred_label_idx: torch.Tensor
    :return: attributions
    :rtype: torch.Tensor
    """
    logger.info("Generating attributions using: guided_backprop")
    attributions_gbp_nt = gbp_model.attribute(
        input_final,
        target=pred_label_idx,
        nt_type=NoiseTunnelDefaults.NT_TYPE,
        nt_samples=NoiseTunnelDefaults.NT_SAMPLES,
        stdevs=NoiseTunnelDefaults.STDEVS,
        nt_samples_batch_size=NoiseTunnelDefaults.NT_SAMPLES_BATCH_SIZE,
    )

    return attributions_gbp_nt


def get_explanations_guidedgradcam(ggc_model, input_final, pred_label_idx):
    """Generates attributons based on guidedgradcam method

    :param ggc_model: Guided gradcam model object
    :type ggc_model: captum.attr._core.guided_grad_cam.GuidedGradCam
    :param input_final: preprocessed input images
    :type input_final: torch.Tensor
    :param pred_label_idx: predicted label
    :type pred_label_idx: torch.Tensor
    :return: attributions
    :rtype: torch.Tensor
    """
    logger.info("Generating attributions using: guided_gradcam")
    attributions_ggc = ggc_model.attribute(input_final, target=pred_label_idx)
    return attributions_ggc


def load_xai_method(model_wrapper, xai_method_name):
    """Loads XAI method given a Deep Learning Network and XAI method name

    :param model_wrapper: Model to use for inferencing
    :type model_wrapper: typing.Union[classification.models.BaseModelWrapper]
    :param xai_method_name: xai algorithm name
    :type xai_method_name: str
    :return: XAI model object
    :rtype: typing.Union[saliency.core.xrai.XRAI,
                         captum.attr._core.noise_tunnel.NoiseTunnel,
                         captum.attr._core.guided_grad_cam.GuidedGradCam]
    """

    model_wrapper.model.eval()
    for module in model_wrapper.model.modules():
        if isinstance(module, torch.nn.ReLU):
            module.inplace = False
    if xai_method_name is None:
        xai_method_name = ExplainabilityDefaults.XAI_ALGORITHM

    if xai_method_name == ExplainabilityLiterals.INTEGRATEDGRADIENTS_METHOD_NAME:
        xai_method = IntegratedGradients(model_wrapper.model)
        return NoiseTunnel(xai_method)

    elif xai_method_name == ExplainabilityLiterals.XRAI_METHOD_NAME:
        xai_method = saliency.XRAI()
        return xai_method

    elif xai_method_name == ExplainabilityLiterals.GUIDEDBACKPROP_METHOD_NAME:
        xai_method = GuidedBackprop(model_wrapper.model)
        return NoiseTunnel(xai_method)

    elif xai_method_name == ExplainabilityLiterals.GUIDEDGRADCAM_METHOD_NAME:

        if model_wrapper.model_name == ModelNames.MOBILENETV2:
            return GuidedGradCam(model_wrapper.model, model_wrapper.model.features[-1])

        elif model_wrapper.model_name in [
            ModelNames.SERESNEXT,
            ModelNames.RESNET18,
            ModelNames.RESNET34,
            ModelNames.RESNET50,
            ModelNames.RESNET101,
            ModelNames.RESNET152,
            ModelNames.RESNEST50,
            ModelNames.RESNEST101,
        ]:
            return GuidedGradCam(model_wrapper.model, model_wrapper.model.layer4[-1])

        else:
            # Following vit models and any new model will be marked as not supported
            # ModelNames.VITB16R224,
            # ModelNames.VITS16R224,
            # ModelNames.VITL16R224,
            logger.info(
                "{} doesn't support {}".format(
                    xai_method_name, model_wrapper.model_name
                )
            )
            raise AutoMLVisionDataException(
                "{} doesn't support {}".format(
                    xai_method_name, model_wrapper.model_name
                ),
                has_pii=False,
            )

    else:
        raise AutoMLVisionDataException(
            "Invalid explainability algorithm name {}".format(xai_method_name), has_pii=False
        )


def get_explanations(
    model_wrapper,
    images,
    inference_labels,
    conf_scores,
    pred_label_indices,
    device,
    xai_method,
    xai_method_name,
    **kwargs
):
    """Generates attributions and visualizations

    :param model_wrapper: Model to use for inferencing
    :type model_wrapper: typing.Union[classification.models.BaseModelWrapper]
    :param images: preprocessed input images
    :type images: torch.Tensor
    :param inference_labels: labels or annotations
    :type inference_labels: list
    :param conf_scores: confidence scores
    :type conf_scores: torch.Tensor
    :param pred_label_indices: predicted label indices
    :type pred_label_indices: torch.Tensor
    :param device: device to be used for XAI
    :type device: torch.device
    :param xai_method: XAI model object
    :type xai_method: typing.Union[saliency.core.xrai.XRAI,
                                   captum.attr._core.noise_tunnel.NoiseTunnel,
                                   ]
    :param xai_method_name: xai method name
    :type xai_method_name: str
    :return: visualizations (list of size len(images)), attributions (list of size len(images))
    :rtype: tuple of lists
    """

    logger.info("Generating attributions using: {}".format(xai_method_name))

    if xai_method_name == ExplainabilityLiterals.GUIDEDGRADCAM_METHOD_NAME:

        attributions = get_explanations_guidedgradcam(
            xai_method, images, pred_label_indices
        )

    elif xai_method_name == ExplainabilityLiterals.INTEGRATEDGRADIENTS_METHOD_NAME:

        attributions = get_explanations_ig(
            xai_method,
            images,
            pred_label_indices,
            n_steps=kwargs.get(
                ExplainabilityLiterals.N_STEPS, IntegratedGradientsDefaults.N_STEPS
            ),
            method=kwargs.get(
                ExplainabilityLiterals.APPROXIMATION_METHOD,
                IntegratedGradientsDefaults.METHOD,
            ),
        )

    elif xai_method_name == ExplainabilityLiterals.GUIDEDBACKPROP_METHOD_NAME:

        attributions = get_explanations_guidedbackprop(
            xai_method, images, pred_label_indices
        )

    elif xai_method_name == ExplainabilityLiterals.XRAI_METHOD_NAME:

        attributions = xrai_utility_method(
            model_wrapper, images, pred_label_indices, device, xai_method, **kwargs
        )
    else:
        raise AutoMLVisionDataException("Invalid XAI method name", has_pii=False)

    visualization_image_strs = [None] * len(images)
    if attributions is not None:

        if kwargs.get(
            XAIPredictionLiterals.VISUALIZATIONS_KEY_NAME,
            ExplainabilityDefaults.OUTPUT_VISUALIZATIONS,
        ):
            for (
                idx,
                (images_i, pred_label_indices_i, conf_scores_i, attributions_i,),
            ) in enumerate(zip(images, pred_label_indices, conf_scores, attributions)):
                label_idx = pred_label_indices_i.item()
                prediction_score = conf_scores_i.item()
                image_str = save_captum_visualizations(
                    xai_method_name,
                    attributions_i,
                    images_i.unsqueeze(0),
                    inference_labels[label_idx],
                    prediction_score,
                )
                visualization_image_strs[idx] = image_str

    if kwargs.get(
        XAIPredictionLiterals.ATTRIBUTIONS_KEY_NAME,
        ExplainabilityDefaults.OUTPUT_ATTRIBUTIONS,
    ):
        if attributions is None:
            raise ValueError("Attributions can't be None")
        return (
            visualization_image_strs,
            [
                attr_sample.cpu().detach().numpy().tolist()
                for attr_sample in attributions
            ],
        )

    else:
        return visualization_image_strs, [None] * len(images)


def _xai_batch(
    model_wrapper, batch, probs, inference_labels, device, xai_method, **kwargs
):
    """Generates explanations

    :param model_wrapper: Model to use for inferencing
    :type model_wrapper: typing.Union[classification.models.BaseModelWrapper]
    :param batch: preprocessed input images
    :type batch: torch.Tensor
    :param probs: preprocessed input images
    :type probs: torch.Tensor
    :param inference_labels: labels or annotations
    :type inference_labels: list
    :param device: device to be used for XAI
    :type device: torch.device
    :param xai_method: XAI model object
    :type xai_method: typing.Union[saliency.core.xrai.XRAI,
                                   captum.attr._core.noise_tunnel.NoiseTunnel,
                                   ]
    :param xai_method_name: xai method name
    :type xai_method_name: str
    :return: visualizations (list of size len(images)), attributions (list of size len(images))
    :rtype: tuple of lists
    """
    visualizations, attributions = [None] * len(batch), [None] * len(batch)
    if model_wrapper.multilabel:  # for multi-label classification
        score_threshold = float(
            kwargs.get(
                ExplainabilityLiterals.CONFIDENCE_SCORE_THRESHOLD_MULTILABEL,
                ExplainabilityDefaults.CONFIDENCE_SCORE_THRESHOLD_MULTILABEL,
            )
        )
        final_classes = (probs > score_threshold).type(
            torch.int
        )  # 1 if probs > score_threshold else 0

        # In case of multi-label classification, in each image in the batch of images,
        # it may have more than one labels predicted. Since XAI has to be called against all the labels
        # predicted for each image, we have to explicitly replicate each image for number of labels
        # predicted on that image.

        for img_idx in range(len(batch)):
            multi_labels = (final_classes[img_idx] == 1).nonzero().flatten()
            if multi_labels.nelement() == 0:
                continue
            probs_batch = probs[img_idx][multi_labels]
            # single image will be replicated in dataloader generated samples
            img_multilabel = batch[img_idx]
            # the XaiMultiLabelCustomDataset and DataLoader will be used to get batch of samples and
            # generate explanations
            multilabel_replicated_data = XaiMultiLabelCustomDataset(
                multi_labels, img_multilabel, probs_batch
            )
            multilabel_xai_dataloader = DataLoader(
                multilabel_replicated_data, batch_size=len(batch), shuffle=False
            )

            visualizations_per_image, attributions_per_image = None, None
            for img_replica_idx, sample_replica_batch in enumerate(
                multilabel_xai_dataloader
            ):
                (
                    visualizations_per_replica_batch,
                    attributions_per_replica_batch,
                ) = get_explanations(
                    model_wrapper,
                    sample_replica_batch[0],
                    inference_labels,
                    sample_replica_batch[2],
                    sample_replica_batch[1],
                    device=device,
                    xai_method=xai_method,
                    xai_method_name=kwargs.get(
                        ExplainabilityLiterals.XAI_ALGORITHM,
                        ExplainabilityDefaults.XAI_ALGORITHM,
                    ),
                    **kwargs
                )
                # aggregate visualizations and attributions for each image with multiple labels
                if visualizations_per_replica_batch is not None:
                    if visualizations_per_image is None:
                        visualizations_per_image = []
                    visualizations_per_image.extend(visualizations_per_replica_batch)
                if attributions_per_replica_batch is not None:
                    if attributions_per_image is None:
                        attributions_per_image = []
                    attributions_per_image.extend(attributions_per_replica_batch)
            # store aggregated visualizations and attributions per image at image index
            if visualizations_per_image is not None:
                visualizations[img_idx] = visualizations_per_image  # type: ignore
            if attributions_per_image is not None:
                attributions[img_idx] = attributions_per_image  # type: ignore
    else:  # for multi-class classification
        conf_scores, class_predictions = torch.max(probs, dim=1)

        visualizations, attributions = get_explanations(
            model_wrapper,
            batch,
            inference_labels,
            conf_scores,
            class_predictions,
            device=device,
            xai_method=xai_method,
            xai_method_name=kwargs.get(
                ExplainabilityLiterals.XAI_ALGORITHM,
                ExplainabilityDefaults.XAI_ALGORITHM,
            ),
            **kwargs
        )
    model_wrapper.model.eval()
    return visualizations, attributions
