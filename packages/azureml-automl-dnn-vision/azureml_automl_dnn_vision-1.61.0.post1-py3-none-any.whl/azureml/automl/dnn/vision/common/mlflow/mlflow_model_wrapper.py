# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

"""Mlflow PythonModel wrapper class that loads the Mlflow model, preprocess inputs and performs inference."""

import base64
import json
import tempfile
from typing import Any, Callable, Dict

import pandas as pd
from azureml.automl.core.shared import logging_utilities
from azureml.automl.dnn.vision.common.constants import MLFlowSchemaLiterals
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.utils import strtobool
from azureml.automl.dnn.vision.explainability.constants import (
    ExplainabilityDefaults, ExplainabilityLiterals, XAIPredictionLiterals)

import mlflow

logger = get_logger(__name__)


class MLFlowImagesModelWrapper(mlflow.pyfunc.PythonModel):
    """MLFlow model wrapper for AutoML for Images models."""

    def __init__(
        self,
        task_type: str,
        scoring_method: Callable[..., None],
        model_settings: Dict[str, Any],
    ) -> None:
        """This method is called when the python model wrapper is initialized.

        :param model_settings: Settings for the model.
        :type model_settings: dict
        :param task_type: Task type used in training.
        :type task_type: str
        :param scoring_method: scoring function corresponding to the task type.
        :type scoring_method: python method
        """
        super().__init__()
        self._task_type = task_type
        self._scoring_method = scoring_method
        self._model_settings = model_settings

    def load_context(self, context: mlflow.pyfunc.PythonModelContext) -> None:
        """This method is called when loading a Mlflow model with pyfunc.load_model().

        :param context: Mlflow context containing artifacts that the model can use for inference.
        :type context: mlflow.pyfunc.PythonModelContext
        """
        from azureml.automl.dnn.vision.common.model_export_utils import \
            load_model

        with open(context.artifacts["settings"]) as f:
            self._model_settings = json.load(f)
        try:
            self._model = load_model(
                self._task_type, context.artifacts["model"], **self._model_settings
            )
        except Exception as e:
            logger.warning("Failed to load the the model.")
            logging_utilities.log_traceback(e, logger)
            raise

    @staticmethod
    def _process_image(img: pd.Series) -> pd.Series:
        """This method decodes input data from binary or base64 string format.
        https://github.com/mlflow/mlflow/blob/master/examples/flower_classifier/image_pyfunc.py

        :param img: pandas series with image in binary or base64 string format.
        :type img: pd.Series
        :return: decoded image in pandas series format.
        :rtype: Pandas Series
        """
        if isinstance(img[0], bytes):
            return pd.Series(img[0])
        elif isinstance(img[0], str):
            try:
                return pd.Series(base64.b64decode(img[0]))
            except ValueError:
                raise ValueError("The provided image string cannot be decoded."
                                 "Expected format is bytes or base64 string.")
        else:
            raise ValueError(f"Image received in {type(img[0])} format which is not supported."
                             "Expected format is bytes or base64 string.")

    @staticmethod
    def _process_result(result: str, explain: bool) -> dict:
        """
        This method formats the output of the predict function

        :param result: inference result as json string
        :type result: string
        :param explain: whether or not model explainability is requested
        :type explain: bool
        :return: result record to report to user
        :rtype: dict
        """
        result_dict = json.loads(result)
        keep_keys = [MLFlowSchemaLiterals.OUTPUT_COLUMN_PROBS, MLFlowSchemaLiterals.OUTPUT_COLUMN_BOXES,
                     MLFlowSchemaLiterals.OUTPUT_COLUMN_LABELS]
        if explain:
            keep_keys.append(XAIPredictionLiterals.VISUALIZATIONS_KEY_NAME)
            keep_keys.append(XAIPredictionLiterals.ATTRIBUTIONS_KEY_NAME)
        return_dict = {}
        for key in keep_keys:
            if key in result_dict:
                return_dict[key] = result_dict[key]
        return return_dict

    def predict(
        self, context: mlflow.pyfunc.PythonModelContext, input_data: pd.DataFrame
    ) -> pd.DataFrame:
        """This method performs inference on the input data.

        :param context: Mlflow context containing artifacts that the model can use for inference.
        :type context: mlflow.pyfunc.PythonModelContext
        :param input_data: Input images for prediction.
        :type input_data: Pandas DataFrame with a first column name ['image'] of images where each
        image is in base64 String format.
        :return: Output of inferencing
        :rtype: Pandas DataFrame with columns ['filename', 'probs', 'labels'] for classification and
        ['filename', 'boxes'] for object detection, instance segmentation
        """
        from azureml.automl.dnn.vision.common.model_export_utils import (
            create_temp_file, run_inference_batch)

        # whether the rows in dataframe are dictionaries (for xai) or base64 strings (for just scoring)
        dict_input_format = False
        # Read explainability parameters if available in dictionary at input_data first row
        xai_params = {}
        record = input_data.loc[0, MLFlowSchemaLiterals.INPUT_COLUMN_IMAGE]

        # Acceptable inputs are only string (str) and binary (bytes)
        if isinstance(record, str):
            try:
                xai_params = json.loads(input_data.loc[0, MLFlowSchemaLiterals.INPUT_COLUMN_IMAGE])
                dict_input_format = True
            except Exception:
                logger.info("input data format isn't for XAI.")
        elif not isinstance(record, bytes):  # if not str or bytes, raise error for incompatible format
            logger.info("input data format is incompatible.")
            raise ValueError("incompatible input format")

        def get_json_dict(x: pd.Series) -> pd.Series:
            return json.loads(x[0])[MLFlowSchemaLiterals.INPUT_IMAGE_KEY]

        if dict_input_format:
            # As explainability parameters have been taken out from first row,
            # update the column to have only base64 images
            input_data.loc[:, MLFlowSchemaLiterals.INPUT_COLUMN_IMAGE] = input_data.loc[
                :, [MLFlowSchemaLiterals.INPUT_COLUMN_IMAGE]
            ].apply(axis=1, func=get_json_dict)

        # Decode the base64 image column
        decoded_images = input_data.loc[
            :, [MLFlowSchemaLiterals.INPUT_COLUMN_IMAGE]
        ].apply(axis=1, func=MLFlowImagesModelWrapper._process_image)

        model_explainability = xai_params.get(
            ExplainabilityLiterals.MODEL_EXPLAINABILITY, ExplainabilityDefaults.MODEL_EXPLAINABILITY
        )
        model_explainability = bool(strtobool(str(model_explainability)))

        xai_parameters = xai_params.get(ExplainabilityLiterals.XAI_PARAMETERS, {})

        with tempfile.TemporaryDirectory() as tmp_output_dir:
            image_path_list = (
                decoded_images.iloc[:, 0]
                .map(lambda row: create_temp_file(row, tmp_output_dir))
                .tolist()
            )
            result = run_inference_batch(
                self._model,
                image_path_list,
                self._scoring_method,
                model_explainability=model_explainability,
                **xai_parameters
            )

        return pd.DataFrame(map(MLFlowImagesModelWrapper._process_result,
                                result, [model_explainability] * len(result)))
