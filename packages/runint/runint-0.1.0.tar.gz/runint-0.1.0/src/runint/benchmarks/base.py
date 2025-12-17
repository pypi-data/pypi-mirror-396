import time
import logging
import platform
import subprocess
from abc import ABC, abstractmethod
from typing import List, Any, Dict, Optional
from datetime import datetime

from ..schemas.results import BenchmarkReport, BenchmarkResult, EnvironmentInfo

logger = logging.getLogger(__name__)

class BaseBenchmark(ABC):
    def __init__(
        self, 
        model_name: str, 
        engine: str, 
        task_type: str, 
        dataset_name: str, 
        config: Dict[str, Any] = None
    ):
        """
        Base class for all RunInt benchmarks.
        
        :param config: Task-specific settings (e.g., {'api_url': '...', 'temperature': 0.7})
        """
        self.model_name = model_name
        self.engine = engine
        self.task_type = task_type
        self.dataset_name = dataset_name
        self.config = config or {}

    @abstractmethod
    def load_data(self) -> List[Any]:
        """
        Must return a list of inputs (strings, image paths, etc.).
        """
        pass

    @abstractmethod
    def run_inference(self, input_item: Any) -> Any:
        """
        Must execute the call to the engine and return the raw output.
        """
        pass

    @abstractmethod
    def calculate_metrics(self, prediction: Any, ground_truth: Any) -> Dict[str, Any]:
        """
        Must return a dictionary of metric scores (e.g. {'bleu': 24.5}).
        """
        pass

    def _detect_environment(self) -> EnvironmentInfo:
        """
        Auto-discovers hardware specs. 
        Crucial for your backend to map performance to hardware.
        """
        gpu_name = None
        gpu_count = 0
        
        # Simple check for NVIDIA GPUs
        try:
            # Run nvidia-smi query
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                capture_output=True, text=True
            )
            if result.returncode == 0:
                gpus = result.stdout.strip().split('\n')
                gpus = [g for g in gpus if g] # filter empty
                if gpus:
                    gpu_name = gpus[0] # Take the first one
                    gpu_count = len(gpus)
        except FileNotFoundError:
            pass # No nvidia-smi found, likely CPU only or Mac

        # Basic CPU/Memory info
        cpu_info = platform.processor()
        
        return EnvironmentInfo(
            gpu_name=gpu_name,
            gpu_count=gpu_count,
            cpu_info=cpu_info,
            engine_version=self.config.get("engine_version", "unknown")
        )

    def execute(self) -> BenchmarkReport:
        """
        The main orchestration loop. 
        Returns a strongly typed BenchmarkReport.
        """
        logger.info(f"Starting {self.task_type} benchmark on {self.model_name}...")
        
        data_items = self.load_data()
        results_list: List[BenchmarkResult] = []
        
        # 1. Capture Environment Context
        env_info = self._detect_environment()

        # 2. Run the Loop
        for i, item in enumerate(data_items):
            input_data = item['input']
            ground_truth = item.get('ground_truth')
            
            # Use 'input_id' if present in data, else index
            item_id = item.get('id', str(i))
            
            start_time = time.perf_counter()
            error_flag = False
            error_msg = None
            prediction = None
            metrics = {}

            try:
                prediction = self.run_inference(input_data)
            except Exception as e:
                logger.error(f"Inference failed for item {i}: {e}")
                error_flag = True
                error_msg = str(e)
            
            end_time = time.perf_counter()
            latency = (end_time - start_time) * 1000  # Convert to ms

            # Calculate metrics only if successful and ground truth exists
            if not error_flag and ground_truth is not None:
                try:
                    metrics = self.calculate_metrics(prediction, ground_truth)
                except Exception as e:
                    logger.warning(f"Metric calculation failed: {e}")
                    metrics = {"metric_error": str(e)}

            # Create the Result Object
            res = BenchmarkResult(
                input_id=item_id,
                latency_ms=round(latency, 2),
                error=error_flag,
                error_message=error_msg,
                metrics=metrics,
                # Truncate raw output to avoid bloating the report
                raw_output_snippet=str(prediction)[:200] if prediction else None
            )
            results_list.append(res)

        # 3. Compile Final Report
        report = BenchmarkReport(
            project_name=self.config.get("project_name", "default"),
            task_type=self.task_type,
            model_name=self.model_name,
            engine=self.engine,
            dataset_name=self.dataset_name,
            parameters=self.config,
            environment=env_info,
            results=results_list
            # Summary stats are auto-calculated by the Validator in schemas/results.py
        )
        
        return report
