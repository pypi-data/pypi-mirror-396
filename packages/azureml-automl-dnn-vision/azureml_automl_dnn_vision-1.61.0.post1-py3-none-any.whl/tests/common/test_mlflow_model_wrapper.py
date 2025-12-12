import pytest
import base64
import pandas as pd
import json
import os

from azureml.automl.dnn.vision.common.mlflow.mlflow_model_wrapper import MLFlowImagesModelWrapper
from azureml.automl.dnn.vision.common.constants import MLFlowSchemaLiterals
from azureml.automl.dnn.vision.explainability.constants import XAIPredictionLiterals


class TestMLFlowImagesModelWrapper():
    """
    Test class for MLFlowImagesModelWrapper
    """

    TEST_IMAGE_PATH = os.path.join(os.path.dirname(__file__), '../data/classification_data/images/crack_1.jpg')

    IC_RESULT = {
        "probs": [
            2.098e-06,
            4.783e-08,
            0.999,
            8.637e-06
        ],
        "labels": [
            "can",
            "carton",
            "milk_bottle",
            "water_bottle"
        ],
        "visualizations": None,
        "attributions": None
    }

    OD_RESULT = {
        "boxes": [
            {
                "box": {
                    "topX": 0.224,
                    "topY": 0.285,
                    "bottomX": 0.399,
                    "bottomY": 0.620
                },
                "label": "milk_bottle",
                "score": 0.937
            },
            {
                "box": {
                    "topX": 0.664,
                    "topY": 0.484,
                    "bottomX": 0.959,
                    "bottomY": 0.812
                },
                "label": "can",
                "score": 0.891
            },
            {
                "box": {
                    "topX": 0.423,
                    "topY": 0.253,
                    "bottomX": 0.632,
                    "bottomY": 0.725
                },
                "label": "water_bottle",
                "score": 0.876
            }
        ]
    }

    IC_RESULT_EXPLAIN = {
        "probs": [
            0.006,
            9.345e-05,
            0.992,
            0.003
        ],
        "labels": [
            "can",
            "carton",
            "milk_bottle",
            "water_bottle"
        ],
        "visualizations": "iVBORw0KGgoAAAAN.....",
        "attributions": [
            [
                [-4.2969e-04, -1.3090e-03, 7.7791e-04, 2.6677e-04,
                 -5.5195e-03, 1.7989e-03],
                [-5.8236e-03, -7.9108e-04, -2.6963e-03, 2.6517e-03,
                 1.2546e-03, 6.6507e-04]
            ]
        ]
    }

    @pytest.mark.parametrize(
        "image_file",
        [
            (TEST_IMAGE_PATH)
        ]
    )
    def test_process_image(self, image_file):
        with open(image_file, 'rb') as f:
            image = f.read()

        # test binary input
        binary_result = MLFlowImagesModelWrapper._process_image(pd.Series(image))
        # test string input
        string_result = MLFlowImagesModelWrapper._process_image(pd.Series(base64.encodebytes(image).decode('utf-8')))

        # verify that these are equivalent
        assert binary_result[0] == image
        assert string_result[0] == binary_result[0]

    @pytest.mark.parametrize(
        "result,explain",
        [
            (IC_RESULT, True),
            (OD_RESULT, False),
            (IC_RESULT_EXPLAIN, True)
        ]
    )
    def test_process_result(self, result, explain):
        processed_result = MLFlowImagesModelWrapper._process_result(json.dumps(result), explain)

        if not explain:
            assert XAIPredictionLiterals.VISUALIZATIONS_KEY_NAME not in processed_result
            assert XAIPredictionLiterals.ATTRIBUTIONS_KEY_NAME not in processed_result
        else:
            assert processed_result[XAIPredictionLiterals.VISUALIZATIONS_KEY_NAME] == result['visualizations']
            assert processed_result[XAIPredictionLiterals.ATTRIBUTIONS_KEY_NAME] == result['attributions']

        if "probs" in result:
            assert processed_result[MLFlowSchemaLiterals.OUTPUT_COLUMN_PROBS] == result["probs"]
        if "boxes" in result:
            assert processed_result[MLFlowSchemaLiterals.OUTPUT_COLUMN_BOXES] == result["boxes"]
        if "labels" in result:
            assert processed_result[MLFlowSchemaLiterals.OUTPUT_COLUMN_LABELS] == result["labels"]
