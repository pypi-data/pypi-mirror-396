from pydantic import BaseModel, Field, model_validator

from picsellia.types.enums import InferenceType


class PredictionFormat(BaseModel):
    detection_classes: list[int]
    detection_texts: list[str] | None = None

    @property
    def model_type(cls) -> InferenceType:  # pragma: no cover
        raise NotImplementedError()


class ClassificationPredictionFormat(PredictionFormat):
    detection_scores: list[float]

    @property
    def model_type(cls) -> InferenceType:
        return InferenceType.CLASSIFICATION

    @model_validator(mode="before")
    @classmethod
    def check_sizes(cls, data):
        labels, scores = (
            data.get("detection_classes"),
            data.get("detection_scores"),
        )

        if labels is None or scores is None or len(labels) != len(scores):
            raise ValueError("incoherent lists")

        texts = data.get("detection_texts")
        if texts and len(texts) != len(labels):
            raise ValueError(
                "texts are not well defined, there must be exactly the same count of texts than classes"
            )

        return data


class DetectionPredictionFormat(PredictionFormat):
    detection_boxes: list[list[int]]
    detection_scores: list[float]

    @property
    def model_type(cls) -> InferenceType:
        return InferenceType.OBJECT_DETECTION

    @model_validator(mode="before")
    @classmethod
    def check_sizes(cls, data):
        labels, scores, boxes = (
            data.get("detection_classes"),
            data.get("detection_scores"),
            data.get("detection_boxes"),
        )

        if (
            labels is None
            or scores is None
            or boxes is None
            or len(labels) != len(scores)
            or len(boxes) != len(labels)
        ):
            raise ValueError("incoherent lists")

        texts = data.get("detection_texts")
        if texts and len(texts) != len(labels):
            raise ValueError(
                "texts are not well defined, there must be exactly the same count of texts and classes"
            )

        return data


class SegmentationPredictionFormat(PredictionFormat):
    detection_scores: list[float]
    detection_masks: list[list[list[int]]]

    detection_boxes: list[list[int]] = Field(
        default=None, exclude=True, deprecated=True
    )

    @property
    def model_type(cls) -> InferenceType:
        return InferenceType.SEGMENTATION

    @model_validator(mode="before")
    @classmethod
    def check_sizes(cls, data):
        labels, scores, masks = (
            data.get("detection_classes"),
            data.get("detection_scores"),
            data.get("detection_masks"),
        )

        if (
            labels is None
            or scores is None
            or masks is None
            or len(labels) != len(scores)
            or len(masks) != len(labels)
        ):
            raise ValueError("incoherent lists")

        texts = data.get("detection_texts")
        if texts and len(texts) != len(labels):
            raise ValueError(
                "texts are not well defined, there must be exactly the same count of texts than classes"
            )

        return data
