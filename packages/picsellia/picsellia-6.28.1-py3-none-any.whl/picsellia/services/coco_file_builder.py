import math

from picsellia_annotations.coco import Annotation as COCOAnnotation
from picsellia_annotations.coco import Category as COCOCategory
from picsellia_annotations.coco import COCOFile
from picsellia_annotations.coco import Image as COCOImage

from picsellia.sdk.asset import MultiAsset


class COCOFileBuilder:
    def __init__(self, categories: dict[str, int]):
        self.categories = categories
        self.assets = {}
        self.coco_annotations = []
        self.coco_images = []
        self.coco_categories = []

    @staticmethod
    def prepare_categories(
        label_names: list[str],
        enforced_ordered_labels: list[str] | None = None,
    ) -> dict[str, int]:
        """This method returns a dict with name matching category id of labels.
        If enforced_ordered_labels is given, it will first put labels in given order, and then put remaining labels
        If not, it will be in the natural order (so created_at)
        """
        labels = {}
        if enforced_ordered_labels:
            for k in range(len(enforced_ordered_labels)):
                labels[enforced_ordered_labels[k]] = k

        for label in label_names:
            if not enforced_ordered_labels or label not in enforced_ordered_labels:
                labels[label] = len(labels)

        return labels

    def load_coco_annotations(self, loaded_annotations: dict[str, list]) -> list[str]:
        for asset_id, annotations in loaded_annotations.items():
            if len(annotations) == 0:
                continue

            # As load_annotations() return the annotations ordered by -created_at
            # we need to build shape for the first annotation of the list
            annotation = annotations[0]
            image_id = len(self.assets)
            self.assets[asset_id] = image_id
            self._build_coco_shapes(image_id, annotation)

        return list(self.assets.keys())

    def load_coco_images(self, loaded_assets: MultiAsset, use_id: bool = False):
        for asset in loaded_assets:
            asset_id = str(asset.id)
            if asset_id in self.assets:
                if use_id:
                    file_name = asset.id_with_extension
                else:
                    file_name = asset.filename
                coco_image = COCOImage(
                    id=self.assets[asset_id],
                    file_name=file_name,
                    width=asset.width,
                    height=asset.height,
                )
                self.coco_images.append(coco_image)

    def load_coco_categories(self):
        for label_name, k in self.categories.items():
            category = COCOCategory(id=k, name=label_name)
            self.coco_categories.append(category)

        # Return categories by order of id
        self.coco_categories = sorted(self.coco_categories, key=lambda cat: cat.id)

    def build(self) -> COCOFile:
        return COCOFile(
            categories=self.coco_categories,
            images=self.coco_images,
            annotations=self.coco_annotations,
        )

    def _build_coco_shapes(self, image_id: int, annotation: dict):
        if "classifications" in annotation and annotation["classifications"]:
            for classification in annotation["classifications"]:
                category_id = self.categories[classification["label"]]
                coco_annotation = COCOAnnotation(
                    id=len(self.coco_annotations),
                    image_id=image_id,
                    category_id=category_id,
                    bbox=[],
                    segmentation=[],
                )
                self.coco_annotations.append(coco_annotation)

        if "rectangles" in annotation and annotation["rectangles"]:
            for rectangle in annotation["rectangles"]:
                category_id = self.categories[rectangle["label"]]
                if "area" in rectangle:
                    area = rectangle["area"]
                else:
                    area = float(rectangle["w"] * rectangle["h"])
                coco_annotation = COCOAnnotation(
                    id=len(self.coco_annotations),
                    image_id=image_id,
                    category_id=category_id,
                    bbox=[
                        rectangle["x"],
                        rectangle["y"],
                        rectangle["w"],
                        rectangle["h"],
                    ],
                    segmentation=[],
                    area=area,
                )
                self.coco_annotations.append(coco_annotation)

        if "polygons" in annotation and annotation["polygons"]:
            for polygon in annotation["polygons"]:
                if (
                    "polygon" not in polygon or not polygon["polygon"]
                ):  # pragma: no cover
                    continue
                category_id = self.categories[polygon["label"]]
                bbox, shape = COCOFileBuilder._compute_bbox_and_shape(
                    polygon["polygon"]
                )
                if "area" in polygon:
                    area = polygon["area"]
                else:
                    area = None
                coco_annotation = COCOAnnotation(
                    id=len(self.coco_annotations),
                    image_id=image_id,
                    category_id=category_id,
                    bbox=bbox,
                    segmentation=[shape],  # COCO needs an array around polygons
                    area=area,
                )
                self.coco_annotations.append(coco_annotation)

    @staticmethod
    def _compute_bbox_and_shape(
        polygon: list[list[int | float]],
    ) -> tuple[list[int | float], list[int | float]]:
        x_min = math.inf
        x_max = -1
        y_min = math.inf
        y_max = -1

        segmentation = []
        for point in polygon:
            x = point[0]
            x_min = min(x, x_min)
            x_max = max(x, x_max)
            y = point[1]
            y_min = min(y, y_min)
            y_max = max(y, y_max)
            segmentation.append(x)
            segmentation.append(y)

        return [x_min, y_min, x_max - x_min, y_max - y_min], segmentation
