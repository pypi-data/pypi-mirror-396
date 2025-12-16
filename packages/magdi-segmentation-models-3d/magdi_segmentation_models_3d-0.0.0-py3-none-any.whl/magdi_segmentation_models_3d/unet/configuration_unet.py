from transformers import PretrainedConfig
from transformers.utils import logging

from transformers.utils.backbone_utils import (
    BackboneConfigMixin,
    get_aligned_output_features_output_indices,
)
from collections.abc import Sequence
from monai.networks.layers.factories import Act, Norm

logger = logging.get_logger(__name__)


class UnetConfig(BackboneConfigMixin, PretrainedConfig):

    model_type = "unet"

    def __init__(
        self,
        spatial_dims: int = 3,
        in_channels: int = 1,
        out_channels: int = 1,
        channels: Sequence[int] = (64, 128, 256, 512, 1024),
        strides: Sequence[int] = (2, 2, 2, 2),
        kernel_size: Sequence[int] | int = 3,
        up_kernel_size: Sequence[int] | int = 3,
        num_res_units: int = 0,
        act: tuple | str = Act.PRELU,
        norm: tuple | str = Norm.INSTANCE,
        dropout: float = 0.0,
        bias: bool = True,
        adn_ordering: str = "NDA",
        out_features=None,
        out_indices=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.spatial_dims = spatial_dims
        self.in_channels = in_channels
        self.out_channels = out_channels

        self.channels = channels
        self.strides = strides
        self.kernel_size = kernel_size
        self.up_kernel_size = up_kernel_size
        self.num_res_units = num_res_units
        self.act = act
        self.norm = norm
        self.dropout = dropout
        self.bias = bias
        self.adn_ordering = adn_ordering

        depths = [1]
        self.stage_names = ["stem"] + [
            f"stage{idx}" for idx in range(1, len(depths) + 1)
        ]

        self._out_features, self._out_indices = (
            get_aligned_output_features_output_indices(
                out_features=out_features,
                out_indices=out_indices,
                stage_names=self.stage_names,
            )
        )


__all__ = ["UnetConfig"]
