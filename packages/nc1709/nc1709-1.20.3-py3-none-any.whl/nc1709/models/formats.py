"""
Prompt format templates for different model families.

Each model family expects prompts in a specific format. This module
handles the conversion automatically based on the model's prompt_format.
"""

from typing import List, Dict, Optional
from dataclasses import dataclass
from .registry import PromptFormat


@dataclass
class Message:
    """A chat message"""
    role: str  # "system", "user", "assistant"
    content: str


class PromptFormatter:
    """
    Formats prompts for different model families.

    Each model family has its own expected format. This class
    handles the conversion automatically.

    Example:
        formatter = PromptFormatter()
        messages = [
            Message("system", "You are helpful"),
            Message("user", "Hello!"),
        ]
        prompt = formatter.format(messages, PromptFormat.CHATML)
    """

    @staticmethod
    def format(
        messages: List[Message],
        prompt_format: PromptFormat,
        add_generation_prompt: bool = True
    ) -> str:
        """
        Format messages for a specific model format.

        Args:
            messages: List of messages
            prompt_format: The format to use
            add_generation_prompt: Whether to add the assistant prompt at end

        Returns:
            Formatted prompt string
        """
        formatters = {
            PromptFormat.CHATML: PromptFormatter._format_chatml,
            PromptFormat.LLAMA: PromptFormatter._format_llama,
            PromptFormat.ALPACA: PromptFormatter._format_alpaca,
            PromptFormat.RAW: PromptFormatter._format_raw,
            PromptFormat.DEEPSEEK: PromptFormatter._format_deepseek,
            PromptFormat.MISTRAL: PromptFormatter._format_mistral,
            PromptFormat.COMMAND_R: PromptFormatter._format_command_r,
        }

        formatter = formatters.get(prompt_format, PromptFormatter._format_raw)
        return formatter(messages, add_generation_prompt)

    @staticmethod
    def format_from_dicts(
        messages: List[Dict[str, str]],
        prompt_format: PromptFormat,
        add_generation_prompt: bool = True
    ) -> str:
        """
        Format messages from dict format.

        Args:
            messages: List of {"role": "...", "content": "..."} dicts
            prompt_format: The format to use
            add_generation_prompt: Whether to add the assistant prompt at end

        Returns:
            Formatted prompt string
        """
        msg_objects = [
            Message(role=m["role"], content=m["content"])
            for m in messages
        ]
        return PromptFormatter.format(msg_objects, prompt_format, add_generation_prompt)

    @staticmethod
    def _format_chatml(messages: List[Message], add_gen: bool) -> str:
        """
        ChatML format (Qwen, OpenAI-style)

        <|im_start|>system
        You are helpful<|im_end|>
        <|im_start|>user
        Hello!<|im_end|>
        <|im_start|>assistant
        """
        parts = []
        for msg in messages:
            parts.append(f"<|im_start|>{msg.role}\n{msg.content}<|im_end|>")

        if add_gen:
            parts.append("<|im_start|>assistant\n")

        return "\n".join(parts)

    @staticmethod
    def _format_llama(messages: List[Message], add_gen: bool) -> str:
        """
        Llama/Llama2/Llama3 format

        [INST] <<SYS>>
        System prompt
        <</SYS>>

        User message [/INST] Assistant response
        """
        parts = []
        system_msg = None

        for msg in messages:
            if msg.role == "system":
                system_msg = msg.content
            elif msg.role == "user":
                if system_msg:
                    parts.append(
                        f"[INST] <<SYS>>\n{system_msg}\n<</SYS>>\n\n{msg.content} [/INST]"
                    )
                    system_msg = None
                else:
                    parts.append(f"[INST] {msg.content} [/INST]")
            elif msg.role == "assistant":
                parts.append(msg.content)

        return "\n".join(parts)

    @staticmethod
    def _format_alpaca(messages: List[Message], add_gen: bool) -> str:
        """
        Alpaca format

        ### System:
        System prompt

        ### Instruction:
        User message

        ### Response:
        """
        parts = []

        for msg in messages:
            if msg.role == "system":
                parts.append(f"### System:\n{msg.content}\n")
            elif msg.role == "user":
                parts.append(f"### Instruction:\n{msg.content}\n")
            elif msg.role == "assistant":
                parts.append(f"### Response:\n{msg.content}\n")

        if add_gen:
            parts.append("### Response:\n")

        return "\n".join(parts)

    @staticmethod
    def _format_deepseek(messages: List[Message], add_gen: bool) -> str:
        """
        DeepSeek format

        <|system|>
        System prompt
        <|user|>
        User message
        <|assistant|>
        """
        parts = []

        for msg in messages:
            if msg.role == "system":
                parts.append(f"<|system|>\n{msg.content}")
            elif msg.role == "user":
                parts.append(f"<|user|>\n{msg.content}")
            elif msg.role == "assistant":
                parts.append(f"<|assistant|>\n{msg.content}")

        if add_gen:
            parts.append("<|assistant|>\n")

        return "\n".join(parts)

    @staticmethod
    def _format_mistral(messages: List[Message], add_gen: bool) -> str:
        """
        Mistral format

        [INST] User message [/INST] Assistant response
        """
        parts = []

        for msg in messages:
            if msg.role == "user":
                parts.append(f"[INST] {msg.content} [/INST]")
            elif msg.role == "assistant":
                parts.append(msg.content)
            elif msg.role == "system":
                # Mistral often handles system as first user message
                parts.append(f"[INST] {msg.content}\n")

        return "".join(parts)

    @staticmethod
    def _format_command_r(messages: List[Message], add_gen: bool) -> str:
        """
        Cohere Command-R format

        <|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>...<|END_OF_TURN_TOKEN|>
        <|START_OF_TURN_TOKEN|><|USER_TOKEN|>...<|END_OF_TURN_TOKEN|>
        <|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>
        """
        parts = []

        for msg in messages:
            if msg.role == "system":
                parts.append(
                    f"<|START_OF_TURN_TOKEN|><|SYSTEM_TOKEN|>{msg.content}<|END_OF_TURN_TOKEN|>"
                )
            elif msg.role == "user":
                parts.append(
                    f"<|START_OF_TURN_TOKEN|><|USER_TOKEN|>{msg.content}<|END_OF_TURN_TOKEN|>"
                )
            elif msg.role == "assistant":
                parts.append(
                    f"<|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>{msg.content}<|END_OF_TURN_TOKEN|>"
                )

        if add_gen:
            parts.append("<|START_OF_TURN_TOKEN|><|CHATBOT_TOKEN|>")

        return "".join(parts)

    @staticmethod
    def _format_raw(messages: List[Message], add_gen: bool) -> str:
        """
        Raw format (no special tokens)

        System: ...
        User: ...
        Assistant: ...
        """
        parts = []

        for msg in messages:
            if msg.role == "system":
                parts.append(f"System: {msg.content}\n")
            elif msg.role == "user":
                parts.append(f"User: {msg.content}\n")
            elif msg.role == "assistant":
                parts.append(f"Assistant: {msg.content}\n")

        if add_gen:
            parts.append("Assistant: ")

        return "".join(parts)


