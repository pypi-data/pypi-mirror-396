"""
Documentation on Hugging Face: https://huggingface.co/docs/transformers/en/custom_models

Examples:
https://github.com/huggingface/transformers/tree/main/src/transformers/models
"""

from monai.inferers import sliding_window_inference
from monai.losses import DiceCELoss
from transformers import PreTrainedModel
from monai.networks.nets import SwinUNETR
from transformers.utils import auto_docstring

from .configuration_swinunetr2 import (
    SwinUNETRv2Config,
)


@auto_docstring
class SwinUNETRv2PreTrainedModel(PreTrainedModel):
    config_class = SwinUNETRv2Config  # type: ignore
    base_model_prefix = "swinunetrv2"
    main_input_name = "pixel_values"
    supports_gradient_checkpointing = False


@auto_docstring
class SwinUNETRv2Model(SwinUNETRv2PreTrainedModel):

    def __init__(self, config):
        super().__init__(config)
        self.model = SwinUNETR(
            in_channels=config.in_channels,
            out_channels=config.out_channels,
            patch_size=config.patch_size,
            depths=config.depths,
            num_heads=config.num_heads,
            window_size=config.window_size,
            qkv_bias=config.qkv_bias,
            mlp_ratio=config.mlp_ratio,
            feature_size=config.feature_size,
            norm_name=config.norm_name,
            drop_rate=config.drop_rate,
            attn_drop_rate=config.attn_drop_rate,
            dropout_path_rate=config.dropout_path_rate,
            normalize=config.normalize,
            patch_norm=config.patch_norm,
            use_checkpoint=config.use_checkpoint,
            spatial_dims=config.spatial_dims,
            downsample=config.downsample,
            use_v2=True,
        )

    def forward(self, tensor):
        return self.model(tensor)


# @auto_docstring
class SwinUNETRv2ForImageSegmentation(SwinUNETRv2PreTrainedModel):

    def __init__(self, config):
        super().__init__(config)
        self.model = SwinUNETR(
            in_channels=config.in_channels,
            out_channels=config.out_channels,
            patch_size=config.patch_size,
            depths=config.depths,
            num_heads=config.num_heads,
            window_size=config.window_size,
            qkv_bias=config.qkv_bias,
            mlp_ratio=config.mlp_ratio,
            feature_size=config.feature_size,
            norm_name=config.norm_name,
            drop_rate=config.drop_rate,
            attn_drop_rate=config.attn_drop_rate,
            dropout_path_rate=config.dropout_path_rate,
            normalize=config.normalize,
            patch_norm=config.patch_norm,
            use_checkpoint=config.use_checkpoint,
            spatial_dims=config.spatial_dims,
            downsample=config.downsample,
            use_v2=True,
        )

    def forward(self, tensor: dict, roi_size=(128, 128, 128), sw_batch_size=1) -> dict:
        criterion = DiceCELoss(to_onehot_y=True, softmax=True)
        image = tensor["image"]
        annotations = None
        if "annotations" in tensor:
            annotations = tensor["annotations"]

        if self.training:
            logits = self.model(image)

        else:
            logits = sliding_window_inference(
                tensor["image"],
                roi_size,
                sw_batch_size,
                self.model.forward,
            )

        result = {"logits": logits}
        if "annotations" in tensor:
            result["loss"] = criterion(logits, annotations)
        return result


@auto_docstring
class SwinUNETRv2Backbone(SwinUNETRv2PreTrainedModel):

    def __init__(self, config):
        super().__init__(config)
        self.swinViT = SwinUNETR(
            in_channels=config.in_channels,
            out_channels=config.out_channels,
            patch_size=config.patch_size,
            depths=config.depths,
            num_heads=config.num_heads,
            window_size=config.window_size,
            qkv_bias=config.qkv_bias,
            mlp_ratio=config.mlp_ratio,
            feature_size=config.feature_size,
            norm_name=config.norm_name,
            drop_rate=config.drop_rate,
            attn_drop_rate=config.attn_drop_rate,
            dropout_path_rate=config.dropout_path_rate,
            normalize=config.normalize,
            patch_norm=config.patch_norm,
            use_checkpoint=config.use_checkpoint,
            spatial_dims=config.spatial_dims,
            downsample=config.downsample,
            use_v2=True,
        ).swinViT

    def forward(self, tensor):
        return self.swinViT(tensor)


__all__ = [
    "SwinUNETRv2ForImageSegmentation",
    "SwinUNETRv2Model",
    "SwinUNETRv2PreTrainedModel",
    "SwinUNETRv2Backbone",
]
