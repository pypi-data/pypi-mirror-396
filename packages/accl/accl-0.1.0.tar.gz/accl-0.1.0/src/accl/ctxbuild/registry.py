from typing import Dict, Type
from accl.ctxbuild.base import BaseContextBuilder
from accl.utils.schemas import TemplateType, BasePayload
from ctxbuild.dtctx_builder import DataTableContextBuilder

class ContextBuilderRegistry:
    """
    Simple registry so you can easily add more template builders later.
    For example: ChartContextBuilder, AnglesContextBuilder, etc.
    """

    def __init__(self) -> None:
        self._builders: Dict[TemplateType, BaseContextBuilder] = {}

    def register(self, builder: BaseContextBuilder) -> None:
        self._builders[builder.template_type] = builder

    def get(self, template_type: TemplateType) -> BaseContextBuilder:
        try:
            return self._builders[template_type]
        except KeyError:
            raise ValueError(f"No context builder registered for {template_type}")

    def build(self, template_type: TemplateType, **kwargs) -> BasePayload:
        """
        Convenience helper: directly build a payload by template type.
        """
        builder = self.get(template_type)
        return builder.build(**kwargs)


# Create a global registry instance and register known builders
context_registry = ContextBuilderRegistry()
context_registry.register(DataTableContextBuilder())
