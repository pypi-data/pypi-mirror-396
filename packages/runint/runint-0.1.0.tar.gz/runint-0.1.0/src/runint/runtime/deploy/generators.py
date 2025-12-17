import yaml
from ..engines.ollama import OllamaEngine
from ..engines.vllm import VLLMEngine
from ...schemas.config import RunConfig

class DockerComposeGenerator:
    def __init__(self, config: RunConfig):
        self.config = config

    def generate_yaml(self) -> str:
        """
        Constructs the docker-compose dictionary and returns it as a YAML string.
        """
        services = {}
        volumes = {}
        
        # Extract engine settings
        engine_settings = self.config.engine.model_dump()
        provider = self.config.engine.provider

        # Select the correct Engine class
        if provider == "ollama":
            engine_instance = OllamaEngine(engine_settings)
            services["ollama"] = engine_instance.get_docker_service_config()
            # Register the volume required by Ollama
            volumes["ollama_models"] = {}
            
        elif provider == "vllm":
            engine_instance = VLLMEngine(engine_settings)
            services["vllm"] = engine_instance.get_docker_service_config()
            # vLLM usually binds a host path, so no named volume is needed by default
            
        else:
            pass

        # Build the final structure
        compose_structure = {
            "services": services,
        }

        # Only add the volumes key if we actually have named volumes
        if volumes:
            compose_structure["volumes"] = volumes

        # Return as YAML string
        return yaml.dump(compose_structure, sort_keys=False)
