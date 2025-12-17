# RUNINT: AI Runtime & Benchmark Intelligence

[![PyPI version](https://badge.fury.io/py/runint.svg)](https://badge.fury.io/py/runint)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**RunInt** is an open-source library designed to standardize how AI models are **deployed** (Run Intelligence) and **measured** (Benchmark Intelligence).

It serves as the universal adapter between high-level configuration intents ("I want to run Llama3 on a T4 GPU") and concrete, executable environments (Docker, Ollama, vLLM).

[Image of RunInt Library Architecture]

---

## 🚀 Key Features

* **Run Intelligence:**
    * **Agnostic Config:** Define your AI runtime in a clean JSON/YAML format.
    * **Auto-Deployment:** Generates production-ready `docker-compose.yml` files for Ollama, vLLM, and others.
    * **Hardware Aware:** Automatically detects GPU capabilities to optimize container settings.

* **Benchmark Intelligence:**
    * **Standardized Metrics:** Measures Latency, Throughput (tokens/s), and Quality (Accuracy/BLEU) in a unified format.
    * **Context Capture:** Every result is tagged with the exact hardware (GPU/CPU) and software version it ran on.
    * **Extensible Registry:** Easily add new tasks (OCR, Audio, Vision) via a simple Python decorator.

---

## 📦 Installation

```bash
pip install runint

Requirements: Python 3.10+, Docker (for deployment features)
```

## 🛠 Usage
### 1. Run Intelligence (Deployment)
Instead of writing complex Dockerfiles, use a Run Config.

```bash
config.json


{
  "project_name": "local_inference",
  "engine": {
    "provider": "ollama",
    "gpu_count": 0,
    "container_image": "ollama/ollama:latest"
  },
  "models": [
    { 
        "name": "llama3", 
        "source": "ollama_library" 
    }
  ]
}
```

```bash
Deploy it


# Generates docker-compose.yml and instructions
runint deploy --config config.json

# (Optional) Perform a dry-run to just see the generated file
runint deploy --config config.json --dry-run
```

### 2. Benchmark Intelligence (Measurement)

Once your engine is running (localhost or remote), run standard benchmarks against it.

```bash
# List available benchmarks:
runint info
```

```bash
# Run a benchmark:
runint benchmark \
  --task translation_en_de_v1 \
  --engine ollama \
  --model llama3 \
  --iterations 10
```

```bash
# Output:

Running translation_en_de_v1 on llama3 via ollama...
┏━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Run ID   ┃ Latency (ms) ┃ Metrics                       ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ a1b2c3d4 │        45.20 │ {'exact_match': 1.0}          │
│ e5f6g7h8 │        48.10 │ {'exact_match': 0.0}          │
└──────────┴──────────────┴───────────────────────────────┘
Average Latency: 46.65 ms
```

## 🧩 For Contributors
We welcome contributions! RunInt is designed to be modular.

### Adding a New Benchmark

1. Create a new file in src/runint/benchmarks/your_category/.

2. Inherit from BaseBenchmark.

3. Decorate with @register_benchmark

```bash
from runint.benchmarks.base import BaseBenchmark
from runint.benchmarks.registry import register_benchmark

@register_benchmark(name="my_new_task", task_type="custom", description="My cool test")
class MyBenchmark(BaseBenchmark):
    def load_data(self):
        return [{"input": "test"}]
    
    def run_inference(self, item):
        return "result"
        
    def calculate_metrics(self, pred, truth):
        return {"score": 100}
```

```bash
# Development Setup

git clone [https://github.com/filipzupancic/runint.git](https://github.com/filipzupancic/runint.git)
cd runint
poetry install
poetry run pytest
```

## 🔗 Integration

**RUNINT** is designed to be consumed by other applications.

- **Python API:**
```bash
from runint.schemas.config import RunConfig
from runint.runtime.manager import RuntimeManager

config = RunConfig(...)
manager = RuntimeManager(config)
manager.generate_deployment()
```

- **Benchmark Data:** All benchmark results are exported as standardized JSON objects (BenchmarkReport), making it easy to ingest data into analytics backends.


## 📄 License
MIT License. See LICENSE for details.
