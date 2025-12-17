from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

# --- Core Components ---

class EnvironmentInfo(BaseModel):
    """
    Captures the context where the benchmark ran.
    Essential for the "Advisor" to learn hardware capabilities.
    """
    gpu_name: Optional[str] = None      # e.g. "NVIDIA A100-SXM4-40GB"
    gpu_count: int = 0
    cpu_info: Optional[str] = None
    system_memory_gb: Optional[float] = None
    engine_version: Optional[str] = None # e.g. "ollama:0.1.28"

# --- Individual Run Result ---

class BenchmarkResult(BaseModel):
    """
    Represents a single iteration of a benchmark (one prompt/image).
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Inputs
    input_id: Optional[str] = None       # ID of the specific dataset item
    input_length: Optional[int] = None   # Tokens or pixels
    
    # Performance
    latency_ms: float                    # The most critical metric
    time_to_first_token_ms: Optional[float] = None # Critical for LLM streaming
    tokens_per_second: Optional[float] = None
    
    # Quality / Outcome
    error: bool = False
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = {}         # Flexible: {"bleu": 24.5} or {"iou": 0.85}
    
    # Debugging
    raw_output_snippet: Optional[str] = Field(None, max_length=500)

# --- Aggregate Report ---

class BenchmarkReport(BaseModel):
    """
    The full package returned after a benchmark suite finishes.
    This is what your CLI will save to JSON and your Backend will ingest.
    """
    run_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    project_name: str = "default"
    
    # Context
    task_type: str        # "translation", "ocr"
    model_name: str       # "llama3"
    engine: str           # "ollama"
    dataset_name: str
    
    # Configuration
    parameters: Dict[str, Any]       # The config used (temp, top_k, etc.)
    environment: EnvironmentInfo     # Hardware context
    
    # The Data
    results: List[BenchmarkResult]
    
    # Summary Statistics (Calculated post-run)
    summary: Dict[str, float] = {}   # {"avg_latency": 45.2, "p99_latency": 120.1}

    @validator('summary', always=True)
    def calculate_defaults(cls, v, values):
        """
        Auto-calculate basic stats if not provided.
        """
        if v: return v # If summary already exists, keep it
        
        results = values.get('results', [])
        if not results:
            return {}
            
        latencies = [r.latency_ms for r in results if not r.error]
        if not latencies:
            return {"error_rate": 1.0}
            
        return {
            "total_requests": len(results),
            "successful_requests": len(latencies),
            "avg_latency_ms": sum(latencies) / len(latencies),
            "min_latency_ms": min(latencies),
            "max_latency_ms": max(latencies)
        }
