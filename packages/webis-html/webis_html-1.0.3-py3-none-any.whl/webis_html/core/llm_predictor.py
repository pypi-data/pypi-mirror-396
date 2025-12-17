import json
import os
import asyncio
import logging
from pathlib import Path
from typing import Optional, Union

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False
    # Remove synchronous requests fallback logic
    print("Warning: httpx module not found. Please install it via 'pip install httpx'")

from tqdm import tqdm

REMOTE_MODEL_URL = os.environ.get(
    "LLM_PREDICTOR_API_URL", "https://api.siliconflow.cn/v1/chat/completions"
)
REMOTE_MODEL_NAME = os.environ.get("LLM_PREDICTOR_MODEL", "deepseek-ai/DeepSeek-V3")
REMOTE_API_TIMEOUT = float(os.environ.get("LLM_PREDICTOR_API_TIMEOUT", "30"))
MAX_CONCURRENT_REQUESTS = int(os.environ.get("LLM_PREDICTOR_MAX_CONCURRENT", "10"))
CONFIG_PATH_CANDIDATES = [
    Path(__file__).resolve().parent.parent / "config" / "api_keys.json",
    Path.cwd() / "config" / "api_keys.json",
]
_API_KEY_CACHE: Optional[str] = None


def _load_api_key_from_config() -> Optional[str]:
    for path in CONFIG_PATH_CANDIDATES:
        if not path.exists():
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            api_key = data.get("llm_predictor_api_key") or data.get("deepseek_api_key")
            if api_key and not api_key.lower().startswith("your_"):
                return api_key
        except (OSError, ValueError) as err:
            print(f"Failed to read configuration file {path}: {err}")
    return None


def _resolve_api_key() -> Optional[str]:
    global _API_KEY_CACHE
    if _API_KEY_CACHE:
        return _API_KEY_CACHE

    for env_var in ("LLM_PREDICTOR_API_KEY", "DEEPSEEK_API_KEY"):
        api_key = os.environ.get(env_var)
        if api_key and not api_key.lower().startswith("your_"):
            _API_KEY_CACHE = api_key
            return api_key

    api_key = _load_api_key_from_config()
    if api_key:
        _API_KEY_CACHE = api_key
    return api_key


def _build_api_payload(text_input: str) -> dict:
    """Build API request payload"""
    messages = [
        {
            "role": "system",
            "content": (
                "You are a precise noise detector for DOM text segments. "
                "Reply using only a single digit: '1' keeps the text, '0' discards it."
            ),
        },
        {
            "role": "user",
            "content": (
                "Perform three-step noise detection:\n"
                "1. Content analysis (determine if the snippet is irrelevant).\n"
                "2. Tag risk analysis (consider last_tag and risk_tags metadata).\n"
                "3. Structural verification (depth and confidence).\n"
                "Only respond with 0 or 1 for the following snippet:\n"
                f"{text_input}"
            ),
        },
    ]
    return {
        "model": REMOTE_MODEL_NAME,
        "messages": messages,
        "stream": False,
        "max_tokens": 8,
        "temperature": 0.1,
        "top_p": 0.9,
        "top_k": 50,
        "n": 1,
        "response_format": {"type": "text"},
    }


async def call_remote_model_api_async(
    text_input: str, 
    api_key: Optional[str] = None,
    client: Optional[object] = None
) -> Union[int, str]:
    """Asynchronously call remote LLM API for noise detection"""
    api_key = api_key or _resolve_api_key()
    if not api_key:
        print("Missing remote LLM API key, please set LLM_PREDICTOR_API_KEY or DEEPSEEK_API_KEY.")
        return "error"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = _build_api_payload(text_input)

    try:
        if HAS_HTTPX and client is not None:
            # Use httpx async client
            response = await client.post(
                REMOTE_MODEL_URL,
                json=payload,
                headers=headers,
                timeout=REMOTE_API_TIMEOUT
            )
            response.raise_for_status()
            result = response.json()
            
            content = (
                result.get("choices", [{}])[0]
                .get("message", {})
                .get("content", "")
                .strip()
            )
            for char in content:
                if char in ("0", "1"):
                    return int(char)
            print(f"Remote API returned incorrect format: {content}")
            return "error"
        else:
            print("Error: httpx not installed or client not provided, cannot execute async request")
            return "error"
    except Exception as e:
        print(f"Remote API request error: {e}")
        return "error"


