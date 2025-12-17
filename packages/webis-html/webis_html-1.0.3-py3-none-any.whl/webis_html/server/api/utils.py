from fastapi import APIRouter
import subprocess
import sys

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Web Content Extraction API service is running"}

@router.get("/check-model-server")
def check_model_server():
    try:
        import requests
        # Check model server health
        response = requests.get("http://localhost:9065/health", timeout=5)
        if response.status_code == 200:
            return {"status": "online"}
        else:
            return {"status": "offline", "reason": f"Health check failed with status code {response.status_code}"}
    except Exception as e:
        return {"status": "offline", "reason": str(e)}

@router.get("/install-dependencies")
def install_dependencies():
    try:
        dependencies = [
            "fastapi",
            "uvicorn",
            "python-multipart",
            "aiofiles",
            "pydantic",
            "requests",
            "tqdm",
            "beautifulsoup4",
            "lxml",
            "vllm"
        ]
        
        cmd = [sys.executable, "-m", "pip", "install", "--upgrade"] + dependencies
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            return {
                "status": "failed",
                "message": "Dependency installation failed",
                "error": result.stderr
            }
            
        return {
            "status": "success",
            "message": "All dependencies installed successfully",
            "details": dependencies
        }
    except Exception as e:
        return {
            "status": "failed",
            "message": f"Installation error: {str(e)}"
        }

@router.get("/check-model-server")
def check_model_server():
    try:
        import requests
        response = requests.get("http://localhost:9065/health", timeout=5)
        if response.status_code == 200:
            return {
                "status": "online",
                "message": "Model server is running",
                "details": response.json()
            }
        else:
            return {
                "status": "error",
                "message": "Model server responded with error",
                "statusCode": response.status_code
            }
    except requests.exceptions.RequestException:
        return {
            "status": "offline",
            "message": "Model server is not running or unreachable",
            "hint": "Please ensure node_model_server.py is started"
        }
