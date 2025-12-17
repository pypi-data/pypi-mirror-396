Webis Documentation Home
===============

Overview
----
Webis is a web structured information extraction tool based on large language models, supporting entity extraction (such as company names, contact information, etc.) from HTML content via HTTP interface or command line.
This project can run in local GPU environments, supports automatic loading of HuggingFace format models, and is compatible with both CLI and RESTful API calls.

Features
----
- Advanced Web Crawling and Text Discovery:
    - Support for sitemaps (TXT, XML) and feeds (ATOM, JSON, RSS)
    - Intelligent crawling and URL management (filtering and deduplication)
- Parallel Processing of Online and Offline Input:
    - Efficient handling of download queues
    - Previously downloaded HTML files and parsed HTML trees
- Robust and Configurable Key Element Extraction:
    - Main content (common patterns and generic algorithms like jusText and readability)
    - Metadata (title, author, date, site name, categories, and tags)
    - Format and structure: paragraphs, headings, lists, quotes, code, line breaks, inline text formatting
    - Optional elements: comments, links, images, tables
- Multiple Output Formats:
    - TXT and Markdown
    - CSV format
    - JSON format
    - HTML, XML, and XML-TEI


Installation and Dependencies
---------

This project recommends using Conda for Python environment management and depends on the following components:

- Python ≥ 3.10
- PyTorch + CUDA (GPU environment recommended)
- vLLM (for efficient model inference)
- FastAPI + Uvicorn (for API service)

For quick environment setup, please refer to :doc:`quickstart` for detailed steps and dependency installation methods.


Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   quickstart
   api_usage
   cli_usage
   gui_usage
   troubleshooting
   config

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
