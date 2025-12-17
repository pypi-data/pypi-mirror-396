API Usage Examples
====================

This page explains how to use the API interfaces provided by Webis for structured information extraction, suitable for client programs or scripts with raw HTML data.

Example script: ``samples/api_usage.py``

The script demonstrates two typical calling patterns:

- Synchronous processing: Suitable for small batches of data, where the client waits for the response
- Asynchronous processing: Suitable for large batches of files, processed in the background with status polling capability

-----------------------------

Synchronous Processing Mode
-----------------------------

Used for one-time upload of a single or a small number of HTML files, with immediate waiting for extraction results:

.. code-block:: python

   import requests

   files = {"file": open("input.html", "rb")}
   data = {"task_id": "demo-task"}

   # Submit HTML for synchronous processing
   response = requests.post(
       "http://localhost:8002/extract/process-html",
       files=files,
       data=data
   )

   print("Processing result:", response.json())

   # Download compressed results
   task_id = data["task_id"]
   download_response = requests.get(
       f"http://localhost:8002/tasks/{task_id}/download", stream=True
   )
   with open(f"{task_id}_results.zip", "wb") as f:
       for chunk in download_response.iter_content(chunk_size=8192):
           f.write(chunk)

-----------------------------

Asynchronous Processing Mode
-----------------------------

Suitable for background processing, large file uploads and other scenarios, the interface returns an asynchronous task ID:

.. code-block:: python

   import requests

   files = {"file": open("input.html", "rb")}
   data = {"task_id": "long-task"}

   # Submit asynchronous task
   response = requests.post(
       "http://localhost:8002/extract/process-async",
       files=files,
       data=data
   )

   async_task_id = response.json()["task_id"]

   # Query task status
   status = requests.get(f"http://localhost:8002/tasks/{async_task_id}")
   print("Current status:", status.json())

   # Download processing results (after completion)
   download_response = requests.get(
       f"http://localhost:8002/tasks/{async_task_id}/download", stream=True
   )
   with open(f"{async_task_id}_async_results.zip", "wb") as f:
       for chunk in download_response.iter_content(chunk_size=8192):
           f.write(chunk)

-----------------------------

Running Example Scripts
-----------------------------

Use the built-in example script ``samples/api_usage.py`` to run test calls:

.. code-block:: bash

   # Default call to local service (synchronous mode)
   python samples/api_usage.py

   # Specify API key (required)
   python samples/api_usage.py --api-key YOUR_API_KEY_HERE

Result explanation:

- Synchronous task: Saved as ``{task_id}_results.zip``
- Asynchronous task: Saved as ``{async_task_id}_async_results.zip``

Ensure that there is at least one HTML file in the ``input_html/`` directory.
