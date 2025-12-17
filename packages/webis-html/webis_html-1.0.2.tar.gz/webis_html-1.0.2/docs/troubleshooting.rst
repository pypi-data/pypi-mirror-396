Troubleshooting Guide
=================================

This page lists common errors and solutions encountered while using Webis.

---

Unable to Access API: 401 Unauthorized
-------------------------------

**Cause**:

- No valid API Key provided, or server authentication is enabled.

**Solution**:

- Check ``api_keys.json`` in the project root directory and copy a valid key.
- Add the ``api_key`` parameter when calling the API, for example:

  .. code-block:: bash

     curl -X POST http://localhost:8000/generate \
       -H "Content-Type: application/json" \
       -d '{"prompt": "hello", "api_key": "your-key"}'

---

Model Loading Failed Due to Insufficient GPU Memory
-------------------------------

**Error**:

.. code-block:: text

   ValueError: Free memory on device (...) is less than desired GPU memory utilization (...)

**Cause**:

- Remaining GPU memory is less than the model's required usage limit.

**Solution**:

- Set a lower ``GPU_MEMORY_UTILIZATION``:

  .. code-block:: bash

     export GPU_MEMORY_UTILIZATION=0.6

---

libcudart.so Not Found Error
--------------------------

.. code-block:: text

   ImportError: libcudart.so.11.0: cannot open shared object file: No such file or directory

**Cause**:

- CUDA dynamic library not installed or version incompatible.

**Solution**:

- Install PyTorch with corresponding CUDA through conda:

  .. code-block:: bash

     conda install pytorch-cuda=12.1 -c pytorch -c nvidia

---

CUDA Error: No Kernel Image Available for Execution
----------------------------------------------------

**Error**:

.. code-block:: text

   RuntimeError: CUDA error: no kernel image is available for execution on the device
   UserWarning: NVIDIA GeForce RTX 5090 with CUDA capability sm_120 is not compatible with the current PyTorch installation.

**Cause**:

- New GPU architecture (e.g., RTX 5090 with sm_120) requires newer PyTorch version
- Current PyTorch version only supports older GPU architectures (sm_50 to sm_90)

**Solution**:

Update PyTorch to a version that supports your GPU:

.. code-block:: bash

   # For RTX 5090 and newer GPUs, use PyTorch 2.5+ with CUDA 12.4+
   conda install pytorch pytorch-cuda=12.4 -c pytorch -c nvidia

   # Or use pip
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

**Alternative**: If updating PyTorch is not possible, you can run in CPU mode (slower performance):

.. code-block:: bash

   export DEVICE=cpu
   python scripts/start_model_server.py

---

Build Failed: C Compiler Not Found
--------------------------

.. code-block:: text

   RuntimeError: Failed to find C compiler.

**Cause**:

- Compiler tools like ``gcc`` not found when Triton is compiling model kernels.

**Solution**:

- Install ``build-essential``:

  .. code-block:: bash

     sudo apt update
     sudo apt install build-essential

---

HuggingFace Model Download Failed (WSL Network Issue)
-------------------------------------------

**Symptoms**:

- Model download gets stuck or reports `ConnectionError`, `Failed to establish new connection`
- Error: `Network is unreachable` or `Name or service not known`
- Unable to connect to `huggingface.co`

**Solutions**:

**Option 1: Use HuggingFace Mirror (Recommended for China)**

If you are in China or have network issues accessing HuggingFace, use the mirror site:

.. code-block:: bash

   export HF_ENDPOINT=https://hf-mirror.com

**Option 2: Configure Proxy (WSL/Network Proxy)**

1. Open CMD in Windows and run:

   .. code-block:: cmd

      ipconfig

2. Find your machine's IPv4 address, e.g., `192.168.0.123`

3. Set proxy in WSL:

   .. code-block:: bash

      export http_proxy=http://192.168.0.123:7890
      export https_proxy=http://192.168.0.123:7890

**Option 3: Use Local Model Path**

If you have already downloaded the model to a local directory:

.. code-block:: bash

   python scripts/start_model_server.py --model-path /path/to/local/model

---

No Model Output / API Returns Empty String
------------------------------

**Possible Causes**:

- ``prompt`` content incomplete or lacking context.
- ``max_tokens`` set too low, generation truncated.

**Suggestions**:

- Increase the ``max_tokens`` parameter appropriately (e.g., 256 → 512)
- Use clear prompts, for example:

  .. code-block:: text

     Please extract contact name and phone number from the following HTML: <html>...</html>

---

Package Manager Lock Error (dpkg/apt)
------------------------------

**Error**:

.. code-block:: text

   Waiting for cache lock: Could not get lock /var/lib/dpkg/lock-frontend. It is held by process

**Cause**:

- Another package management process (apt, apt-get, dpkg, or system update) is running
- A previous package installation was interrupted, leaving a lock file

**Solution**:

1. Wait if another legitimate update is in progress
2. If no other update is running, check for the process holding the lock:

   .. code-block:: bash

      ps aux | grep -i apt

3. If needed, remove the lock files (use with caution):

   .. code-block:: bash

      sudo rm /var/lib/apt/lists/lock
      sudo rm /var/lib/dpkg/lock
      sudo rm /var/lib/dpkg/lock-frontend
      sudo dpkg --configure -a