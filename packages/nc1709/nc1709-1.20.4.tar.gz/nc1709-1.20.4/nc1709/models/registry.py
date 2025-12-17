"""
Model Registry for NC1709

Centralized model specifications. Adding a new model is as simple as
adding an entry to KNOWN_MODELS or letting the system auto-detect it.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class PromptFormat(Enum):
    """Supported prompt formats"""
    CHATML = "chatml"           # <|im_start|>user\n...<|im_end|>
    LLAMA = "llama"             # [INST] ... [/INST]
    ALPACA = "alpaca"           # ### Instruction:\n...\n### Response:
    RAW = "raw"                 # No special formatting
    DEEPSEEK = "deepseek"       # DeepSeek specific format
    MISTRAL = "mistral"         # Mistral format
    COMMAND_R = "command_r"     # Cohere Command-R format


class ModelCapability(Enum):
    """Model capabilities"""
    CODE_GENERATION = "code_generation"
    CODE_COMPLETION = "code_completion"
    REASONING = "reasoning"
    TOOL_USE = "tool_use"
    FUNCTION_CALLING = "function_calling"
    VISION = "vision"
    LONG_CONTEXT = "long_context"
    FAST_INFERENCE = "fast_inference"
    MATH = "math"
    CREATIVE_WRITING = "creative_writing"
    EMBEDDING = "embedding"


@dataclass
class ModelSpec:
    """
    Complete specification for a model.

    This contains everything NC1709 needs to know to use a model effectively.
    """
    # Basic info
    name: str                                    # Human-readable name
    ollama_name: str                             # Name in Ollama (e.g., "qwen2.5-coder:32b")

    # Context limits
    context_window: int = 32768                  # Max input tokens
    max_output_tokens: int = 4096                # Max output tokens

    # Prompt formatting
    prompt_format: PromptFormat = PromptFormat.CHATML
    system_prompt_supported: bool = True         # Does it support system prompts?

    # Capabilities
    capabilities: List[ModelCapability] = field(default_factory=list)

    # Performance characteristics
    tokens_per_second: Optional[float] = None    # Approximate speed
    memory_gb: Optional[float] = None            # VRAM required

    # Recommended settings
    default_temperature: float = 0.7
    recommended_temperature_code: float = 0.3    # Lower for code
    recommended_temperature_creative: float = 0.9

    # Special features
    supports_streaming: bool = True
    supports_json_mode: bool = False             # Structured output
    supports_vision: bool = False                # Image input

    # Task suitability scores (0-1, higher is better)
    suitability: Dict[str, float] = field(default_factory=dict)

    # Any special notes or quirks
    notes: Optional[str] = None


# ============================================================================
# KNOWN MODELS REGISTRY
# ============================================================================
# Add new models here. This is the ONLY place you need to update when
# adding a new model to the system.

KNOWN_MODELS: Dict[str, ModelSpec] = {

    # -------------------------------------------------------------------------
    # Qwen Models
    # -------------------------------------------------------------------------

    "qwen2.5-coder:32b": ModelSpec(
        name="Qwen 2.5 Coder 32B",
        ollama_name="qwen2.5-coder:32b",
        context_window=32768,
        max_output_tokens=8192,
        prompt_format=PromptFormat.CHATML,
        capabilities=[
            ModelCapability.CODE_GENERATION,
            ModelCapability.CODE_COMPLETION,
            ModelCapability.REASONING,
        ],
        memory_gb=20.0,
        tokens_per_second=30.0,
        default_temperature=0.7,
        recommended_temperature_code=0.3,
        suitability={
            "coding": 0.95,
            "reasoning": 0.80,
            "general": 0.75,
            "fast": 0.40,
            "instant": 0.20,
        },
        notes="Excellent for code generation and debugging."
    ),

    "qwen2.5-coder:7b": ModelSpec(
        name="Qwen 2.5 Coder 7B",
        ollama_name="qwen2.5-coder:7b",
        context_window=32768,
        max_output_tokens=8192,
        prompt_format=PromptFormat.CHATML,
        capabilities=[
            ModelCapability.CODE_GENERATION,
            ModelCapability.CODE_COMPLETION,
            ModelCapability.FAST_INFERENCE,
        ],
        memory_gb=5.0,
        tokens_per_second=80.0,
        suitability={
            "coding": 0.75,
            "reasoning": 0.60,
            "general": 0.65,
            "fast": 0.95,      # Best available for fast tasks
            "instant": 0.95,   # Best available for instant tasks
        },
        notes="Fast model for quick tasks and drafting. Best for instant/fast tier."
    ),

    "qwen2.5:32b": ModelSpec(
        name="Qwen 2.5 32B",
        ollama_name="qwen2.5:32b",
        context_window=32768,
        max_output_tokens=8192,
        prompt_format=PromptFormat.CHATML,
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.TOOL_USE,
            ModelCapability.CREATIVE_WRITING,
        ],
        memory_gb=20.0,
        tokens_per_second=30.0,
        suitability={
            "coding": 0.70,
            "reasoning": 0.85,
            "general": 0.90,
            "tools": 0.85,
            "fast": 0.40,
        },
        notes="Good general-purpose model."
    ),

    # Note: qwen2.5:7b entry removed - use qwen2.5-coder:7b instead

    # Note: qwen2.5:3b removed - not typically installed
    # If you have it, you can add it back with high "fast" and "instant" scores

    # -------------------------------------------------------------------------
    # DeepSeek Models
    # -------------------------------------------------------------------------

    "deepseek-r1:latest": ModelSpec(
        name="DeepSeek R1",
        ollama_name="deepseek-r1:latest",
        context_window=65536,
        max_output_tokens=8192,
        prompt_format=PromptFormat.DEEPSEEK,
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.MATH,
            ModelCapability.LONG_CONTEXT,
        ],
        memory_gb=18.0,
        tokens_per_second=25.0,
        suitability={
            "coding": 0.75,
            "reasoning": 0.95,
            "general": 0.80,
            "math": 0.95,
            "council": 0.90,
        },
        notes="Excellent for complex reasoning and math."
    ),

    "deepseek-coder-v2:latest": ModelSpec(
        name="DeepSeek Coder V2",
        ollama_name="deepseek-coder-v2:latest",
        context_window=128000,
        max_output_tokens=8192,
        prompt_format=PromptFormat.DEEPSEEK,
        capabilities=[
            ModelCapability.CODE_GENERATION,
            ModelCapability.CODE_COMPLETION,
            ModelCapability.LONG_CONTEXT,
        ],
        memory_gb=22.0,
        tokens_per_second=28.0,
        suitability={
            "coding": 0.92,
            "reasoning": 0.85,
            "general": 0.75,
        },
        notes="128K context, great for large codebases."
    ),

    # -------------------------------------------------------------------------
    # Llama Models
    # -------------------------------------------------------------------------

    "llama3.2:latest": ModelSpec(
        name="Llama 3.2",
        ollama_name="llama3.2:latest",
        context_window=128000,
        max_output_tokens=4096,
        prompt_format=PromptFormat.LLAMA,
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.LONG_CONTEXT,
        ],
        memory_gb=8.0,
        tokens_per_second=50.0,
        suitability={
            "coding": 0.70,
            "reasoning": 0.80,
            "general": 0.85,
        },
    ),

    "codellama:34b": ModelSpec(
        name="Code Llama 34B",
        ollama_name="codellama:34b",
        context_window=16384,
        max_output_tokens=4096,
        prompt_format=PromptFormat.LLAMA,
        capabilities=[
            ModelCapability.CODE_GENERATION,
            ModelCapability.CODE_COMPLETION,
        ],
        memory_gb=20.0,
        tokens_per_second=25.0,
        suitability={
            "coding": 0.88,
            "reasoning": 0.70,
            "general": 0.65,
        },
    ),

    # -------------------------------------------------------------------------
    # Mistral Models
    # -------------------------------------------------------------------------

    "mistral:latest": ModelSpec(
        name="Mistral 7B",
        ollama_name="mistral:latest",
        context_window=32768,
        max_output_tokens=4096,
        prompt_format=PromptFormat.MISTRAL,
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.FAST_INFERENCE,
        ],
        memory_gb=5.0,
        tokens_per_second=70.0,
        suitability={
            "coding": 0.70,
            "reasoning": 0.75,
            "general": 0.80,
            "fast": 0.85,
        },
    ),

    "mixtral:8x7b": ModelSpec(
        name="Mixtral 8x7B",
        ollama_name="mixtral:8x7b",
        context_window=32768,
        max_output_tokens=4096,
        prompt_format=PromptFormat.MISTRAL,
        capabilities=[
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
        ],
        memory_gb=26.0,
        tokens_per_second=40.0,
        suitability={
            "coding": 0.80,
            "reasoning": 0.85,
            "general": 0.85,
        },
    ),

    # -------------------------------------------------------------------------
    # Embedding Models
    # -------------------------------------------------------------------------

    "nomic-embed-text": ModelSpec(
        name="Nomic Embed Text",
        ollama_name="nomic-embed-text",
        context_window=8192,
        max_output_tokens=0,  # Embedding model
        prompt_format=PromptFormat.RAW,
        capabilities=[ModelCapability.EMBEDDING],
        memory_gb=0.5,
        tokens_per_second=500.0,
        suitability={
            "embedding": 1.0,
        },
        notes="Embedding model for semantic search."
    ),

    "mxbai-embed-large": ModelSpec(
        name="MxBai Embed Large",
        ollama_name="mxbai-embed-large",
        context_window=512,
        max_output_tokens=0,
        prompt_format=PromptFormat.RAW,
        capabilities=[ModelCapability.EMBEDDING],
        memory_gb=0.7,
        tokens_per_second=400.0,
        suitability={
            "embedding": 0.95,
        },
        notes="High-quality embedding model."
    ),
}


# ============================================================================
# REGISTRY FUNCTIONS
# ============================================================================

def get_model_spec(model_name: str) -> Optional[ModelSpec]:
    """
    Get specification for a model.

    Args:
        model_name: Ollama model name (e.g., "qwen2.5-coder:32b")

    Returns:
        ModelSpec if found, None otherwise
    """
    # Direct lookup
    if model_name in KNOWN_MODELS:
        return KNOWN_MODELS[model_name]

    # Try without tag
    base_name = model_name.split(":")[0]
    for known_name, spec in KNOWN_MODELS.items():
        if known_name.startswith(base_name):
            return spec

    return None


def get_all_models() -> Dict[str, ModelSpec]:
    """Get all known models"""
    return KNOWN_MODELS.copy()


def get_models_with_capability(capability: ModelCapability) -> List[ModelSpec]:
    """Get all models with a specific capability"""
    return [
        spec for spec in KNOWN_MODELS.values()
        if capability in spec.capabilities
    ]


def get_best_model_for_task(task: str) -> Optional[ModelSpec]:
    """
    Get the best model for a specific task based on suitability scores.

    Args:
        task: Task name (e.g., "coding", "reasoning", "fast")

    Returns:
        Best ModelSpec for the task
    """
    best_model = None
    best_score = 0.0

    for spec in KNOWN_MODELS.values():
        score = spec.suitability.get(task, 0.0)
        if score > best_score:
            best_score = score
            best_model = spec

    return best_model


def register_model(spec: ModelSpec) -> None:
    """
    Register a new model at runtime.

    Args:
        spec: Model specification to register
    """
    KNOWN_MODELS[spec.ollama_name] = spec


def unregister_model(model_name: str) -> bool:
    """
    Unregister a model.

    Args:
        model_name: Model name to remove

    Returns:
        True if removed, False if not found
    """
    if model_name in KNOWN_MODELS:
        del KNOWN_MODELS[model_name]
        return True
    return False


def create_model_spec(
    ollama_name: str,
    name: Optional[str] = None,
    context_window: int = 32768,
    prompt_format: PromptFormat = PromptFormat.CHATML,
    capabilities: Optional[List[ModelCapability]] = None,
    suitability: Optional[Dict[str, float]] = None,
    **kwargs
) -> ModelSpec:
    """
    Helper to create a ModelSpec with sensible defaults.

    Args:
        ollama_name: Name in Ollama
        name: Human-readable name (defaults to ollama_name)
        context_window: Context window size
        prompt_format: Prompt format to use
        capabilities: List of capabilities
        suitability: Suitability scores
        **kwargs: Additional ModelSpec fields

    Returns:
        New ModelSpec
    """
    return ModelSpec(
        name=name or ollama_name,
        ollama_name=ollama_name,
        context_window=context_window,
        prompt_format=prompt_format,
        capabilities=capabilities or [],
        suitability=suitability or {"general": 0.5},
        **kwargs
    )
