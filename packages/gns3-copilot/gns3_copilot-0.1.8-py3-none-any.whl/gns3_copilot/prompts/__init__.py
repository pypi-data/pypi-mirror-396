# Prompts module for GNS3 Copilot

from .prompt_loader import load_system_prompt
from .title_prompt import TITLE_PROMPT

__all__ = [
    "load_system_prompt",
    "TITLE_PROMPT"
]
