from transformers import (
    AutoConfig,
    AutoModel,
    AutoModelForImageSegmentation,
)

from magdi_segmentation_models_3d.swinunetrv2.configuration_swinunetr2 import (
    SwinUNETRv2Config,
)
from magdi_segmentation_models_3d.swinunetrv2.modeling_swinunetrv2 import (
    SwinUNETRv2Model,
    SwinUNETRv2ForImageSegmentation,
    SwinUNETRv2Backbone,
)

# AutoClass
AutoConfig.register("swinunetrv2", SwinUNETRv2Config)
AutoModel.register(SwinUNETRv2Config, SwinUNETRv2Model)
AutoModelForImageSegmentation.register(
    SwinUNETRv2Config, SwinUNETRv2ForImageSegmentation
)
AutoModelForImageSegmentation.register(SwinUNETRv2Config, SwinUNETRv2Backbone)

# Upload
SwinUNETRv2Config.register_for_auto_class()
SwinUNETRv2Model.register_for_auto_class("AutoModel")
SwinUNETRv2Backbone.register_for_auto_class("AutoModelForPreTraining")
SwinUNETRv2ForImageSegmentation.register_for_auto_class("AutoModelForImageSegmentation")


seg_labels = 5
swin_unetr_v2_config = SwinUNETRv2Config(
    in_channels=1,
    out_channels=seg_labels,
    depths=(2, 2, 2, 2),
    num_heads=(3, 6, 12, 24),
    feature_size=48,
)
swin_unetr_v2_backbone = SwinUNETRv2Backbone(swin_unetr_v2_config)
swin_unetr_v2_backbone.push_to_hub("anhaltai/swinunetrv2_backbone")  # type: ignore

swin_unetr_v2 = SwinUNETRv2ForImageSegmentation(swin_unetr_v2_config)
swin_unetr_v2.push_to_hub("anhaltai/swinunetrv2")  # type: ignore
