# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""constants needed for exaplainability."""


class ExplainabilityLiterals:
    """Parameters for explainability method names."""

    MODEL_EXPLAINABILITY = "model_explainability"
    XAI_PARAMETERS = "xai_parameters"
    XAI_ALGORITHM = "xai_algorithm"
    XRAI_METHOD_NAME = "xrai"
    INTEGRATEDGRADIENTS_METHOD_NAME = "integrated_gradients"
    GUIDEDGRADCAM_METHOD_NAME = "guided_gradcam"
    GUIDEDBACKPROP_METHOD_NAME = "guided_backprop"
    CONFIDENCE_SCORE_THRESHOLD_MULTILABEL = "confidence_score_threshold_multilabel"
    N_STEPS = "n_steps"
    APPROXIMATION_METHOD = "approximation_method"
    XRAI_FAST = "xrai_fast"


class ExplainabilityDefaults:
    """DEFAULT values for explainability parameters."""

    MODEL_EXPLAINABILITY = False
    XAI_ALGORITHM = ExplainabilityLiterals.XRAI_METHOD_NAME
    OUTPUT_VISUALIZATIONS = True
    OUTPUT_ATTRIBUTIONS = False
    CONFIDENCE_SCORE_THRESHOLD_MULTILABEL = 0.5


class IntegratedGradientsDefaults:
    """DEFAULT parameters for integratedgradients algorithm."""

    N_STEPS = 50  # Range: [2, inf), typical values used are [25, 50, 75, 100]
    N_STEPS_MIN = 2  # minimum value acceptable for N_STEPS
    METHOD = "riemann_middle"  # approximation method name from ['riemann_right', 'riemann_left', 'riemann_middle',
    # 'riemann_trapezoid', 'gausslegendre']
    ALL_METHODS = [
        "riemann_right",
        "riemann_left",
        "riemann_middle",
        "riemann_trapezoid",
        "gausslegendre",
    ]
    INTERNAL_BATCH_SIZE = 5
    RETURN_CONVERGENCE_DELTA = False


class XRAIDefaults:
    """DEFAULT parameters for xrai algorithm."""

    N_STEPS = 50  # Range: [2, inf), typical values used are [25, 50, 75, 100]
    XRAI_FAST = True  # [True, False]
    XRAI_SAMPLES_BATCH = 5  # Number of samples to be generated in XRAI computation


class NoiseTunnelDefaults:
    """DEFAULT parameters for noise tunneling algorithm."""

    NT_TYPE = "smoothgrad"
    NT_SAMPLES = 5
    STDEVS = 0.2
    NT_SAMPLES_BATCH_SIZE = 5


class XAIPredictionLiterals:
    """Strings that will be keys in the output json during prediction."""

    VISUALIZATIONS_KEY_NAME = "visualizations"
    ATTRIBUTIONS_KEY_NAME = "attributions"


class XAIVisualizationDefaults:
    """DEFAULT parameters for XAI visualization."""

    top_x_percent_attributions = 30
    figure_title_fontsize = 20
    savefig_dpi = 100
