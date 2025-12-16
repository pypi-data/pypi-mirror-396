"""Model configurations for clserve."""

import yaml
from typing import Optional
from dataclasses import dataclass

try:
    from importlib.resources import files
except ImportError:
    from importlib_resources import files


@dataclass
class ModelConfig:
    """Configuration for serving a specific model."""

    model_path: str
    tp_size: int = 1
    dp_size: int = 1
    ep_size: int = 1
    nodes_per_worker: int = 1
    workers: int = 1
    num_gpus_per_worker: int = 4
    cuda_graph_max_bs: int = 256
    grammar_backend: str = "llguidance"
    reasoning_parser: str = ""
    use_router: bool = False
    router_policy: str = "cache_aware"
    description: str = ""


# Model aliases for convenience
MODEL_ALIASES = {
    # Qwen models
    "qwen3-235b": "Qwen/Qwen3-235B-A22B-Instruct-2507",
    "qwen3-coder-480b": "Qwen/Qwen3-Coder-480B-A35B-Instruct",
    "qwen3-32b": "Qwen/Qwen3-32B",
    "qwen3-8b": "Qwen/Qwen3-8B",
    "qwen3-embedding-4b": "Qwen/Qwen3-Embedding-4B",
    # DeepSeek models
    "deepseek-v3": "deepseek-ai/DeepSeek-V3.1",
    "deepseek-v3.2": "deepseek-ai/DeepSeek-V3.2",
    "deepseek-r1": "deepseek-ai/DeepSeek-R1",
    # OpenAI models
    "gpt-oss-120b": "openai/gpt-oss-120b",
    # MiniMax models
    "minimax-m2": "MiniMaxAI/MiniMax-M2",
    # Moonshot models
    "kimi-k2": "moonshotai/Kimi-K2-Instruct-0905",
    # Llama models
    "llama-405b": "meta-llama/Llama-3.1-405B-Instruct",
    "llama-70b": "meta-llama/Llama-3.1-70B-Instruct",
    "llama-8b": "meta-llama/Llama-3.1-8B-Instruct",
    # Swiss AI models
    "apertus-8b": "swiss-ai/Apertus-8B-Instruct-2509",
}


def get_model_path(model_name: str) -> str:
    """Resolve model alias to full path, or return as-is if not an alias."""
    return MODEL_ALIASES.get(model_name.lower(), model_name)


def load_model_config(model_name: str) -> Optional[ModelConfig]:
    """Load predefined configuration for a model.

    Args:
        model_name: Model name, alias, or full HuggingFace path

    Returns:
        ModelConfig if found, None otherwise
    """
    # Normalize the model name for config lookup
    lookup_name = model_name.lower().replace("/", "_").replace("-", "_")

    # Also try the alias name if it exists
    for alias, path in MODEL_ALIASES.items():
        if model_name == path or model_name.lower() == alias:
            lookup_name = alias.replace("-", "_")
            break

    try:
        config_content = (
            files("clserve") / "configs" / "models" / f"{lookup_name}.yaml"
        ).read_text()
        config_dict = yaml.safe_load(config_content)
        return ModelConfig(**config_dict)
    except (FileNotFoundError, TypeError):
        return None


def list_available_configs() -> list[str]:
    """List all available predefined model configurations."""
    try:
        models_dir = files("clserve") / "configs" / "models"
        return [
            f.name.replace(".yaml", "")
            for f in models_dir.iterdir()
            if f.name.endswith(".yaml")
        ]
    except (FileNotFoundError, TypeError):
        return []
