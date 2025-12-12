# context_builders.py

from __future__ import annotations

from abc import ABC, abstractmethod


from accl.schemas.base import (
    BasePayload,
    TemplateType,
)


class BaseContextBuilder(ABC):
    """
    Parent class for all context builders.
    Each specific template (data table, chart, etc.)
    will implement its own `build` method.
    """

    template_type: TemplateType

    @abstractmethod
    def build(self, **kwargs) -> BasePayload:
        """
        Build and return a payload for this template type.
        kwargs are template-specific.
        """
        raise NotImplementedError

