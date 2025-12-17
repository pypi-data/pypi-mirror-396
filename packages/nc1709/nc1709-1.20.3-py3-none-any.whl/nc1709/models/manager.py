"""
High-level model management for NC1709.

This is the main interface that the rest of NC1709 uses to interact
with models. It handles model selection, prompt formatting, and
configuration management.
"""

from typing import Optional, List, Dict, Any
from pathlib import Path
import json

from .registry import (
    ModelSpec, ModelCapability, PromptFormat,
    KNOWN_MODELS, get_model_spec, get_best_model_for_task,
    register_model, create_model_spec
)
from .formats import PromptFormatter, Message
from .detector import ModelDetector


class ModelManager:
    """
    High-level interface for model management.

    Provides:
    - Easy model lookup and selection
    - Automatic prompt formatting
    - Model recommendation
    - Registry management

    Example:
        manager = ModelManager(config)
        spec = manager.get_model_for_task("coding")
        prompt = manager.format_prompt(messages, spec.ollama_name)
    """

    def __init__(
        self,
        config: Optional[Any] = None,
        ollama_url: str = "http://localhost:11434"
    ):
        """
        Initialize the model manager.

        Args:
            config: Configuration object with model settings
            ollama_url: Ollama API URL
        """
        self.config = config
        self.detector = ModelDetector(ollama_url)
        self.formatter = PromptFormatter()
        self._initialized = False
        self._model_assignments: Dict[str, str] = {}

        # Load saved model assignments
        self._load_assignments()

    async def initialize(self) -> None:
        """Initialize the model manager (async)"""
        if self._initialized:
            return

        # Sync with Ollama to detect new models
        try:
            await self.detector.sync_with_ollama()
        except Exception:
            pass  # Ollama might not be running

        self._initialized = True

    def initialize_sync(self) -> None:
        """Initialize the model manager (sync)"""
        if self._initialized:
            return

        try:
            self.detector.sync_with_ollama_sync()
        except Exception:
            pass

        self._initialized = True

    def get_model_for_task(self, task: str) -> ModelSpec:
        """
        Get the configured model for a task.

        Args:
            task: Task name (e.g., "coding", "reasoning", "fast", "instant")

        Returns:
            ModelSpec for the configured model
        """
        # Check saved assignments first
        if task in self._model_assignments:
            model_name = self._model_assignments[task]
            spec = get_model_spec(model_name)
            if spec:
                return spec

        # Check config
        if self.config:
            model_name = None
            if hasattr(self.config, 'get'):
                model_name = self.config.get(f"models.{task}")
            elif isinstance(self.config, dict):
                model_name = self.config.get("models", {}).get(task)

            if model_name:
                spec = get_model_spec(model_name)
                if spec:
                    return spec
                # Unknown model - create a basic spec
                spec = create_model_spec(model_name)
                register_model(spec)
                return spec

        # Fallback: get best model for task from registry
        best = get_best_model_for_task(task)
        if best:
            return best

        # Ultimate fallback
        return get_model_spec("qwen2.5:32b") or list(KNOWN_MODELS.values())[0]

    def set_model_for_task(self, task: str, model_name: str) -> bool:
        """
        Set the model for a task.

        Args:
            task: Task name
            model_name: Model to use

        Returns:
            True if successful
        """
        # Verify model exists or can be detected
        spec = get_model_spec(model_name)
        if not spec:
            # Try to auto-detect
            try:
                spec = self.detector.detect_model_spec_sync(model_name)
            except Exception:
                # Create minimal spec
                spec = create_model_spec(model_name)
                register_model(spec)

        self._model_assignments[task] = model_name
        self._save_assignments()
        return True

    def format_prompt(
        self,
        messages: List[Dict[str, str]],
        model_name: str,
        add_generation_prompt: bool = True
    ) -> str:
        """
        Format messages for a specific model.

        Args:
            messages: List of {"role": "...", "content": "..."} dicts
            model_name: Model to format for
            add_generation_prompt: Whether to add assistant prompt at end

        Returns:
            Formatted prompt string
        """
        spec = get_model_spec(model_name)
        prompt_format = spec.prompt_format if spec else PromptFormat.CHATML

        return self.formatter.format_from_dicts(
            messages, prompt_format, add_generation_prompt
        )

    def get_recommended_settings(
        self,
        model_name: str,
        task: str = "general"
    ) -> Dict[str, Any]:
        """
        Get recommended settings for a model and task.

        Args:
            model_name: Model name
            task: Task type

        Returns:
            Dict with temperature, max_tokens, etc.
        """
        spec = get_model_spec(model_name)

        if not spec:
            return {
                "temperature": 0.7,
                "max_tokens": 4096,
                "context_window": 32768,
            }

        # Determine temperature based on task
        if task in ["coding", "code_generation", "code"]:
            temperature = spec.recommended_temperature_code
        elif task in ["creative", "writing"]:
            temperature = spec.recommended_temperature_creative
        else:
            temperature = spec.default_temperature

        return {
            "temperature": temperature,
            "max_tokens": spec.max_output_tokens,
            "context_window": spec.context_window,
        }

    def recommend_model(
        self,
        task: str,
        prefer_fast: bool = False,
        min_context: int = 0
    ) -> Optional[ModelSpec]:
        """
        Recommend the best model for a task.

        Args:
            task: Task type
            prefer_fast: Prioritize speed over quality
            min_context: Minimum context window required

        Returns:
            Recommended ModelSpec
        """
        candidates = []

        for spec in KNOWN_MODELS.values():
            # Filter by context requirement
            if spec.context_window < min_context:
                continue

            # Skip embedding models for non-embedding tasks
            if task != "embedding" and ModelCapability.EMBEDDING in spec.capabilities:
                continue

            # Get suitability score
            score = spec.suitability.get(task, 0.5)

            # Adjust for speed preference
            if prefer_fast and ModelCapability.FAST_INFERENCE in spec.capabilities:
                score *= 1.3

            candidates.append((spec, score))

        if not candidates:
            return None

        # Return highest scoring
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]

    def list_available_models(self) -> List[Dict[str, Any]]:
        """List all available models with their info"""
        return [
            {
                "name": spec.name,
                "ollama_name": spec.ollama_name,
                "context_window": spec.context_window,
                "capabilities": [c.value for c in spec.capabilities],
                "suitability": spec.suitability,
                "notes": spec.notes,
            }
            for spec in KNOWN_MODELS.values()
        ]

    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed info about a model"""
        spec = get_model_spec(model_name)
        if not spec:
            return None

        return {
            "name": spec.name,
            "ollama_name": spec.ollama_name,
            "context_window": spec.context_window,
            "max_output_tokens": spec.max_output_tokens,
            "prompt_format": spec.prompt_format.value,
            "capabilities": [c.value for c in spec.capabilities],
            "suitability": spec.suitability,
            "memory_gb": spec.memory_gb,
            "tokens_per_second": spec.tokens_per_second,
            "notes": spec.notes,
        }

    def add_custom_model(
        self,
        ollama_name: str,
        name: Optional[str] = None,
        context_window: int = 32768,
        prompt_format: str = "chatml",
        capabilities: Optional[List[str]] = None,
        suitability: Optional[Dict[str, float]] = None
    ) -> ModelSpec:
        """
        Add a custom model to the registry.

        Args:
            ollama_name: Name in Ollama
            name: Human-readable name
            context_window: Context window size
            prompt_format: Prompt format name
            capabilities: List of capability strings
            suitability: Suitability scores by task

        Returns:
            Created ModelSpec
        """
        # Parse prompt format
        try:
            fmt = PromptFormat(prompt_format)
        except ValueError:
            fmt = PromptFormat.CHATML

        # Parse capabilities
        caps = []
        if capabilities:
            for cap in capabilities:
                try:
                    caps.append(ModelCapability(cap))
                except ValueError:
                    pass

        spec = ModelSpec(
            name=name or ollama_name,
            ollama_name=ollama_name,
            context_window=context_window,
            prompt_format=fmt,
            capabilities=caps,
            suitability=suitability or {"general": 0.7},
        )

        register_model(spec)
        return spec

    def get_task_assignments(self) -> Dict[str, str]:
        """Get current task-to-model assignments"""
        return self._model_assignments.copy()

    def _load_assignments(self) -> None:
        """Load model assignments from disk"""
        try:
            path = Path.home() / ".nc1709" / "model_assignments.json"
            if path.exists():
                with open(path) as f:
                    self._model_assignments = json.load(f)
        except Exception:
            self._model_assignments = {}

    def _save_assignments(self) -> None:
        """Save model assignments to disk"""
        try:
            path = Path.home() / ".nc1709" / "model_assignments.json"
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                json.dump(self._model_assignments, f, indent=2)
        except Exception:
            pass


# ============================================================================
# CLI HELPER FUNCTIONS
# ============================================================================

def print_model_info(model_name: str) -> None:
    """Print detailed info about a model"""
    spec = get_model_spec(model_name)

    if not spec:
        print(f"Model not found: {model_name}")
        return

    print(f"\n{spec.name}")
    print(f"   Ollama: {spec.ollama_name}")
    print(f"   Context: {spec.context_window:,} tokens")
    print(f"   Max Output: {spec.max_output_tokens:,} tokens")
    print(f"   Format: {spec.prompt_format.value}")

    if spec.capabilities:
        caps = ", ".join(c.value for c in spec.capabilities)
        print(f"   Capabilities: {caps}")

    if spec.suitability:
        print(f"   Suitability:")
        for task, score in sorted(spec.suitability.items(), key=lambda x: -x[1]):
            bar = "#" * int(score * 10) + "-" * (10 - int(score * 10))
            print(f"      {task}: [{bar}] {score:.0%}")

    if spec.memory_gb:
        print(f"   Memory: {spec.memory_gb:.1f} GB")

    if spec.tokens_per_second:
        print(f"   Speed: ~{spec.tokens_per_second:.0f} tokens/sec")

    if spec.notes:
        print(f"   Notes: {spec.notes}")


def print_all_models() -> None:
    """Print summary of all registered models"""
    print("\nRegistered Models:")
    print("-" * 60)

    for name, spec in sorted(KNOWN_MODELS.items()):
        # Best task
        if spec.suitability:
            best_task = max(spec.suitability.items(), key=lambda x: x[1])
            best_str = f"Best for: {best_task[0]}"
        else:
            best_str = ""

        ctx_k = spec.context_window // 1000
        print(f"  {spec.name}")
        print(f"    -> {spec.ollama_name} | {ctx_k}K context | {best_str}")

    print("-" * 60)
    print(f"Total: {len(KNOWN_MODELS)} models")


def print_task_assignments(manager: ModelManager) -> None:
    """Print current task assignments"""
    assignments = manager.get_task_assignments()

    print("\nTask Assignments:")
    print("-" * 40)

    if not assignments:
        print("  (No custom assignments - using defaults)")
    else:
        for task, model in sorted(assignments.items()):
            print(f"  {task}: {model}")

    print("-" * 40)
