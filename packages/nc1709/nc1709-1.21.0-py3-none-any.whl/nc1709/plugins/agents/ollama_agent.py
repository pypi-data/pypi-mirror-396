"""
Ollama Agent for NC1709
Handles Ollama LLM model management operations
"""
import subprocess
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

try:
    from ..base import (
        Plugin, PluginMetadata, PluginCapability,
        ActionResult
    )
except ImportError:
    # When loaded dynamically via importlib
    from nc1709.plugins.base import (
        Plugin, PluginMetadata, PluginCapability,
        ActionResult
    )


@dataclass
class ModelInfo:
    """Represents an Ollama model"""
    name: str
    size: str
    modified: str
    digest: str = ""

    @property
    def base_name(self) -> str:
        """Get the model name without tag"""
        return self.name.split(":")[0] if ":" in self.name else self.name

    @property
    def tag(self) -> str:
        """Get the model tag"""
        return self.name.split(":")[1] if ":" in self.name else "latest"


@dataclass
class RunningModel:
    """Represents a running Ollama model"""
    name: str
    size: str
    processor: str
    until: str


class OllamaAgent(Plugin):
    """
    Ollama model management agent.

    Provides Ollama operations:
    - Model management (list, pull, remove, show)
    - Model running (run, stop)
    - Model information (show details)
    """

    METADATA = PluginMetadata(
        name="ollama",
        version="1.0.0",
        description="Ollama LLM model management",
        author="NC1709 Team",
        capabilities=[
            PluginCapability.COMMAND_EXECUTION
        ],
        keywords=[
            "ollama", "model", "llm", "llama", "mistral", "codellama",
            "pull", "download", "run", "local", "ai", "chat",
            "qwen", "phi", "gemma", "deepseek", "starcoder"
        ],
        config_schema={
            "default_model": {"type": "string", "default": "llama3.2"},
            "host": {"type": "string", "default": "http://localhost:11434"}
        }
    )

    # Popular models with descriptions
    POPULAR_MODELS = {
        "llama3.2": "Meta's latest Llama 3.2 (1B/3B parameters)",
        "llama3.1": "Meta's Llama 3.1 (8B/70B/405B parameters)",
        "codellama": "Code-specialized Llama model",
        "mistral": "Mistral 7B - fast and capable",
        "mixtral": "Mistral's MoE model (8x7B)",
        "phi3": "Microsoft's Phi-3 (3.8B parameters)",
        "gemma2": "Google's Gemma 2 model",
        "qwen2.5": "Alibaba's Qwen 2.5 model",
        "qwen2.5-coder": "Qwen 2.5 optimized for coding",
        "deepseek-coder-v2": "DeepSeek's coding model",
        "starcoder2": "BigCode's StarCoder 2",
        "nomic-embed-text": "Text embedding model",
    }

    @property
    def metadata(self) -> PluginMetadata:
        return self.METADATA

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._ollama_available = False
        self._ollama_version = ""

    def initialize(self) -> bool:
        """Initialize the Ollama agent"""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self._ollama_available = True
                # Parse version
                output = result.stdout.strip() or result.stderr.strip()
                if "version" in output.lower():
                    self._ollama_version = output
                return True
        except FileNotFoundError:
            self._error = "Ollama is not installed. Install from https://ollama.ai"
            return False
        except Exception as e:
            self._error = f"Error checking Ollama: {e}"
            return False

        return False

    def cleanup(self) -> None:
        """Cleanup resources"""
        pass

    def _register_actions(self) -> None:
        """Register Ollama actions"""
        # Model listing
        self.register_action(
            "list",
            self.list_models,
            "List installed models"
        )

        self.register_action(
            "ps",
            self.list_running,
            "List running models"
        )

        # Model management
        self.register_action(
            "pull",
            self.pull_model,
            "Download/update a model",
            parameters={"model": {"type": "string", "required": True}}
        )

        self.register_action(
            "rm",
            self.remove_model,
            "Remove a model",
            parameters={"model": {"type": "string", "required": True}},
            requires_confirmation=True,
            dangerous=True
        )

        self.register_action(
            "show",
            self.show_model,
            "Show model details",
            parameters={"model": {"type": "string", "required": True}}
        )

        self.register_action(
            "cp",
            self.copy_model,
            "Copy a model to a new name",
            parameters={
                "source": {"type": "string", "required": True},
                "destination": {"type": "string", "required": True}
            }
        )

        # Model running
        self.register_action(
            "run",
            self.run_model,
            "Run a model (start it for inference)",
            parameters={
                "model": {"type": "string", "required": True},
                "prompt": {"type": "string", "optional": True}
            }
        )

        self.register_action(
            "stop",
            self.stop_model,
            "Stop a running model",
            parameters={"model": {"type": "string", "required": True}}
        )

        # Utility
        self.register_action(
            "search",
            self.search_models,
            "Search for available models",
            parameters={"query": {"type": "string", "optional": True}}
        )

        self.register_action(
            "recommend",
            self.recommend_model,
            "Get model recommendations based on use case",
            parameters={"use_case": {"type": "string", "required": True}}
        )

    def _run_ollama(self, *args, timeout: int = 60) -> subprocess.CompletedProcess:
        """Run an ollama command"""
        cmd = ["ollama"] + list(args)
        return subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

    def list_models(self) -> ActionResult:
        """List installed Ollama models

        Returns:
            ActionResult with model list
        """
        result = self._run_ollama("list")

        if result.returncode != 0:
            return ActionResult.fail(result.stderr or "Failed to list models")

        models = []
        lines = result.stdout.strip().split("\n")

        # Skip header line
        for line in lines[1:]:
            if not line.strip():
                continue
            # Parse: NAME    ID    SIZE    MODIFIED
            parts = line.split()
            if len(parts) >= 4:
                models.append(ModelInfo(
                    name=parts[0],
                    digest=parts[1] if len(parts) > 1 else "",
                    size=parts[2] if len(parts) > 2 else "",
                    modified=" ".join(parts[3:]) if len(parts) > 3 else ""
                ))

        if not models:
            return ActionResult.ok(
                message="No models installed. Use 'ollama pull <model>' to download one.",
                data=[]
            )

        return ActionResult.ok(
            message=f"{len(models)} models installed",
            data=models
        )

    def list_running(self) -> ActionResult:
        """List currently running models

        Returns:
            ActionResult with running model list
        """
        result = self._run_ollama("ps")

        if result.returncode != 0:
            return ActionResult.fail(result.stderr or "Failed to list running models")

        models = []
        lines = result.stdout.strip().split("\n")

        # Skip header line
        for line in lines[1:]:
            if not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 4:
                models.append(RunningModel(
                    name=parts[0],
                    size=parts[2] if len(parts) > 2 else "",
                    processor=parts[3] if len(parts) > 3 else "",
                    until=" ".join(parts[4:]) if len(parts) > 4 else ""
                ))

        if not models:
            return ActionResult.ok(
                message="No models currently running",
                data=[]
            )

        return ActionResult.ok(
            message=f"{len(models)} models running",
            data=models
        )

    def pull_model(self, model: str) -> ActionResult:
        """Download or update a model

        Args:
            model: Model name (e.g., "llama3.2", "codellama:7b")

        Returns:
            ActionResult with download status
        """
        # Extended timeout for large model downloads (30 minutes)
        result = self._run_ollama("pull", model, timeout=1800)

        if result.returncode != 0:
            error_msg = result.stderr or "Failed to pull model"
            if "not found" in error_msg.lower():
                return ActionResult.fail(
                    f"Model '{model}' not found. Check https://ollama.ai/library for available models."
                )
            return ActionResult.fail(error_msg)

        return ActionResult.ok(
            message=f"Successfully pulled model: {model}",
            data=result.stdout
        )

    def remove_model(self, model: str) -> ActionResult:
        """Remove a model

        Args:
            model: Model name to remove

        Returns:
            ActionResult with removal status
        """
        result = self._run_ollama("rm", model)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr or f"Failed to remove model: {model}")

        return ActionResult.ok(f"Removed model: {model}")

    def show_model(self, model: str) -> ActionResult:
        """Show model details

        Args:
            model: Model name

        Returns:
            ActionResult with model details
        """
        result = self._run_ollama("show", model)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr or f"Model '{model}' not found")

        return ActionResult.ok(
            message=f"Details for {model}",
            data=result.stdout
        )

    def copy_model(self, source: str, destination: str) -> ActionResult:
        """Copy a model to a new name

        Args:
            source: Source model name
            destination: New model name

        Returns:
            ActionResult with copy status
        """
        result = self._run_ollama("cp", source, destination)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr or "Failed to copy model")

        return ActionResult.ok(f"Copied {source} to {destination}")

    def run_model(self, model: str, prompt: Optional[str] = None) -> ActionResult:
        """Start a model for inference

        Args:
            model: Model name
            prompt: Optional prompt to send

        Returns:
            ActionResult with run status
        """
        if prompt:
            # Run with prompt
            result = self._run_ollama("run", model, prompt, timeout=300)
        else:
            # Just load the model
            result = self._run_ollama("run", model, "--", timeout=60)

        if result.returncode != 0:
            error_msg = result.stderr or "Failed to run model"
            if "not found" in error_msg.lower():
                return ActionResult.fail(
                    f"Model '{model}' not found locally. Pull it first with: ollama pull {model}"
                )
            return ActionResult.fail(error_msg)

        return ActionResult.ok(
            message=f"Model {model} response",
            data=result.stdout
        )

    def stop_model(self, model: str) -> ActionResult:
        """Stop a running model

        Args:
            model: Model name to stop

        Returns:
            ActionResult with stop status
        """
        result = self._run_ollama("stop", model)

        if result.returncode != 0:
            return ActionResult.fail(result.stderr or f"Failed to stop model: {model}")

        return ActionResult.ok(f"Stopped model: {model}")

    def search_models(self, query: Optional[str] = None) -> ActionResult:
        """Search for available models

        Args:
            query: Optional search query

        Returns:
            ActionResult with matching models
        """
        # Return popular models (since ollama doesn't have a search API)
        if query:
            query_lower = query.lower()
            matches = {
                name: desc for name, desc in self.POPULAR_MODELS.items()
                if query_lower in name.lower() or query_lower in desc.lower()
            }
        else:
            matches = self.POPULAR_MODELS

        if not matches:
            return ActionResult.ok(
                message=f"No models found matching '{query}'. Visit https://ollama.ai/library for full list.",
                data=[]
            )

        return ActionResult.ok(
            message=f"Found {len(matches)} popular models" + (f" matching '{query}'" if query else ""),
            data=matches
        )

    def recommend_model(self, use_case: str) -> ActionResult:
        """Recommend models based on use case

        Args:
            use_case: Description of intended use (e.g., "coding", "chat", "embeddings")

        Returns:
            ActionResult with recommendations
        """
        use_case_lower = use_case.lower()

        recommendations = {}

        if any(kw in use_case_lower for kw in ["code", "programming", "developer", "coding"]):
            recommendations = {
                "qwen2.5-coder": "Best for coding tasks, code completion, and review",
                "codellama": "Meta's code-specialized model",
                "deepseek-coder-v2": "Excellent for code generation",
                "starcoder2": "Trained on code repositories",
            }
        elif any(kw in use_case_lower for kw in ["chat", "conversation", "assistant", "general"]):
            recommendations = {
                "llama3.2": "Fast, compact, great for general chat",
                "llama3.1": "More capable, slower",
                "mistral": "Fast and capable for conversations",
                "qwen2.5": "Strong multilingual support",
            }
        elif any(kw in use_case_lower for kw in ["embed", "search", "rag", "vector"]):
            recommendations = {
                "nomic-embed-text": "Best for text embeddings and RAG",
            }
        elif any(kw in use_case_lower for kw in ["small", "fast", "light", "edge"]):
            recommendations = {
                "llama3.2:1b": "1B parameters, very fast",
                "phi3:mini": "Small but capable",
                "gemma2:2b": "Google's small model",
            }
        elif any(kw in use_case_lower for kw in ["large", "powerful", "best"]):
            recommendations = {
                "llama3.1:70b": "70B parameters, very capable",
                "mixtral": "8x7B MoE, excellent quality",
                "qwen2.5:72b": "72B parameters, multilingual",
            }
        else:
            recommendations = {
                "llama3.2": "Good all-around default choice",
                "mistral": "Fast and capable",
                "qwen2.5-coder": "If you need coding help",
            }

        return ActionResult.ok(
            message=f"Recommendations for: {use_case}",
            data=recommendations
        )

    def can_handle(self, request: str) -> float:
        """Check if request is Ollama-related"""
        request_lower = request.lower()

        # High confidence keywords
        high_conf = ["ollama", "pull model", "download model", "local llm", "install model"]
        for kw in high_conf:
            if kw in request_lower:
                return 0.95

        # Model names
        model_names = ["llama", "mistral", "codellama", "mixtral", "phi", "gemma", "qwen", "deepseek", "starcoder"]
        for model in model_names:
            if model in request_lower:
                # Check if it's about running/pulling/installing
                if any(verb in request_lower for verb in ["pull", "download", "install", "run", "use", "get"]):
                    return 0.85

        # Medium confidence
        med_conf = ["local model", "llm model", "ai model"]
        for kw in med_conf:
            if kw in request_lower:
                return 0.6

        return super().can_handle(request)

    def handle_request(self, request: str, **kwargs) -> Optional[ActionResult]:
        """Handle a natural language request"""
        request_lower = request.lower()

        # List models
        if any(kw in request_lower for kw in ["list models", "show models", "installed models", "what models"]):
            return self.list_models()

        # Running models
        if any(kw in request_lower for kw in ["running models", "active models", "loaded models"]):
            return self.list_running()

        # Pull/download model
        if any(kw in request_lower for kw in ["pull", "download", "install", "get"]):
            # Extract model name
            for model in self.POPULAR_MODELS:
                if model in request_lower:
                    return self.pull_model(model)
            # Check for specific model names like "llama3.2:1b"
            model_match = re.search(r'(llama\S*|mistral\S*|codellama\S*|qwen\S*|phi\S*|gemma\S*)', request_lower)
            if model_match:
                return self.pull_model(model_match.group(1))

        # Recommend
        if any(kw in request_lower for kw in ["recommend", "suggest", "best model", "which model"]):
            # Extract use case
            use_case = request_lower
            for remove_kw in ["recommend", "suggest", "best model", "which model", "for", "me", "a"]:
                use_case = use_case.replace(remove_kw, "")
            return self.recommend_model(use_case.strip() or "general")

        # Search
        if "search" in request_lower or "find model" in request_lower:
            query = request_lower.replace("search", "").replace("find model", "").strip()
            return self.search_models(query or None)

        return None
