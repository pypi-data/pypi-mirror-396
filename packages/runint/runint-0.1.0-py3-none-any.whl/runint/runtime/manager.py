import time
import subprocess
from rich.console import Console
from ..schemas.config import RunConfig
from .deploy.generators import DockerComposeGenerator

console = Console()

class RuntimeManager:
    def __init__(self, config: RunConfig):
        self.config = config

    def generate_deployment(self, output_path: str = "docker-compose.yml"):
        """
        Generates the infrastructure configuration (Docker Compose).
        """
        generator = DockerComposeGenerator(self.config)
        yaml_content = generator.generate_yaml()
        
        with open(output_path, "w") as f:
            f.write(yaml_content)

    def start_environment(self, compose_file: str = "docker-compose.yml"):
        """
        Runs 'docker compose up -d' (V2 Standard).
        """
        console.print(f"[dim]Running docker compose -f {compose_file} up -d[/dim]")
        
        try:
            subprocess.run(
                ["docker", "compose", "-f", compose_file, "up", "-d"], 
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            console.print("[dim]Waiting 5s for services to stabilize...[/dim]")
            time.sleep(5)
            
        except subprocess.CalledProcessError as e:
            # Decode error if possible, fallback to str
            err_msg = e.stderr.decode() if e.stderr else str(e)
            raise RuntimeError(f"Docker Compose failed: {err_msg}")
        except FileNotFoundError:
             raise RuntimeError("The 'docker' command was not found. Please verify Docker is installed and in your PATH.")

    def stop_environment(self, compose_file: str = "docker-compose.yml"):
        subprocess.run(["docker", "compose", "-f", compose_file, "down"])
