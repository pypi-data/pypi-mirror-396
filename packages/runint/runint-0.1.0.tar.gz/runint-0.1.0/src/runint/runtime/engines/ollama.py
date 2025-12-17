from typing import Dict, Any
from .base import BaseEngine

class OllamaEngine(BaseEngine):
    def get_docker_service_config(self) -> Dict[str, Any]:
        gpu_count = self.config.get("gpu_count", 0)
        
        service = {
            "image": self.config.get("container_image", "ollama/ollama:latest"),
            "ports": ["11434:11434"],
            "volumes": ["ollama_models:/root/.ollama"],
            "restart": "always"
        }

        # Add GPU support if requested
        if gpu_count > 0:
            service["deploy"] = {
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
            
        return service
