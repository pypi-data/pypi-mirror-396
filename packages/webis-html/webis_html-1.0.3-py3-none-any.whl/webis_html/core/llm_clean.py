import os
import json
import requests
from tqdm import tqdm
from pathlib import Path

class ResultFilter:

    @staticmethod
    def call_deepseek_api(text, api_key=None):
        # DeepSeek API configuration
        if api_key is None:
            api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ValueError("DeepSeek API key not provided and not found in environment variables")
        
        base_url = "https://api.siliconflow.cn/v1/chat/completions"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        model_name = "deepseek-ai/DeepSeek-V3"
        prompt = f"""
        Act as a prudent text refinement assistant. Carefully read the entire text to grasp its core themes and logical structure. Remove only obvious fragmentary noise elements such as advertising snippets, repetitive promotional phrases, and platform-generated system messages. Preserve all potentially meaningful content including examples, technical details, and domain-specific terminology. When in doubt about content relevance, prioritize retention over deletion. Return the refined text strictly following these rules:1.No explanations - Provide only the cleaned text without any analysis.2.​Format integrity - Strictly preserve the original formatting and syntactic flow.3.​Minimal intervention - Limit changes to unquestionably non-essential elements.Now, please analyze and filter the following text:'{text}''
        """
        data = {
            "model": model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "stream": False,
            "max_tokens": 20000,
            "stop": None,
            "temperature": 0.7,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "response_format": {"type": "text"}
        }
        try:
            response = requests.post(base_url, json=data, headers=headers)
            response.raise_for_status()
            result = response.json()
            # print(f"result:{result}")
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"api_key:{api_key}")
            print(f"Error calling DeepSeek API: {e}")
            print(f"Error response: {response.text}")
            print(f"Error status code: {response.status_code}")
            return text

    @staticmethod
    def call_chatgpt_api(text):
        # ChatGPT API configuration (if needed in the future)
        # Currently not supported, return original text
        raise NotImplementedError("ChatGPT API not implemented yet. Please use 'deepseek' instead.")
    
    @staticmethod
    def filter_text(text, api_type, api_key=None):
        # Call the corresponding API based on the specified API type
        if api_type == "chatgpt":
            return ResultFilter.call_chatgpt_api(text)
        elif api_type == "deepseek":
            return ResultFilter.call_deepseek_api(text, api_key)
        else:
            raise ValueError("Unsupported API type. Supported types: 'deepseek'")

    @staticmethod
    def process_files(input_dir, output_dir, api_type, api_key=None):
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        file_count = 0

        # Traverse files in input directory
        for filename in tqdm(os.listdir(input_dir), desc="Processing files"):
            if filename.endswith(".txt"):
                # Read original text
                input_path = os.path.join(input_dir, filename)
                with open(input_path, 'r', encoding='utf-8') as f:
                    original_text = f.read()

                # Filter text
                filtered_text = ResultFilter.filter_text(original_text, api_type, api_key)

                # Save filtered text
                output_filename = filename
                output_path = os.path.join(output_dir, output_filename)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(filtered_text)

                file_count += 1

        print(f"Filtering completed, processed {file_count} files in total")
        print(f"Filtered results saved to {output_dir} folder")

def _load_api_key_from_config():
    """Load API key from configuration file or environment variable"""

     # Priority 1: Read from environment variable
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if api_key and api_key != "your_deepseek_api_key_here" and not api_key.lower().startswith("your_"):
        return api_key
        
    # Priority 2: Read from config/api_keys.json
    project_root = Path(__file__).resolve().parent.parent.parent
    api_keys_path = project_root / "config" / "api_keys.json"
    
    if api_keys_path.exists():
        try:
            with open(api_keys_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            api_key = data.get("deepseek_api_key")
            if api_key and api_key != "your_deepseek_api_key_here" and not api_key.lower().startswith("your_"):
                return api_key
        except (OSError, ValueError):
            pass
    
    return None


def run_filter(input_dir, output_dir, api_type, api_key=None):
    """
    Run text filtering process.
    
    Parameters:
        input_dir (str): Input directory containing text files to be filtered.
        output_dir (str): Output directory for saving filtered text files.
        api_type (str): API type to use ("chatgpt" or "deepseek").
        api_key (str): API key (optional, if not provided will be read from config/api_keys.json or environment variables).
    """
    if api_key is None:
        api_key = _load_api_key_from_config()
    
    ResultFilter.process_files(input_dir, output_dir, api_type, api_key)

if __name__ == "__main__":
    input_dir = r"F:\data\sftllm_v2_predicted_texts"
    output_dir = r"F:\data\double_gpt_sftllm_v4_predicted_texts"