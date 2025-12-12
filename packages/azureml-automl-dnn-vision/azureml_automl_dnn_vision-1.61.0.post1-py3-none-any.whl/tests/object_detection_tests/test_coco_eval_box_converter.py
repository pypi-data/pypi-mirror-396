import torch

from azureml.automl.dnn.vision.common.constants import MetricsLiterals
from azureml.automl.dnn.vision.object_detection.common.coco_eval_box_converter import COCOEvalBoxConverter


PRECISION, RECALL = MetricsLiterals.PRECISION, MetricsLiterals.RECALL
AVERAGE_PRECISION, MEAN_AVERAGE_PRECISION = MetricsLiterals.AVERAGE_PRECISION, MetricsLiterals.MEAN_AVERAGE_PRECISION
PER_LABEL_METRICS = MetricsLiterals.PER_LABEL_METRICS


class TestCOCOEvalBoxConverter:
    def test_two_predictions(self):
        index_map = ["cat", "dog"]
        box_converter = COCOEvalBoxConverter(index_map)

        box_converter.add_predictions([
            {
                "filename": "animals.jpg", "width": 640, "height": 480,
                "boxes": torch.tensor([[100, 100, 200, 200], [300, 300, 400, 400]]),
                "labels": torch.tensor([0, 1]), "scores": [0.8, 0.9],
            },
        ])

        eval_bounding_boxes = box_converter.get_boxes()

        assert eval_bounding_boxes == [
            {
                "image_id": "animals.jpg",
                "bbox": [torch.tensor(100), torch.tensor(100), torch.tensor(100), torch.tensor(100)],
                "category_id": "cat", "score": 0.8
            },
            {
                "image_id": "animals.jpg",
                "bbox": [torch.tensor(300), torch.tensor(300), torch.tensor(100), torch.tensor(100)],
                "category_id": "dog", "score": 0.9
            }
        ]

    def test_no_predictions(self):
        index_map = ["cat", "dog"]
        box_converter = COCOEvalBoxConverter(index_map)

        eval_bounding_boxes = box_converter.get_boxes()

        assert len(eval_bounding_boxes) == 0

    def test_multiple_batches(self):
        index_map = ["cat", "dog"]
        box_converter = COCOEvalBoxConverter(index_map)

        for i in range(10):
            box_converter.add_predictions([
                {
                    "filename": "animals{}.jpg".format(i), "width": 640, "height": 480,
                    "boxes": torch.tensor([[100, 100, 200, 200], [300, 300, 400, 400]]),
                    "labels": torch.tensor([0, 1]), "scores": [0.8, 0.9],
                },
            ])

        eval_bounding_boxes = box_converter.get_boxes()

        assert eval_bounding_boxes == [
            {
                "image_id": "animals{}.jpg".format(i // 2),
                "bbox":
                    [torch.tensor(100), torch.tensor(100), torch.tensor(100), torch.tensor(100)] if i % 2 == 0
                    else [torch.tensor(300), torch.tensor(300), torch.tensor(100), torch.tensor(100)],
                "category_id": "cat" if i % 2 == 0 else "dog", "score": 0.8 if i % 2 == 0 else 0.9
            }
            for i in range(20)
        ]

    def test_aggregation(self):
        index_map = ["cat", "dog"]
        box_converter1 = COCOEvalBoxConverter(index_map)
        box_converter2 = COCOEvalBoxConverter(index_map)

        box_converter1.add_predictions([
            {
                "filename": "cat.jpg", "width": 640, "height": 480,
                "boxes": torch.tensor([[100, 100, 200, 200]]),
                "labels": torch.tensor([0]), "scores": [0.8],
            },
        ])
        box_converter2.add_predictions([
            {
                "filename": "dog.jpg", "width": 640, "height": 480,
                "boxes": torch.tensor([[300, 300, 400, 400]]),
                "labels": torch.tensor([1]), "scores": [0.9],
            },
        ])

        eval_bounding_boxes1 = box_converter1.get_boxes()
        eval_bounding_boxes2 = box_converter2.get_boxes()

        eval_bounding_boxes = COCOEvalBoxConverter.aggregate_boxes([eval_bounding_boxes1, eval_bounding_boxes2])
        assert eval_bounding_boxes == [
            {
                "image_id": "cat.jpg",
                "bbox": [torch.tensor(100), torch.tensor(100), torch.tensor(100), torch.tensor(100)],
                "category_id": "cat", "score": 0.8
            },
            {
                "image_id": "dog.jpg",
                "bbox": [torch.tensor(300), torch.tensor(300), torch.tensor(100), torch.tensor(100)],
                "category_id": "dog", "score": 0.9
            }
        ]
