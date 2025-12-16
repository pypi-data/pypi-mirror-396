# Re-export all classes for backward compatibility
from tamar_model_client.schemas.inputs.base import (
    UserContext,
    TamarFileIdInput,
    BaseRequest,
)
# OpenAI
from tamar_model_client.schemas.inputs.openai.responses import OpenAIResponsesInput
from tamar_model_client.schemas.inputs.openai.chat_completions import OpenAIChatCompletionsInput
from tamar_model_client.schemas.inputs.openai.images import OpenAIImagesInput, OpenAIImagesEditInput
from tamar_model_client.schemas.inputs.openai.videos import OpenAIVideosInput
# Google
from tamar_model_client.schemas.inputs.google.genai import GoogleGenAiInput
from tamar_model_client.schemas.inputs.google.genai_images import GoogleGenAIImagesInput
from tamar_model_client.schemas.inputs.google.genai_videos import GoogleGenAiVideosInput
from tamar_model_client.schemas.inputs.google.vertexai_images import GoogleVertexAIImagesInput
# Anthropic
from tamar_model_client.schemas.inputs.anthropic.messages import AnthropicMessagesInput
# Freepik
from tamar_model_client.schemas.inputs.freepik.image_upscaler import FreepikImageUpscalerInput
# BytePlus
from tamar_model_client.schemas.inputs.byteplus.omnihuman_video import BytePlusOmniHumanVideoInput
# Fal AI
from tamar_model_client.schemas.inputs.fal_ai.qwen_images import FalAIQwenImageEditInput
from tamar_model_client.schemas.inputs.fal_ai.wan_video_replace import FalAIWanVideoReplaceInput
from tamar_model_client.schemas.inputs.fal_ai.z_images import FalAIZImageInput, LoRAInput, ImageSizeCustom
# BFL
from tamar_model_client.schemas.inputs.bfl import BFLInput, BFLFlux2Input
# Azure
from tamar_model_client.schemas.inputs.azure import AzureFluxImageInput, AzureFluxImageEditInput
# Unified
from tamar_model_client.schemas.inputs.unified import (
    ModelRequestInput,
    ModelRequest,
    BatchModelRequestItem,
    BatchModelRequest,
)

__all__ = [
    # Base
    "UserContext",
    "TamarFileIdInput",
    "BaseRequest",
    # OpenAI
    "OpenAIResponsesInput",
    "OpenAIChatCompletionsInput",
    "OpenAIImagesInput",
    "OpenAIImagesEditInput",
    "OpenAIVideosInput",
    # Google
    "GoogleGenAiInput",
    "GoogleVertexAIImagesInput",
    "GoogleGenAIImagesInput",
    "GoogleGenAiVideosInput",
    # Anthropic
    "AnthropicMessagesInput",
    # Freepik
    "FreepikImageUpscalerInput",
    # BytePlus
    "BytePlusOmniHumanVideoInput",
    # Fal AI
    "FalAIQwenImageEditInput",
    "FalAIWanVideoReplaceInput",
    "FalAIZImageInput",
    "LoRAInput",
    "ImageSizeCustom",
    # BFL
    "BFLInput",
    "BFLFlux2Input",
    # Azure
    "AzureFluxImageInput",
    "AzureFluxImageEditInput",
    # Unified
    "ModelRequestInput",
    "ModelRequest",
    "BatchModelRequestItem",
    "BatchModelRequest",
]