def get_format_info(prompt_format: PromptFormat) -> Dict[str, str]:
    """
    Get information about a prompt format.

    Args:
        prompt_format: The format to describe

    Returns:
        Dict with format details
    """
    info = {
        PromptFormat.CHATML: {
            "name": "ChatML",
            "description": "OpenAI-style format used by Qwen, etc.",
            "example": "<|im_start|>user\\nHello<|im_end|>",
        },
        PromptFormat.LLAMA: {
            "name": "Llama",
            "description": "Meta Llama format with [INST] tags",
            "example": "[INST] Hello [/INST]",
        },
        PromptFormat.ALPACA: {
            "name": "Alpaca",
            "description": "Stanford Alpaca instruction format",
            "example": "### Instruction:\\nHello\\n### Response:",
        },
        PromptFormat.DEEPSEEK: {
            "name": "DeepSeek",
            "description": "DeepSeek model format",
            "example": "<|user|>\\nHello\\n<|assistant|>",
        },
        PromptFormat.MISTRAL: {
            "name": "Mistral",
            "description": "Mistral AI format",
            "example": "[INST] Hello [/INST]",
        },
        PromptFormat.COMMAND_R: {
            "name": "Command-R",
            "description": "Cohere Command-R format",
            "example": "<|START_OF_TURN_TOKEN|><|USER_TOKEN|>Hello",
        },
        PromptFormat.RAW: {
            "name": "Raw",
            "description": "Plain text with role prefixes",
            "example": "User: Hello\\nAssistant:",
        },
    }
    return info.get(prompt_format, {"name": "Unknown", "description": "", "example": ""})
