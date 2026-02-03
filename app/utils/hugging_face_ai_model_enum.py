from enum import Enum

class HuggingFaceModelList(Enum):
    model_list = [
        "meta-llama/Llama-3.1-8B-Instruct",
        "deepseek-ai/DeepSeek-R1"
    ]

class HuggingFaceModelForInternalReserchEngine(Enum):
    PERPLEXITY_RESERCH_MODEL = "perplexity-ai/r1-1776"