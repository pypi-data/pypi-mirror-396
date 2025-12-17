Quickstart Guide
====================

The following steps are for users who have Python/conda configured, with the goal of running Webis and completing an extraction in the shortest possible time.

--------------
! Important Notes:
- Due to pytorch and vllm libraries only supporting Linux operating systems, this project can currently only run on Linux systems. Windows users can use the WSL feature
- Ubuntu is recommended

Installation and Initialization
--------------

Using Miniconda (recommended):

.. code-block:: bash

   conda create -n webis_html python=3.10 -y
   conda activate webis_html
   pip install -r requirements.txt

Starting the Model Service
--------------

.. code-block:: bash

   python scripts/start_model_server.py \
     --model-path Easonnoway/Web_info_extra_1.5b

The model will be automatically downloaded on first startup.

Sending Test Request
--------------

.. code-block:: bash

   curl -X POST http://localhost:8000/generate \
     -H "Content-Type: application/json" \
     -d '{"prompt": "Extract company name", "max_tokens": 128}'

Command Line Usage (CLI Mode)
-------------------------

.. code-block:: bash

   python scripts/webis_extract.py \
     --input ./data/example.html \
     --model node
