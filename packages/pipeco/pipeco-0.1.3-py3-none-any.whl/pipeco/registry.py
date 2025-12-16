"""Step registration and discovery system."""
from pipeco.contracts import Step

_REGISTRY: dict[str, type[Step]] = {}

def register(name: str):
    """Decorator to register a step class with a unique name."""
    def _wrap(cls: type[Step]) -> type[Step]:
        _REGISTRY[name] = cls
        cls.name = name  # convenience
        return cls
    return _wrap

def get_step(name: str) -> type[Step]:
    """Retrieve a registered step class by name."""
    if name not in _REGISTRY:
        raise KeyError(f"Step '{name}' not registered")
    return _REGISTRY[name]
