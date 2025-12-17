from pathlib import Path
from typing import Optional
from ..models.schemas import TaskStatus
from ...core.html_processor import HtmlProcessor
from ...core.dataset_processor import process_json_folder
from ...core.llm_predictor import process_predictions
from ...core.content_restorer import restore_text_from_json
from ...core.llm_clean import run_filter
from ...utils.url_fetcher import (
    UrlFetcher, 
    RENDER_METHOD_PLAYWRIGHT, 
    RENDER_METHOD_SELENIUM, 
    RENDER_METHOD_REQUESTS,
    has_playwright,
    has_selenium
)

class ContentExtractor:
    def __init__(self, deepseek_api_key: Optional[str] = None):
        self.deepseek_api_key = deepseek_api_key

    def process_files(self, input_dir: Path, output_dir: Path, model_type: str = "node") -> TaskStatus:
        try:
            # Data preprocessing
            processor = HtmlProcessor(input_dir, output_dir)
            processor.process_html_folder()
            
            # Dataset generation
            dataset_dir = output_dir / "dataset"
            dataset_dir.mkdir(exist_ok=True)
            process_json_folder(
                output_dir / "content_output",
                output_dir / "dataset" / "extra_datasets.json"
            )
            
            # Model prediction
            process_predictions(
                output_dir / "dataset" / "extra_datasets.json",
                output_dir / "dataset" / "pred_results.json"
            )
            
            # Result restoration
            predicted_dir = output_dir / "predicted_texts"
            predicted_dir.mkdir(exist_ok=True)
            restore_text_from_json(
                output_dir / "dataset" / "pred_results.json",
                predicted_dir
            )
            
            # Large model text filtering (final step)
            if not self.deepseek_api_key:
                return TaskStatus(
                    status="failed",
                    error="DEEPSEEK_API_KEY environment variable not set",
                    message="Missing DeepSeek API key"
                )
                
            filtered_dir = output_dir / "filtered_texts"
            filtered_dir.mkdir(exist_ok=True)
            run_filter(str(predicted_dir), str(filtered_dir), "deepseek", self.deepseek_api_key)
                
            # Collect results
            result_files = []
            for file in filtered_dir.glob("*.txt"):
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
                result_files.append({
                    "filename": file.name,
                    "content": content,
                    "source": "filtered"
                })
            
            return TaskStatus(
                status="completed",
                output_dir=str(output_dir),
                results=result_files,
                message="Processing completed"
            )
            
        except Exception as e:
            return TaskStatus(
                status="failed",
                error=str(e),
                message="Processing failed"
            )

    def fetch_url(self, url: str) -> tuple[Optional[str], Optional[str], Optional[int]]:
        render_method = RENDER_METHOD_PLAYWRIGHT
        if not has_playwright and has_selenium:
            render_method = RENDER_METHOD_SELENIUM
        elif not has_playwright and not has_selenium:
            render_method = RENDER_METHOD_REQUESTS
        
        fetcher = UrlFetcher(render_method=render_method, wait_time=5)
        html_content, _, title, status_code = fetcher.fetch_url(url)
        
        return html_content, title, status_code