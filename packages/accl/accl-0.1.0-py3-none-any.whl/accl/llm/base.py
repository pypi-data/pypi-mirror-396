# src/llm/base.py

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseLLM(ABC):
    """
    Abstract base class for all LLM wrappers in this project.

    Provides:
      - invoke(): raw model call
      - invoke_json(): convenience for 'JSON list' responses
    """

    @abstractmethod
    def invoke(self, prompt: str, **kwargs: Any) -> Any:
        """
        Low-level call to the underlying model.
        Concrete implementations decide what they return.
        """
        raise NotImplementedError

    @abstractmethod
    def invoke_json(self, prompt: str, **kwargs: Any) -> List[Dict]:
        """
        High-level call for prompts that are expected to produce
        a JSON array/list of objects.

        Implementations should:
          - call `invoke`
          - extract raw text/content
          - parse JSON into Python objects
        """
        raise NotImplementedError
