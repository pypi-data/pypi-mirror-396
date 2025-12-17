import requests
from typing import List, Any, Dict
from ..base import BaseBenchmark
from ..registry import register_benchmark

@register_benchmark(
    name="translation_en_de_v1",
    task_type="nlp",
    description="Basic English to German translation benchmark using simple string matching."
)
class TranslationBenchmark(BaseBenchmark):
    
    def load_data(self) -> List[Any]:
        return [
            {"id": "1", "input": "Hello world", "ground_truth": "Hallo Welt"},
            {"id": "2", "input": "The weather is nice", "ground_truth": "Das Wetter ist schön"},
            {"id": "3", "input": "Machine learning is fun", "ground_truth": "Maschinelles Lernen macht Spaß"}
        ]

    def run_inference(self, input_text: str) -> str:
        """
        Adapts the call based on the selected engine (Ollama vs vLLM).
        """
        api_url = self.config.get("api_url", "http://localhost:11434")
        
        # 1. OLLAMA API
        if self.engine == "ollama":
            url = f"{api_url}/api/generate"
            payload = {
                "model": self.model_name,
                "prompt": f"Translate to German: {input_text}",
                "stream": False,
                "options": {"temperature": 0}
            }
            try:
                response = requests.post(url, json=payload, timeout=30)
                response.raise_for_status()
                return response.json().get("response", "").strip()
            except requests.RequestException as e:
                raise RuntimeError(f"Ollama API Error: {e}")

        # 2. vLLM (OpenAI Compatible) API
        elif self.engine == "vllm":
            url = f"{api_url}/v1/completions"
            payload = {
                "model": self.model_name,
                "prompt": f"Translate to German: {input_text}",
                "max_tokens": 50,
                "temperature": 0
            }
            try:
                response = requests.post(url, json=payload, timeout=30)
                response.raise_for_status()
                return response.json()['choices'][0]['text'].strip()
            except requests.RequestException as e:
                raise RuntimeError(f"vLLM API Error: {e}")
        
        else:
            raise ValueError(f"Unsupported engine for this benchmark: {self.engine}")

    def calculate_metrics(self, prediction: str, ground_truth: str) -> Dict[str, Any]:
        match = 1.0 if prediction.strip().lower() == ground_truth.strip().lower() else 0.0
        return {
            "exact_match": match,
            "char_length_diff": abs(len(prediction) - len(ground_truth))
        }
