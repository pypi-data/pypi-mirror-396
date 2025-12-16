"""
Documentation on Hugging Face: https://huggingface.co/docs/transformers/en/custom_models
"""

from monai.inferers import sliding_window_inference
from monai.losses import DiceCELoss
from transformers import PreTrainedModel
from monai.networks.nets import UNet
from transformers.utils import auto_docstring

from .configuration_unet import UnetConfig


@auto_docstring
class UnetPreTrainedModel(PreTrainedModel):
    config_class = UnetConfig  # type: ignore
    base_model_prefix = "unet"
    main_input_name = "pixel_values"
    supports_gradient_checkpointing = False


@auto_docstring
class UnetModel(UnetPreTrainedModel):

    def __init__(self, config):
        super().__init__(config)
        self.model = UNet(
            spatial_dims=config.spatial_dims,
            in_channels=config.in_channels,
            out_channels=config.out_channels,
            channels=config.channels,
            strides=config.strides,
            kernel_size=config.kernel_size,
            up_kernel_size=config.up_kernel_size,
            num_res_units=config.num_res_units,
            act=config.act,
            norm=config.norm,
            dropout=config.dropout,
            bias=config.bias,
            adn_ordering=config.adn_ordering,
        )

    def forward(self, tensor):
        return self.model(tensor)


# @auto_docstring
class UnetForImageSegmentation(UnetPreTrainedModel):

    def __init__(self, config):
        super().__init__(config)
        self.model = UNet(
            spatial_dims=config.spatial_dims,
            in_channels=config.in_channels,
            out_channels=config.out_channels,
            channels=config.channels,
            strides=config.strides,
            kernel_size=config.kernel_size,
            up_kernel_size=config.up_kernel_size,
            num_res_units=config.num_res_units,
            act=config.act,
            norm=config.norm,
            dropout=config.dropout,
            bias=config.bias,
            adn_ordering=config.adn_ordering,
        )

    def forward(self, tensor: dict, roi_size=(128, 128, 128), sw_batch_size=1):
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
class UnetBackbone(UnetPreTrainedModel):

    def __init__(self, config):
        super().__init__(config)
        self.backbone = UNet(
            spatial_dims=config.spatial_dims,
            in_channels=config.in_channels,
            out_channels=config.out_channels,
            channels=config.channels,
            strides=config.strides,
            kernel_size=config.kernel_size,
            up_kernel_size=config.up_kernel_size,
            num_res_units=config.num_res_units,
            act=config.act,
            norm=config.norm,
            dropout=config.dropout,
            bias=config.bias,
            adn_ordering=config.adn_ordering,
        ).model[:2]

    def forward(self, tensor):
        return self.backbone(tensor)


__all__ = [
    "UnetForImageSegmentation",
    "UnetModel",
    "UnetPreTrainedModel",
    "UnetBackbone",
]
