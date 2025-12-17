CLI Usage
=========

Webis supports direct extraction of structured information from web pages through the command line.

Command Line Tool
----------

.. code-block:: bash

   python scripts/webis_extract.py --input <html_file_path> [options]

Common Parameters
--------

- ``--input``: Specify HTML file path (supports single file or directory)
- ``--output``: Output directory (default `./outputs`)
- ``--model``: Specify model type, such as `node`, `llama`
- ``--max-length``: Maximum length for model generation
- ``--batch-size``: Batch processing size
- ``--api-key``: Can be passed if the server requires an API Key


Basic Usage
----------

```bash
# Process HTML file (requires API key)
webis extract \
    --input /path/to/input_html \
    --output /path/to/output_basic \
    --api-key YOUR_API_KEY \
    --verbose
```

    Other Commands
    ----------

    ```bash
    # View version information
    webis version

    # Check API connection
    webis check-api --api-key YOUR_API_KEY

    # View help
    webis --help
    webis extract --help
    ```

    File Description
    ----------

    - `api_usage.py`: API interface usage example
    - `cli_usage.sh`: Command-line interface usage example
    - `input_html/`: Sample HTML file directory
    - `output_basic/`: CLI output results directory
    - `requirements.txt`: List of dependencies (including requests, goose3, newspaper3k, trafilatura, etc.)

    Processing Results Description
    ----------

    When processing HTML files using the API, zip files will be generated with content varying based on processing mode and tools:

    1. Synchronous processing result `{task_id}_results.zip`: Contains results of HTML files processed via synchronous API (first 2 files)
    2. Asynchronous processing result `{async_task_id}_async_results.zip`: Contains results of HTML files processed via asynchronous API (3rd file)

    The zip files contain the following:
    - Preprocessed HTML content
    - Dataset files
    - Model prediction results
    - Processed text content

    Important Notes
    ----------

    1. Server Startup:
    Ensure the following servers are running:
    - Model server (port 8000) [Started]
    - Web API server (port 8002) [Running]
    Example startup command:
    python -m uvicorn app:app --host 0.0.0.0 --port 8002

    2. DeepSeek Enhanced Features Require Valid API Key:
    Key configuration methods
    export DEEPSEEK_API_KEY=YOUR_API_KEY_HERE  or specify with --api-key in command

    3. Dependencies Installation:
    - Install required Python packages:
    pip install -r requirements.txt

    4. File Paths: 
    After processing, results are saved in the script's running directory by default. Recommend specifying `--output` parameter to avoid overwriting.

    5. Performance Optimization:
    - For large files, prefer asynchronous processing mode. 
    - Adjust batch_size (--batch-size in CLI) to optimize memory usage.