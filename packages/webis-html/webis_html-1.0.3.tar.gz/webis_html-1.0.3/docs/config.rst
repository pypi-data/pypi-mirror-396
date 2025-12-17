Configuration Options
================

Webis supports configuration of model path, GPU utilization, device usage, etc. through command-line arguments and environment variables.

Command-line Arguments
-------------

``scripts/start_model_server.py`` supports the following parameters when starting:

+------------------+------------------------+-----------------------------------------+
| Parameter        | Default Value          | Description                             |
+==================+========================+=========================================+
| --model-path     | WebFlow-Node-1.5b      | Model name or local path               |
+------------------+------------------------+-----------------------------------------+
| --gpu-id         | 0                      | GPU index to use                        |
+------------------+------------------------+-----------------------------------------+
| --memory-limit   | 0.9                    | GPU memory usage limit (between 0~1)    |
+------------------+------------------------+-----------------------------------------+

Environment Variables Support
----------------

Webis also supports the following environment variables (can be set via shell or injected through .env file):

+----------------------------+--------------------------------------------+
| Environment Variable       | Function                                   |
+============================+============================================+
| MODEL_PATH                | Model path (can replace parameter input)    |
+----------------------------+--------------------------------------------+
| CUDA_VISIBLE_DEVICES      | Control visible GPU indices                |
+----------------------------+--------------------------------------------+
| GPU_MEMORY_UTILIZATION    | Control maximum GPU memory usage (0~1)     |
+----------------------------+--------------------------------------------+

CLI Tool Parameters (webis_extract.py)
---------------------------------

The CLI tool supports the following configurations:

+----------------+----------+--------------------------------------------+
| Parameter      | Type     | Description                                |
+================+==========+============================================+
| --input        | str      | Input HTML file or directory              |
+----------------+----------+--------------------------------------------+
| --output       | str      | Output directory (default ./outputs)       |
+----------------+----------+--------------------------------------------+
| --model        | str      | Model to use (node/llama etc.)            |
+----------------+----------+--------------------------------------------+
| --max-length   | int      | Maximum number of tokens to generate       |
+----------------+----------+--------------------------------------------+
| --api-key      | str      | API Key credential if enabled             |
+----------------+----------+--------------------------------------------+