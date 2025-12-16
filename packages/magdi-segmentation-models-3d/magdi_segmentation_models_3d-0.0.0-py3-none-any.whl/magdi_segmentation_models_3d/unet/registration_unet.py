import os.path

import torch
from transformers import (
    AutoConfig,
    AutoModel,
    AutoModelForImageSegmentation,
    AutoImageProcessor,
)

from monai.networks.layers.factories import Act, Norm
from magdi_segmentation_models_3d.unet.configuration_unet import UnetConfig
from magdi_segmentation_models_3d.unet.modeling_unet import (
    UnetModel,
    UnetForImageSegmentation,
    UnetBackbone,
)
from magdi_segmentation_models_3d.unet.image_processing_unet import (
    UnetImageProcessor,
)

# AutoClass
AutoConfig.register("unet", UnetConfig)
AutoImageProcessor.register(UnetConfig, UnetImageProcessor)
AutoModel.register(UnetConfig, UnetModel)
AutoModelForImageSegmentation.register(UnetConfig, UnetForImageSegmentation)
AutoModelForImageSegmentation.register(UnetConfig, UnetBackbone)

# Upload
UnetConfig.register_for_auto_class()
UnetImageProcessor.register_for_auto_class("AutoImageProcessor")
UnetModel.register_for_auto_class("AutoModel")
UnetBackbone.register_for_auto_class("AutoModelForPreTraining")
UnetForImageSegmentation.register_for_auto_class("AutoModelForImageSegmentation")


out_channels = 5
unet_config = UnetConfig(
    in_channels=1,
    out_channels=out_channels,
    channels=(64, 128, 256, 512, 1024),
    strides=(2, 2, 2, 2),
    num_res_units=2,
    spatial_dims=3,
    kernel_size=3,
    up_kernel_size=3,
    act=Act.PRELU,
    norm=Norm.INSTANCE,
    dropout=0.0,
    bias=True,
    adn_ordering="NDA",
)

source_path = (
    "data/Mais_v0_beta_v_2025_07_02_mini/occurrence-0000/instance-0000/image.nii.gz"
)
gt_path = os.path.join(
    "data/Mais_v0_beta_v_2025_07_02_mini",
    "occurrence-0000/instance-0000/annotations.nii.gz",
)

processor = UnetImageProcessor()
# inputs = processor.preprocess(source_path, gt_path)

processor.push_to_hub("anhaltai/unet")
processor = AutoImageProcessor.from_pretrained("anhaltai/unet")


inputs = processor(source_path, gt_path)
inputs_for_inference = processor(source_path)
inputs_for_inference["image"] = inputs_for_inference["image"].unsqueeze(0)

# unet_backbone = UnetBackbone(unet_config)
# unet_backbone.push_to_hub("anhaltai/unet_backbone")  # type: ignore

# unet = UnetForImageSegmentation(unet_config)
# unet.push_to_hub("anhaltai/unet")  # type: ignore

hf_model = AutoModelForImageSegmentation.from_pretrained(
    "anhaltai/swinunetrv2_Mais_v0_beta", trust_remote_code=True, revision="main"
)

with torch.no_grad():
    result = hf_model.forward(inputs_for_inference)
print("finished")