async def process_predictions_async(
    input_json_path: str, 
    output_json_path: str,
    max_concurrent: Optional[int] = None,
    api_key: Optional[str] = None
):
    """Asynchronously batch process prediction tasks"""
    max_concurrent = max_concurrent or MAX_CONCURRENT_REQUESTS
    
    if not HAS_HTTPX:
        print("Error: httpx library must be installed to use async processing feature. Please run 'pip install httpx'")
        return

    with open(input_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if os.path.exists(output_json_path):
        with open(output_json_path, "r", encoding="utf-8") as f:
            results = json.load(f)
    else:
        results = {}
    
    # Use provided api_key, or try to resolve from environment/config
    if api_key is None:
        api_key = _resolve_api_key()
    if not api_key:
        print("Warning: Missing remote LLM API key. Using default predictions (keeping all text segments).")
        # Create default predictions (all 1, meaning keep all text) when no API key is available
        if not data:
            print("Warning: Input data is empty. Creating empty prediction results.")
            results = {}
        else:
            for file_name, entries in data.items():
                if file_name in results:
                    continue
                results[file_name] = [
                    {
                        "text": item.get("text", ""),
                        "path": item.get("path", ""),
                        "prediction": 1  # Default: keep all text when no API key
                    }
                    for item in entries
                ]
        # Save default predictions
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Default predictions saved to {output_json_path}")
        return
    
    # Create httpx async client
    async with httpx.AsyncClient(timeout=REMOTE_API_TIMEOUT) as client:
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_item_with_semaphore(item):
            async with semaphore:
                content_input = item.get("input", "")
                llm_result = await call_remote_model_api_async(content_input, api_key, client)
                return {
                    "text": item.get("text", ""),
                    "path": item.get("path", ""),
                    "prediction": llm_result
                }
        
        for file_name, entries in tqdm(data.items(), desc="Processing files"):
            if file_name in results:
                print(f"Skipping {file_name} as it has already been processed.")
                continue
            
            # Create progress bar
            pbar = tqdm(total=len(entries), desc=f"Processing entries in {file_name}", leave=False)
            
            async def process_item_with_progress(item):
                result = await process_item_with_semaphore(item)
                pbar.update(1)
                return result
            
            # Concurrently process all entries
            tasks = [process_item_with_progress(item) for item in entries]
            updated_entries = await asyncio.gather(*tasks)
            pbar.close()
            
            results[file_name] = updated_entries
            # Save immediately after processing each file
            with open(output_json_path, "w", encoding="utf-8") as f:
                json.dump(results, f, ensure_ascii=False, indent=2)


def process_predictions(input_json_path: str, output_json_path: str, api_key: Optional[str] = None):
    """
    Batch process prediction tasks (async only)
    
    Args:
        input_json_path: Input JSON file path
        output_json_path: Output JSON file path
        api_key: Optional API key. If not provided, will be resolved from environment variables or config file
    """
    if not HAS_HTTPX:
        print("Error: httpx library must be installed. Please run 'pip install httpx'")
        return
        
    # Force use of async processing
    asyncio.run(process_predictions_async(input_json_path, output_json_path, api_key=api_key))


def main():
    folder_path = r"/home/ubuntu/Webis/samples/output_basic"
    input_json = os.path.join(folder_path, "dataset", "extra_datasets.json")
    output_json = os.path.join(folder_path, "dataset", "pred_results.json")
    process_predictions(input_json, output_json)


if __name__ == "__main__":
    main()
    