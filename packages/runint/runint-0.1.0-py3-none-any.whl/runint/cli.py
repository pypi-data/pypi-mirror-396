import typer
import json
import os
from typing import Annotated
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Import internal modules
from runint.benchmarks.registry import list_benchmarks, get_benchmark_class
from runint.runtime.manager import RuntimeManager
from runint.schemas.config import RunConfig

app = typer.Typer(help="RunInt: AI Runtime & Benchmark Intelligence CLI", pretty_exceptions_show_locals=False)
console = Console()

@app.command()
def info():
    """List available benchmarks."""
    console.print(Panel.fit("[bold cyan]RunInt Library v0.0.1[/bold cyan]", border_style="cyan"))
    benchmarks = list_benchmarks()
    if benchmarks:
        table = Table(title="Available Benchmarks")
        table.add_column("Name", style="green")
        table.add_column("Type", style="magenta")
        table.add_column("Description")
        for name, meta in benchmarks.items():
            table.add_row(name, meta.get("task_type", "N/A"), meta.get("description", ""))
        console.print(table)
    else:
        console.print("[yellow]No benchmarks registered.[/yellow]")

@app.command()
def deploy(
    config: Annotated[str, typer.Option(help="Path to the JSON run configuration file")],
    dry_run: Annotated[bool, typer.Option(help="Generate deployment files without starting them")] = False
):
    """
    [Run Intelligence] Deploys an AI environment based on a configuration file.
    """
    # The variable 'config' automatically becomes the flag '--config'
    if not os.path.exists(config):
        console.print(f"[bold red]Error:[/bold red] Config file '{config}' not found.")
        raise typer.Exit(code=1)

    console.print(f"[bold blue]Loading configuration from {config}...[/bold blue]")
    
    try:
        with open(config, 'r') as f:
            data = json.load(f)
            run_config = RunConfig(**data)
            
        manager = RuntimeManager(run_config)
        output_file = "docker-compose.yml"
        manager.generate_deployment(output_path=output_file)
        console.print(f"[green]✔ Deployment file generated at: {output_file}[/green]")
        
        if not dry_run:
            console.print("[yellow]Starting environment...[/yellow]")
            manager.start_environment()
            console.print("[bold green]✔ Environment is up and running![/bold green]")
            
    except Exception as e:
        console.print(f"[bold red]Deployment failed:[/bold red] {e}")
        raise typer.Exit(code=1)

@app.command()
def benchmark(
    task: Annotated[str, typer.Option(help="Name of the benchmark")],
    engine: Annotated[str, typer.Option(help="Engine (ollama/vllm)")] = "ollama",
    url: Annotated[str, typer.Option(help="Engine URL")] = "http://localhost:11434",
    model: Annotated[str, typer.Option(help="Model name")] = "llama3",
    iterations: Annotated[int, typer.Option(help="Number of iterations")] = 5
):
    """
    [Benchmark Intelligence] Runs a specific benchmark.
    """
    cls = get_benchmark_class(task)
    if not cls:
        console.print(f"[bold red]Error:[/bold red] Benchmark '{task}' not found.")
        raise typer.Exit(code=1)

    console.print(f"Running [bold cyan]{task}[/bold cyan] on [bold]{model}[/bold]...")
    
    # Initialize benchmark
    bench = cls(
        model_name=model, 
        engine=engine, 
        task_type=task, 
        dataset_name="default",
        config={"api_url": url, "iterations": iterations}
    )

    try:
        report = bench.execute()
        
        # Display Results
        table = Table(title=f"Results for {task}")
        table.add_column("Run ID", style="dim")
        table.add_column("Latency (ms)", justify="right")
        table.add_column("Metrics")
        
        for res in report.results:
            table.add_row(str(res.id)[:8], f"{res.latency_ms:.2f}", str(res.metrics))
        console.print(table)
        
    except Exception as e:
        console.print(f"[bold red]Benchmark failed:[/bold red] {e}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
