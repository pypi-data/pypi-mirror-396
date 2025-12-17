from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class EngineConfig(BaseModel):
    provider: str        # e.g., "ollama", "vllm", "local_python"
    container_image: Optional[str] = None  # e.g. "vllm/vllm-openai:latest"
    gpu_count: int = 0
    env_vars: Dict[str, str] = {}
    
class ModelConfig(BaseModel):
    name: str            # e.g. "llama3"
    source: str          # e.g. "huggingface", "ollama_library"
    parameters: Dict[str, Any] = {} # temp, top_k

class RunConfig(BaseModel):
    """
    The Master Object.
    Your proprietary algorithm generates this.
    The Open Source Library executes this.
    """
    version: str = "1.0"
    project_name: str
    engine: EngineConfig
    models: List[ModelConfig]
    
    required_benchmarks: List[str] = []