from typing import Dict, Any
from .base import BaseEngine

class VLLMEngine(BaseEngine):
    def get_docker_service_config(self) -> Dict[str, Any]:
        gpu_count = self.config.get("gpu_count", 1) # vLLM usually needs at least 1
        model_name = self.config.get("model_name", "facebook/opt-125m")
        hf_token = self.config.get("env_vars", {}).get("HF_TOKEN", "${HF_TOKEN}")

        service = {
            "image": self.config.get("container_image", "vllm/vllm-openai:latest"),
            "ports": ["8000:8000"],
            "runtime": "nvidia", # vLLM requires nvidia runtime usually
            "environment": [
                f"HUGGING_FACE_HUB_TOKEN={hf_token}"
            ],
            "volumes": ["~/.cache/huggingface:/root/.cache/huggingface"],
            "command": f"--model {model_name}",
            "deploy": {
                "resources": {
                    "reservations": {
                        "devices": [
                            {
                                "driver": "nvidia",
                                "count": gpu_count,
                                "capabilities": ["gpu"]
                            }
                        ]
                    }
                }
            }
        }
        return service
