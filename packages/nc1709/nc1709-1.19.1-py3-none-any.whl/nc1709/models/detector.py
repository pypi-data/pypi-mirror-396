"""
Auto-detect model capabilities from Ollama.

When you download a new model that's not in the registry,
this module can detect its basic capabilities and create a spec.
"""

import asyncio
import re
from typing import Optional, List, Dict, Any

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

from .registry import (
    ModelSpec, ModelCapability, PromptFormat,
    KNOWN_MODELS, register_model
)


class ModelDetector:
    """
    Auto-detects model capabilities from Ollama.

    When you download a new model that's not in the registry,
    this class can detect its basic capabilities.

    Example:
        detector = ModelDetector()
        models = await detector.list_installed_models()
        spec = await detector.detect_model_spec("new-model:latest")
    """

    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url.rstrip("/")

    async def list_installed_models(self) -> List[str]:
        """
        Get list of models installed in Ollama.

        Returns:
            List of model names
        """
        try:
            data = await self._get(f"{self.ollama_url}/api/tags")
            if data:
                return [model["name"] for model in data.get("models", [])]
        except Exception:
            pass
        return []

    def list_installed_models_sync(self) -> List[str]:
        """Synchronous version of list_installed_models"""
        try:
            return asyncio.get_event_loop().run_until_complete(
                self.list_installed_models()
            )
        except RuntimeError:
            # No event loop, create one
            return asyncio.run(self.list_installed_models())

    async def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        Get model info from Ollama.

        Args:
            model_name: The model name

        Returns:
            Model info dict or None
        """
        try:
            return await self._post(
                f"{self.ollama_url}/api/show",
                {"name": model_name}
            )
        except Exception:
            return None

    async def detect_model_spec(self, model_name: str) -> ModelSpec:
        """
        Detect/create a ModelSpec for a model.

        First checks the registry, then tries to auto-detect.

        Args:
            model_name: The model name to detect

        Returns:
            ModelSpec (from registry or auto-detected)
        """
        # Check registry first
        if model_name in KNOWN_MODELS:
            return KNOWN_MODELS[model_name]

        # Try to get info from Ollama
        info = await self.get_model_info(model_name)

        # Detect capabilities based on model name and info
        capabilities = self._detect_capabilities(model_name, info)
        prompt_format = self._detect_prompt_format(model_name, info)
        context_window = self._detect_context_window(info)

        # Create spec
        spec = ModelSpec(
            name=self._format_name(model_name),
            ollama_name=model_name,
            context_window=context_window,
            prompt_format=prompt_format,
            capabilities=capabilities,
            suitability=self._estimate_suitability(model_name, capabilities),
            notes="Auto-detected model"
        )

        # Register it for future use
        register_model(spec)

        return spec

    def detect_model_spec_sync(self, model_name: str) -> ModelSpec:
        """Synchronous version of detect_model_spec"""
        try:
            return asyncio.get_event_loop().run_until_complete(
                self.detect_model_spec(model_name)
            )
        except RuntimeError:
            return asyncio.run(self.detect_model_spec(model_name))

    async def sync_with_ollama(self) -> List[ModelSpec]:
        """
        Sync registry with installed Ollama models.

        Detects any new models and adds them to the registry.

        Returns:
            List of newly detected models
        """
        installed = await self.list_installed_models()
        new_models = []

        for model_name in installed:
            if model_name not in KNOWN_MODELS:
                spec = await self.detect_model_spec(model_name)
                new_models.append(spec)

        return new_models

    def sync_with_ollama_sync(self) -> List[ModelSpec]:
        """Synchronous version of sync_with_ollama"""
        try:
            return asyncio.get_event_loop().run_until_complete(
                self.sync_with_ollama()
            )
        except RuntimeError:
            return asyncio.run(self.sync_with_ollama())

    def _detect_capabilities(
        self,
        model_name: str,
        info: Optional[Dict]
    ) -> List[ModelCapability]:
        """Detect capabilities from model name and info"""
        capabilities = []
        name_lower = model_name.lower()

        # Detect from name
        if "coder" in name_lower or "code" in name_lower:
            capabilities.extend([
                ModelCapability.CODE_GENERATION,
                ModelCapability.CODE_COMPLETION,
            ])

        if any(x in name_lower for x in ["r1", "reason", "think"]):
            capabilities.append(ModelCapability.REASONING)

        if "math" in name_lower:
            capabilities.append(ModelCapability.MATH)

        if any(x in name_lower for x in [":1b", ":3b", ":0.5b", "3b", "1b"]):
            capabilities.append(ModelCapability.FAST_INFERENCE)

        if "vision" in name_lower or "llava" in name_lower:
            capabilities.append(ModelCapability.VISION)

        if "embed" in name_lower:
            capabilities.append(ModelCapability.EMBEDDING)

        if "tool" in name_lower or "function" in name_lower:
            capabilities.append(ModelCapability.TOOL_USE)

        # Check context window from info
        if info:
            ctx = self._detect_context_window(info)
            if ctx >= 100000:
                capabilities.append(ModelCapability.LONG_CONTEXT)

        # Default: at least general reasoning
        if not capabilities:
            capabilities.append(ModelCapability.REASONING)

        return list(set(capabilities))  # Remove duplicates

    def _detect_prompt_format(
        self,
        model_name: str,
        info: Optional[Dict]
    ) -> PromptFormat:
        """Detect prompt format from model name and info"""
        name_lower = model_name.lower()

        # Check model family
        if "qwen" in name_lower:
            return PromptFormat.CHATML
        if "deepseek" in name_lower:
            return PromptFormat.DEEPSEEK
        if "llama" in name_lower or "codellama" in name_lower:
            return PromptFormat.LLAMA
        if "mistral" in name_lower or "mixtral" in name_lower:
            return PromptFormat.MISTRAL
        if "command" in name_lower:
            return PromptFormat.COMMAND_R
        if "alpaca" in name_lower or "vicuna" in name_lower:
            return PromptFormat.ALPACA

        # Check template in info
        if info and "template" in info:
            template = info["template"].lower()
            if "im_start" in template or "chatml" in template:
                return PromptFormat.CHATML
            if "[inst]" in template:
                return PromptFormat.LLAMA
            if "### instruction" in template:
                return PromptFormat.ALPACA

        # Default to ChatML (most common)
        return PromptFormat.CHATML

    def _detect_context_window(self, info: Optional[Dict]) -> int:
        """Detect context window from info"""
        if info:
            # Check parameters
            params = info.get("parameters", {})
            if isinstance(params, dict) and "num_ctx" in params:
                return params["num_ctx"]

            # Check modelfile
            modelfile = info.get("modelfile", "")
            if isinstance(modelfile, str) and "num_ctx" in modelfile:
                match = re.search(r"num_ctx\s+(\d+)", modelfile)
                if match:
                    return int(match.group(1))

            # Check details
            details = info.get("details", {})
            if isinstance(details, dict):
                # Some models report context in details
                families = details.get("families", [])
                if "llama" in families:
                    return 128000  # Llama 3 default
                if "qwen2" in families:
                    return 32768

        return 32768  # Default

    def _estimate_suitability(
        self,
        model_name: str,
        capabilities: List[ModelCapability]
    ) -> Dict[str, float]:
        """Estimate suitability scores based on name and capabilities"""
        scores = {
            "coding": 0.5,
            "reasoning": 0.5,
            "general": 0.6,
            "fast": 0.5,
            "instant": 0.3,
        }

        name_lower = model_name.lower()

        # Adjust based on capabilities
        if ModelCapability.CODE_GENERATION in capabilities:
            scores["coding"] = 0.85

        if ModelCapability.REASONING in capabilities:
            scores["reasoning"] = 0.80

        if ModelCapability.FAST_INFERENCE in capabilities:
            scores["fast"] = 0.90
            scores["instant"] = 0.80
            scores["coding"] *= 0.8  # Fast models usually less capable

        if ModelCapability.EMBEDDING in capabilities:
            scores = {"embedding": 1.0}
            return scores

        # Adjust based on size hints in name
        if any(x in name_lower for x in ["70b", "72b", "65b"]):
            scores["coding"] = min(scores["coding"] * 1.15, 0.95)
            scores["reasoning"] = min(scores["reasoning"] * 1.15, 0.95)
            scores["fast"] *= 0.3
            scores["instant"] *= 0.2
        elif any(x in name_lower for x in ["32b", "34b", "33b"]):
            scores["coding"] = min(scores["coding"] * 1.1, 0.92)
            scores["reasoning"] = min(scores["reasoning"] * 1.1, 0.90)
            scores["fast"] *= 0.5
        elif any(x in name_lower for x in ["7b", "8b"]):
            scores["fast"] = min(scores["fast"] * 1.2, 0.92)
        elif any(x in name_lower for x in ["3b", "1b", "0.5b"]):
            scores["fast"] = 0.95
            scores["instant"] = 0.95
            scores["coding"] *= 0.6

        return scores

    def _format_name(self, model_name: str) -> str:
        """Format model name for display"""
        # Remove :latest suffix
        name = model_name.replace(":latest", "")
        # Capitalize parts
        parts = name.replace("-", " ").replace(":", " ").split()
        return " ".join(p.capitalize() for p in parts)

    async def _get(self, url: str) -> Optional[Dict]:
        """HTTP GET request"""
        if HAS_AIOHTTP:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    if response.status == 200:
                        return await response.json()
        elif HAS_HTTPX:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=10)
                if response.status_code == 200:
                    return response.json()
        return None

    async def _post(self, url: str, data: Dict) -> Optional[Dict]:
        """HTTP POST request"""
        if HAS_AIOHTTP:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url, json=data, timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        return await response.json()
        elif HAS_HTTPX:
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=data, timeout=10)
                if response.status_code == 200:
                    return response.json()
        return None


# Convenience function
def auto_detect_model(model_name: str, ollama_url: str = "http://localhost:11434") -> ModelSpec:
    """
    Auto-detect a model's capabilities.

    Args:
        model_name: The model name
        ollama_url: Ollama API URL

    Returns:
        ModelSpec for the model
    """
    detector = ModelDetector(ollama_url)
    return detector.detect_model_spec_sync(model_name)
