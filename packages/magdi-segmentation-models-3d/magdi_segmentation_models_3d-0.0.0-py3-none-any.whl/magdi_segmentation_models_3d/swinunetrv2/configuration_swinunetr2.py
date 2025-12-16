from transformers import PretrainedConfig
from transformers.utils import logging

from transformers.utils.backbone_utils import (
    BackboneConfigMixin,
    get_aligned_output_features_output_indices,
)
from collections.abc import Sequence
import torch.nn as nn

logger = logging.get_logger(__name__)


class SwinUNETRv2Config(BackboneConfigMixin, PretrainedConfig):

    model_type = "swinunetrv2"

    def __init__(
        self,
        in_channels: int = 1,
        out_channels: int = 1,
        patch_size: int = 2,
        depths: Sequence[int] = (2, 2, 2, 2),
        num_heads: Sequence[int] = (3, 6, 12, 24),
        window_size: Sequence[int] | int = 7,
        qkv_bias: bool = True,
        mlp_ratio: float = 4.0,
        feature_size: int = 24,
        norm_name: tuple | str = "instance",
        drop_rate: float = 0.0,
        attn_drop_rate: float = 0.0,
        dropout_path_rate: float = 0.0,
        normalize: bool = True,
        patch_norm: bool = False,
        use_checkpoint: bool = False,
        spatial_dims: int = 3,
        downsample: str | nn.Module = "merging",
        out_features=None,
        out_indices=None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        self.in_channels = in_channels
        self.out_channels = out_channels
        self.patch_size = patch_size
        self.depths = depths
        self.num_layers = len(depths)
        self.num_heads = num_heads
        self.window_size = window_size
        self.qkv_bias = qkv_bias
        self.mlp_ratio = mlp_ratio
        self.feature_size = feature_size
        self.norm_name = norm_name
        self.drop_rate = drop_rate
        self.attn_drop_rate = attn_drop_rate
        self.dropout_path_rate = dropout_path_rate
        self.normalize = normalize
        self.patch_norm = patch_norm
        self.use_checkpoint = use_checkpoint
        self.spatial_dims = spatial_dims
        self.downsample = downsample

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


__all__ = ["SwinUNETRv2Config"]
