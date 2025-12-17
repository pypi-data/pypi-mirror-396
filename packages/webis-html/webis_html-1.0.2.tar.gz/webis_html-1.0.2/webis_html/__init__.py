#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Webis HTML - Intelligent Web Content Extraction Tool

This package provides complete HTML content extraction, processing and optimization functionality.
"""

__version__ = "1.0.2"
__author__ = "Webis"
__email__ = "webis@example.com"

# Import core functionality
from .core.html_processor import HtmlProcessor
from .core.llm_predictor import process_predictions
from .core.content_restorer import restore_text_from_json
from .core.dataset_processor import process_json_folder
from .core.llm_clean import run_filter, ResultFilter

# Import server functionality
from .server import create_app
from .server.services.extractor import ContentExtractor
from .server.services.task_manager import TaskManager

# Import CLI functionality
from .cli.cli import cli_app

# Import utility functions
from .utils.url_fetcher import UrlFetcher

__all__ = [
    # Version information
    "__version__",
    "__author__",
    "__email__",
    
    # Core processing functionality
    "HtmlProcessor",
    "process_predictions", 
    "restore_text_from_json",
    "process_json_folder",
    "run_filter",
    "ResultFilter",
    
    # Server functionality
    "create_app",
    "ContentExtractor",
    "TaskManager",
    
    # CLI functionality
    "cli_app",
    
    # Utility functions
    "UrlFetcher",
]

# Convenience functions
def _cleanup_intermediate_files(output_path, keep_predicted_texts=False):
    """
    Helper function to clean up intermediate files and cache directories
    
    Args:
        output_path: Path to output directory
        keep_predicted_texts: If True, keep predicted_texts directory (when no API key)
    """
    import shutil
    
    # Remove content_output directory (intermediate HTML processing output)
    content_output_dir = output_path / "content_output"
    if content_output_dir.exists():
        shutil.rmtree(content_output_dir)
    
    # Remove dataset directory (intermediate JSON files)
    dataset_dir = output_path / "dataset"
    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)
    
    # Remove predicted_texts if we have filtered_texts (when API key is provided)
    if not keep_predicted_texts:
        predicted_texts_dir = output_path / "predicted_texts"
        if predicted_texts_dir.exists():
            shutil.rmtree(predicted_texts_dir)

def extract_from_html(html_content, api_key=None, output_dir="./output"):
    """
    Convenience function: Extract valuable information from HTML content
    
    Args:
        html_content (str): HTML content
        api_key (str, optional): DeepSeek API key
        output_dir (str): Output directory
        
    Returns:
        dict: Extraction results
    """
    import tempfile
    import os
    from pathlib import Path
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
        f.write(html_content)
        temp_html_path = f.name
    
    try:
        # Create output directory
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Process HTML
        processor = HtmlProcessor(Path(temp_html_path).parent, output_path)
        processor.process_html_file(temp_html_path)
        
        # Dataset generation
        dataset_output = output_path / "dataset"
        dataset_output.mkdir(parents=True, exist_ok=True)
        process_json_folder(
            output_path / "content_output",
            dataset_output / "extra_datasets.json"
        )
        
        # Model prediction
        process_predictions(
            dataset_output / "extra_datasets.json", 
            dataset_output / "pred_results.json"
        )
        
        # Result restoration
        predicted_texts_dir = output_path / "predicted_texts"
        predicted_texts_dir.mkdir(parents=True, exist_ok=True)
        restore_text_from_json(
            dataset_output / "pred_results.json", 
            predicted_texts_dir
        )
        
        # DeepSeek filtering
        if api_key:
            filtered_texts_dir = output_path / "filtered_texts"
            filtered_texts_dir.mkdir(parents=True, exist_ok=True)
            run_filter(str(predicted_texts_dir), str(filtered_texts_dir), "deepseek", api_key)
            
            # Read filtered results
            results = []
            for txt_file in filtered_texts_dir.glob("*.txt"):
                with open(txt_file, 'r', encoding='utf-8') as f:
                    results.append({
                        "filename": txt_file.name,
                        "content": f.read()
                    })
            
            # Clean up intermediate files and cache (keep only filtered_texts)
            _cleanup_intermediate_files(output_path, keep_predicted_texts=False)
            
            return {
                "success": True,
                "results": results,
                "output_dir": str(filtered_texts_dir)
            }
        else:
            # Read prediction results
            results = []
            for txt_file in predicted_texts_dir.glob("*.txt"):
                with open(txt_file, 'r', encoding='utf-8') as f:
                    results.append({
                        "filename": txt_file.name,
                        "content": f.read()
                    })
            
            # Clean up intermediate files and cache (keep predicted_texts as final output)
            _cleanup_intermediate_files(output_path, keep_predicted_texts=True)
            
            return {
                "success": True,
                "results": results,
                "output_dir": str(predicted_texts_dir)
            }
            
    finally:
        # Clean up temporary files
        if os.path.exists(temp_html_path):
            os.unlink(temp_html_path)


def extract_from_url(url, api_key=None, output_dir="./output"):
    """
    Convenience function: Extract valuable information from URL
    
    Args:
        url (str): Web page URL
        api_key (str, optional): DeepSeek API key
        output_dir (str): Output directory
        
    Returns:
        dict: Extraction results
    """
    # Get web page content
    fetcher = UrlFetcher()
    html_content, _, title, status_code = fetcher.fetch_url(url)
    
    if html_content is None:
        return {
            "success": False,
            "error": f"Failed to fetch URL: {url}",
            "status_code": status_code
        }
    
    # Process HTML content
    result = extract_from_html(html_content, api_key, output_dir)
    result["url"] = url
    result["title"] = title
    return result

def extract_from_directory(input_dir, output_dir="./output", api_key=None):
    """
    Convenience function: Batch process all HTML files in directory
    
    Args:
        input_dir (str): Input directory path containing HTML files
        output_dir (str): Output directory path
        api_key (str, optional): DeepSeek API key
        
    Returns:
        dict: Batch processing results
    """
    from pathlib import Path
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    if not input_path.exists():
        return {
            "success": False,
            "error": f"Input directory does not exist: {input_path}"
        }
    
    # Get all HTML files
    html_files = list(input_path.glob("*.html"))
    if not html_files:
        return {
            "success": False,
            "error": "No HTML files found in input directory"
        }
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # Use HtmlProcessor for batch processing
        processor = HtmlProcessor(input_path, output_path)
        processor.process_html_folder()
        
        # Get configuration file path (automatically found)
        # process_json_folder now automatically finds configuration files
        
        # Dataset generation
        dataset_output = output_path / "dataset"
        dataset_output.mkdir(parents=True, exist_ok=True)
        process_json_folder(
            output_path / "content_output",
            dataset_output / "extra_datasets.json"
        )
        
        # Model prediction
        process_predictions(
            dataset_output / "extra_datasets.json", 
            dataset_output / "pred_results.json"
        )
        
        # Result restoration
        predicted_texts_dir = output_path / "predicted_texts"
        predicted_texts_dir.mkdir(parents=True, exist_ok=True)
        restore_text_from_json(
            dataset_output / "pred_results.json", 
            predicted_texts_dir
        )
        
        # DeepSeek filtering (if API key provided)
        if api_key:
            filtered_texts_dir = output_path / "filtered_texts"
            filtered_texts_dir.mkdir(parents=True, exist_ok=True)
            run_filter(str(predicted_texts_dir), str(filtered_texts_dir), "deepseek", api_key)
            
            # Read filtered results
            results = []
            for txt_file in filtered_texts_dir.glob("*.txt"):
                with open(txt_file, 'r', encoding='utf-8') as f:
                    results.append({
                        "filename": txt_file.name,
                        "content": f.read()
                    })
            
            # Clean up intermediate files and cache (keep only filtered_texts)
            _cleanup_intermediate_files(output_path, keep_predicted_texts=False)
            
            return {
                "success": True,
                "processed_files": len(html_files),
                "results": results,
                "output_dir": str(filtered_texts_dir)
            }
        else:
            # Read prediction results
            results = []
            for txt_file in predicted_texts_dir.glob("*.txt"):
                with open(txt_file, 'r', encoding='utf-8') as f:
                    results.append({
                        "filename": txt_file.name,
                        "content": f.read()
                    })
            
            # Clean up intermediate files and cache (keep predicted_texts as final output)
            _cleanup_intermediate_files(output_path, keep_predicted_texts=True)
            
            return {
                "success": True,
                "processed_files": len(html_files),
                "results": results,
                "output_dir": str(predicted_texts_dir)
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Batch processing failed: {str(e)}"
        }

# Add convenience functions to __all__
__all__.extend(["extract_from_html", "extract_from_url", "extract_from_directory"])
