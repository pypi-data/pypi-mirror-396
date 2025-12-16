"""
NC1709 Model Registry System

Centralized model management that makes adding new models a single config change.

Usage:
    from nc1709.models import ModelManager, get_model_spec, KNOWN_MODELS

    # Get a model spec
    spec = get_model_spec("qwen2.5-coder:32b")
    print(f"Context: {spec.context_window}")

    # Use the manager
    manager = ModelManager(config)
    spec = manager.get_model_for_task("coding")
    prompt = manager.format_prompt(messages, spec.ollama_name)

    # Set a model for a task
    manager.set_model_for_task("coding", "new-model:70b")
"""

# Registry
from .registry import (
    # Classes
    ModelSpec,
    PromptFormat,
    ModelCapability,
    # Data
    KNOWN_MODELS,
    # Functions
    get_model_spec,
    get_all_models,
    get_models_with_capability,
    get_best_model_for_task,
    register_model,
    unregister_model,
    create_model_spec,
)

# Formats
from .formats import (
    Message,
    PromptFormatter,
    get_format_info,
)

# Detector
from .detector import (
    ModelDetector,
    auto_detect_model,
)

# Manager
from .manager import (
    ModelManager,
    print_model_info,
    print_all_models,
    print_task_assignments,
)

__all__ = [
    # Registry
    "ModelSpec",
    "PromptFormat",
    "ModelCapability",
    "KNOWN_MODELS",
    "get_model_spec",
    "get_all_models",
    "get_models_with_capability",
    "get_best_model_for_task",
    "register_model",
    "unregister_model",
    "create_model_spec",
    # Formats
    "Message",
    "PromptFormatter",
    "get_format_info",
    # Detector
    "ModelDetector",
    "auto_detect_model",
    # Manager
    "ModelManager",
    "print_model_info",
    "print_all_models",
    "print_task_assignments",
]
