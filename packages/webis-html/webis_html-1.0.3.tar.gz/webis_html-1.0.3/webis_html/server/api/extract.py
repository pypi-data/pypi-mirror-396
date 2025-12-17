from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse, HTMLResponse
from typing import List, Optional
from pathlib import Path
import time

from ..services.extractor import ContentExtractor
from ..services.task_manager import TaskManager
from ..models.schemas import ProcessResult

router = APIRouter()
extractor: ContentExtractor = None
task_manager: TaskManager = None

def init_router(content_extractor: ContentExtractor, task_mgr: TaskManager):
    global extractor, task_manager
    extractor = content_extractor
    task_manager = task_mgr

@router.post("/process-html")
async def process_html(
    files: List[UploadFile] = File(...),
    tag_probs: Optional[UploadFile] = None,
    model_type: str = Form("node")
):
    task_id = task_manager.create_task()
    input_dir, output_dir = task_manager.get_task_dirs(task_id)
    
    # Save uploaded files
    for file in files:
        file_path = input_dir / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(await file.read())
    
    # tag_probs is now automatically handled by process_json_folder
    
    try:
        result = extractor.process_files(input_dir, output_dir, model_type)
        task_manager.update_task_status(task_id, **result.dict())
        
        return ProcessResult(
            task_id=task_id,
            status=result.status,
            result_count=len(result.results) if result.results else 0,
            message=result.message
        )
        
    except Exception as e:
        task_manager.update_task_status(task_id, status="failed", error=str(e), message="Processing failed")
        return JSONResponse(
            status_code=500,
            content=ProcessResult(
                task_id=task_id,
                status="failed",
                message="Processing failed",
                error=str(e)
            ).dict()
        )

@router.post("/process-async")
async def process_async(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    tag_probs: Optional[UploadFile] = None,
    model_type: str = Form("node")
):
    task_id = task_manager.create_task()
    input_dir, output_dir = task_manager.get_task_dirs(task_id)
    
    # Save uploaded files
    for file in files:
        file_path = input_dir / file.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(await file.read())
    
    # Process tag_probs
    tag_probs_path = None
    if tag_probs:
        tag_probs_path = output_dir / "tag_probs.json"
        with open(tag_probs_path, "wb") as f:
            f.write(await tag_probs.read())
    else:
        tag_probs_path = Path(__file__).resolve().parent.parent.parent.parent / 'config' / 'tag_probs.json'
    
    # Asynchronous processing function
    def process_task():
        try:
            result = extractor.process_files(input_dir, output_dir, model_type)
            task_manager.update_task_status(task_id, **result.dict())
        except Exception as e:
            task_manager.update_task_status(task_id, status="failed", error=str(e), message="Processing failed")
    
    # Add to background tasks
    background_tasks.add_task(process_task)
    
    return {"task_id": task_id, "status": "processing", "message": "Task submitted for processing"}

@router.get("/fetch-url")
async def fetch_url(
    url: str,
    remove_scripts: bool = True,
    remove_images: bool = True
):
    if not url or not (url.startswith('http://') or url.startswith('https://')):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL. URL must start with http:// or https://"
        )
    
    html_content, title, status_code = extractor.fetch_url(url)
    
    if html_content is None:
        raise HTTPException(
            status_code=status_code or 500,
            detail=f"Failed to fetch URL content: {url}"
        )
    
    return HTMLResponse(content=html_content, status_code=200)

@router.post("/process-url")
async def process_url(url: str, model_type: str = "node"):
    if not url or not (url.startswith('http://') or url.startswith('https://')):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL. URL must start with http:// or https://"
        )
    
    task_id = task_manager.create_task()
    input_dir, output_dir = task_manager.get_task_dirs(task_id)
    
    html_content, title, status_code = extractor.fetch_url(url)
    
    if html_content is None:
        raise HTTPException(
            status_code=status_code or 500,
            detail=f"Failed to fetch URL content: {url}"
        )
    
    # Save HTML content
    filename = f"url_content_{int(time.time())}.html"
    file_path = input_dir / filename
    
    if isinstance(html_content, bytes):
        with open(file_path, "wb") as f:
            f.write(html_content)
    else:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
    
    # Use default tag_probs file
    tag_probs_path = Path(__file__).resolve().parent.parent.parent.parent / 'config' / 'tag_probs.json'
    
    task_manager.update_task_status(
        task_id,
        url=url,
        title=title
    )
    
    try:
        result = extractor.process_files(input_dir, output_dir, model_type)
        task_manager.update_task_status(task_id, **result.dict())
        
        return ProcessResult(
            task_id=task_id,
            status=result.status,
            result_count=len(result.results) if result.results else 0,
            message=result.message
        )
        
    except Exception as e:
        task_manager.update_task_status(task_id, status="failed", error=str(e), message="Processing failed")
        return JSONResponse(
            status_code=500,
            content=ProcessResult(
                task_id=task_id,
                status="failed",
                message="Processing failed",
                error=str(e)
            ).dict()
        )