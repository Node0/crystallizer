# ./backends/providers/__init__.py
"""Registry for backend provider adapters."""
from typing import Callable, Dict, Type, TypeVar, Any

ProviderCls = TypeVar("ProviderCls")

PROVIDER_REGISTRY: Dict[str, Type[Any]] = {}


def register_provider(api_type: str) -> Callable[[ProviderCls], ProviderCls]:
    """Decorator to register a provider class for a given api_type."""
    def decorator(cls: ProviderCls) -> ProviderCls:
        if api_type in PROVIDER_REGISTRY:
            raise ValueError(f"Provider type '{api_type}' already registered")
        PROVIDER_REGISTRY[api_type] = cls
        return cls

    return decorator


def get_provider_class(api_type: str) -> Type[Any]:
    """Return the provider class associated with an api type."""
    try:
        return PROVIDER_REGISTRY[api_type]
    except KeyError as exc:
        raise ValueError(f"Provider type '{api_type}' not registered") from exc


# Ensure provider modules are imported for side effects (decorator registration)
from . import openai as _openai_provider  # noqa: E402,F401
from . import ollama as _ollama_provider  # noqa: E402,F401
from . import anthropic as _anthropic_provider  # noqa: E402,F401
from . import vllm as _vllm_provider  # noqa: E402,F401
