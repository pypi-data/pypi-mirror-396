#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from pathlib import Path
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import extract, tasks, utils
from .services.extractor import ContentExtractor
from .services.task_manager import TaskManager

def load_api_key():
    try:
        # Get api-keys in configuration doc
        config_path = Path(__file__).resolve().parent.parent / 'config' / 'api_keys.json'
        api_keys_path = config_path
        
        if api_keys_path.exists():
            with open(api_keys_path, 'r') as f:
                import json
                api_keys = json.load(f)
                api_key = api_keys.get('deepseek_api_key')
                if api_key and api_key != "your-api-key-here":
                    print(f"Success: Loaded DeepSeek API key from config file {api_keys_path}")
                    return api_key
                else:
                    print(f"Warning: API key in {api_keys_path} is invalid or default")
                    return None
        else:
            print(f"Warning: API key config file does not exist: {api_keys_path}")
            return None
    except Exception as e:
        print(f"Error reading API key file: {str(e)}")
        return None

def create_app():
    # Get API key (required)
    api_key = load_api_key()
    if not api_key:
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if api_key:
            print("Success: Loaded DeepSeek API key from environment variable DEEPSEEK_API_KEY")
        else:
            print("Error: DeepSeek API key is required but not found")
            print("Please set DEEPSEEK_API_KEY environment variable or configure it in config/api_keys.json")
            raise ValueError("DeepSeek API key is required")
    
    # Create FastAPI application
    app = FastAPI(
        title="Web Content Extraction API",
        description="API service providing web content extraction, dataset generation, model prediction, result restoration, and DeepSeek optimization",
        version="1.0.0"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=86400,
    )

    # Create temporary directory
    temp_dir = Path("./temp_api_data")
    temp_dir.mkdir(exist_ok=True)

    # Initialize services
    task_manager = TaskManager(temp_dir)
    content_extractor = ContentExtractor(api_key)

    # Initialize routers
    extract.init_router(content_extractor, task_manager)
    tasks.init_router(task_manager)

    # Register routes
    app.include_router(utils.router, tags=["utils"])
    app.include_router(extract.router, prefix="/extract", tags=["extract"])
    app.include_router(tasks.router, prefix="/tasks", tags=["tasks"])

    return app

def main():
    app = create_app()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        limit_concurrency=100,
        limit_max_requests=10000,
    )

if __name__ == "__main__":
    main()
