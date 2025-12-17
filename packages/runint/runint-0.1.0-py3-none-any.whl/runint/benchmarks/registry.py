from typing import Dict, Type, Any, Optional
from .base import BaseBenchmark

# Stores the actual class references
_BENCHMARK_REGISTRY: Dict[str, Type[BaseBenchmark]] = {}
# Stores metadata (description, default config) for the UI/CLI
_BENCHMARK_METADATA: Dict[str, Dict[str, Any]] = {}

def register_benchmark(name: str, task_type: str, description: str):
    """
    Decorator to register a benchmark class.
    """
    def decorator(cls: Type[BaseBenchmark]):
        if name in _BENCHMARK_REGISTRY:
            raise ValueError(f"Benchmark '{name}' is already registered.")
            
        _BENCHMARK_REGISTRY[name] = cls
        _BENCHMARK_METADATA[name] = {
            "task_type": task_type,
            "description": description,
            "class_name": cls.__name__,
            "module": cls.__module__
        }
        return cls
    return decorator

def list_benchmarks() -> Dict[str, Dict[str, Any]]:
    return _BENCHMARK_METADATA

def get_benchmark_class(name: str) -> Optional[Type[BaseBenchmark]]:
    return _BENCHMARK_REGISTRY.get(name)
