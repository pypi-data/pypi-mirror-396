import numpy as np
from monai.transforms import (
    Compose,
    LoadImaged,
    CastToTyped,
    EnsureChannelFirstd,
    Orientationd,
    ScaleIntensityd,
    SpatialPadd,
    NormalizeIntensityd,
)
from transformers import BaseImageProcessor
from transformers.image_processing_base import BatchFeature


class UnetImageProcessor(BaseImageProcessor):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.roi_size = kwargs.get("roi_size", (128, 128, 128))
        self.image_dtype = kwargs.get("image_dtype", "int16")
        self.annotation_dtype = kwargs.get("annotation_dtype", "uint8")
        self.normalization = kwargs.get("normalization", "ScaleIntensityd")

    def __call__(
        self, images, annotations: str | None = None, **kwargs
    ) -> BatchFeature:
        """Preprocess an image or a batch of images."""
        return self.preprocess(images, annotations, **kwargs)

    def preprocess(
        self,
        images: str | dict,
        annotations: str | None = None,
        **kwargs,
    ) -> BatchFeature:

        if isinstance(images, dict):  # unpack dict
            if "annotations" in images:
                annotations = images["annotations"]
            images = images["image"]

        if annotations is None:
            inference_transforms = self.get_inference_data_transforms(
                self.image_dtype, self.roi_size
            )
            return inference_transforms({"image": images})
        else:
            train_transforms = self.get_annotated_data_transforms(
                np.dtype(self.image_dtype),
                np.dtype(self.annotation_dtype),
                self.roi_size,
            )
            return train_transforms({"image": images, "annotations": annotations})

    def get_normalize(self):
        if self.normalization == "NormalizeIntensityd":
            return NormalizeIntensityd(keys="image", nonzero=True, channel_wise=True)

        return ScaleIntensityd(keys=["image"])

    def get_annotated_data_transforms(self, image_dtype, annotation_dtype, roi_size):
        return Compose(
            [
                LoadImaged(keys=["image", "annotations"]),
                CastToTyped(keys="image", dtype=image_dtype),
                CastToTyped(keys="annotations", dtype=annotation_dtype),
                EnsureChannelFirstd(keys=["image", "annotations"]),
                Orientationd(keys=["image", "annotations"], axcodes="RAS"),
                self.get_normalize(),
                SpatialPadd(keys=["image", "annotations"], spatial_size=roi_size),
            ]
        )

    def get_inference_data_transforms(self, image_dtype, roi_size):
        return Compose(
            [
                LoadImaged(keys=["image"]),
                CastToTyped(keys="image", dtype=image_dtype),
                EnsureChannelFirstd(keys=["image"]),
                Orientationd(keys=["image"], axcodes="RAS"),
                self.get_normalize(),
                SpatialPadd(keys=["image"], spatial_size=roi_size),
            ]
        )
