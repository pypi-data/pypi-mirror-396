import click
from pathlib import Path
import os
import sys
from tqdm import tqdm
import time
import subprocess
import webbrowser

# Import core modules
from ..core.html_processor import HtmlProcessor
from ..core.dataset_processor import process_json_folder
from ..core.llm_predictor import process_predictions
from ..core.content_restorer import restore_text_from_json
from ..core.llm_clean import run_filter


# CLI main command group
@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def cli_app():
    """
    Webis Content Extraction Tool - Extract and clean valuable content from HTML files

    This tool can process HTML files, extract valuable content, filter out irrelevant noise text,
    and use DeepSeek API for content optimization.

    Usage examples:

      # Basic usage, process HTML files in input_folder (requires setting deepseek_api_key in config/api_keys.json or DEEPSEEK_API_KEY environment variable)
      webis extract --input ./input_folder

      # Specify API key
      webis extract --input ./input_folder --api-key YOUR_API_KEY

      # Specify output directory
      webis extract --input ./input_folder --output ./results --api-key YOUR_API_KEY
    """
    pass


# Unified function to load API key
def load_api_key():
    """Load DeepSeek API key from configuration file or environment variable"""
    import json

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
        except (OSError, ValueError) as err:
            pass

    
    return None


@cli_app.command("extract")
@click.option("--input", "-i", required=True, help="Input directory path containing HTML files")
@click.option("--output", "-o", default="./output", help="Output directory path for processing results")
@click.option(
    "--api-key",
    "-k",
    default=None,
    help="DeepSeek API key (required, can also be set via config/api_keys.json or DEEPSEEK_API_KEY environment variable)",
)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed processing progress and information")
def extract(input, output, api_key, verbose):
    """Extract and clean valuable content from HTML files"""
    start_time = time.time()
    input_path = Path(input)
    output_path = Path(output)

    # Check if input directory exists
    if not input_path.exists():
        click.secho(f"Error: Input directory '{input_path}' does not exist", fg="red")
        return

    # Check if there are HTML files
    html_files = list(input_path.glob("**/*.html"))
    if not html_files:
        click.secho(f"Warning: No HTML files found in input directory", fg="yellow")
        return

    click.secho(f"Found {len(html_files)} HTML files", fg="green")

    # tag_probs configuration file is now automatically handled by process_json_folder

    # Ensure output directory exists
    output_path.mkdir(parents=True, exist_ok=True)

    # Data preprocessing
    click.echo("Step 1/4: HTML preprocessing...")
    processor = HtmlProcessor(input_path, output_path)
    processor.process_html_folder()

    # Dataset generation
    click.echo("Step 2/4: Generating dataset...")
    dataset_output = output_path / "dataset"
    dataset_output.mkdir(parents=True, exist_ok=True)
    process_json_folder(
        output_path / "content_output",
        dataset_output / "extra_datasets.json",
    )

    # Model prediction
    click.echo("Step 3/4: Executing model predictions...")
    process_predictions(
        dataset_output / "extra_datasets.json", dataset_output / "pred_results.json"
    )

    # Result restoration
    click.echo("Step 4/4: Restoring processed text...")
    predicted_texts_dir = output_path / "predicted_texts"
    predicted_texts_dir.mkdir(parents=True, exist_ok=True)
    restore_text_from_json(dataset_output / "pred_results.json", predicted_texts_dir)
    click.secho(
        f"Node and local processing completed! Results saved in: {predicted_texts_dir}", fg="green"
    )

    # DeepSeek extraction (required step)
    # If API key not provided in command line, try to get from configuration file or environment variable
    if api_key is None:
        api_key = load_api_key()
        if api_key and verbose:
            click.secho(f"Loaded DeepSeek API key from configuration file or environment variable", fg="blue")

    # Check if there is a valid API key in the end
    if api_key is None:
        click.secho("Error: DeepSeek API key is required", fg="red")
        click.echo("You can provide the API key in the following ways:")
        click.echo("1. Use command line parameter --api-key")
        click.echo("2. Set deepseek_api_key in config/api_keys.json")
        click.echo("3. Set environment variable DEEPSEEK_API_KEY")
        return

    click.secho("Performing large model text filtering...", fg="blue")
    filtered_texts_dir = output_path / "filtered_texts"
    filtered_texts_dir.mkdir(parents=True, exist_ok=True)

    with tqdm(total=len(html_files), desc="Filtering files") as pbar:

        def progress_callback(completed, total):
            pbar.update(1)

        run_filter(str(predicted_texts_dir), str(filtered_texts_dir), "deepseek", api_key)

    click.secho(f"Large model filtering completed! Results saved in: {filtered_texts_dir}", fg="green")

    # Display processing statistics
    elapsed_time = time.time() - start_time
    click.echo(f"\nProcessing statistics:")
    click.echo(f"- Number of HTML files processed: {len(html_files)}")
    click.echo(f"- Total processing time: {elapsed_time:.2f} seconds")
    filtered_files = list(filtered_texts_dir.glob("*.txt"))
    click.echo(f"- Number of files after large model filtering: {len(filtered_files)}")

    click.secho("\nProcessing completed!", fg="green", bold=True)


# Add other utility commands


@cli_app.command("version")
def version():
    """Display version information"""
    try:
        import tomli

        pyproject_path = (
            Path(__file__).resolve().parent.parent.parent / "pyproject.toml"
        )
        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                pyproject = tomli.load(f)
                version = pyproject.get("project", {}).get("version", "Unknown")
        else:
            version = "Unknown"
    except Exception:
        version = "Unknown"

    click.echo(f"Webis Content Extraction Tool v{version}")
    click.echo("© 2025 Webis Team")


@cli_app.command("check-api")
@click.option("--api-key", "-k", required=True, help="DeepSeek API key")
def check_api(api_key):
    """Test DeepSeek API connection status"""
    click.echo("Checking DeepSeek API connection...")
    try:
        # Import requests to check connection
        import requests

        url = "https://api.siliconflow.cn/v1/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

        # Send a simple request to test the API
        data = {
            "model": "deepseek-ai/DeepSeek-V3",
            "messages": [{"role": "user", "content": "Hello"}],
            "max_tokens": 5,
        }

        response = requests.post(url, headers=headers, json=data, timeout=10)

        if response.status_code == 200:
            click.secho("✓ API connection successful!", fg="green")
        else:
            click.secho(f"× API connection failed: Status code {response.status_code}", fg="red")
            click.echo(f"Response: {response.text}")

    except Exception as e:
        click.secho(f"× API connection error: {str(e)}", fg="red")


@cli_app.command("gui")
@click.option("--web-port", "-wp", default=9000, help="Web API server port (default 9000)")
@click.option("--gui-port", "-gp", default=8001, help="GUI interface server port (default 8001)")
@click.option("--api-key", "-k", default=None, help="DeepSeek API key (optional, can also be set via environment variable)")
def gui(web_port, gui_port, api_key):
    """Start Webis visual interface server (first start Web API server, then start GUI interface)"""
    import http.server
    import socketserver
    import socket
    import time
    import requests
    
    # 1. Start Web API server
    click.secho("Step 1/2: Starting Web API server...", fg="blue")
    
    # Find start_web_server.py script path
    package_root = Path(__file__).resolve().parent.parent
    web_server_script = package_root / "scripts" / "start_web_server.py"
    
    if not web_server_script.exists():
        click.secho(f"Error: Cannot find Web server script: {web_server_script}", fg="red")
        return
    
    # Check if port is already in use
    def check_port(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return False
            except socket.error:
                return True
    
    web_server_process = None
    if check_port(web_port):
        click.secho(f"Warning: Web API server port {web_port} is already in use, trying to use the already running server", fg="yellow")
        # Verify if the already running server is available
        try:
            response = requests.get(f"http://127.0.0.1:{web_port}/", timeout=2)
            if response.status_code in [200, 404]:
                click.secho(f"✓ Using already running Web API server: http://127.0.0.1:{web_port}", fg="green")
            else:
                click.secho(f"Error: Port {web_port} is occupied but server is not available", fg="red")
                return
        except (requests.RequestException, ConnectionError):
            click.secho(f"Error: Port {web_port} is occupied but server is not available", fg="red")
            return
    else:
        # Build startup command
        cmd = [sys.executable, str(web_server_script), "--port", str(web_port), "--host", "127.0.0.1"]
        if api_key:
            cmd.extend(["--api-key", api_key])
        
        # Start Web server process
        try:
            web_server_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=str(package_root)
            )
            click.secho(f"Web API server process started (PID: {web_server_process.pid})", fg="green")
        except Exception as e:
            click.secho(f"Error: Failed to start Web API server: {e}", fg="red")
            return
        
        # Wait for server to start
        click.echo("Waiting for Web API server to start...")
        max_wait = 30  # Maximum wait 30 seconds
        waited = 0
        while waited < max_wait:
            try:
                response = requests.get(f"http://127.0.0.1:{web_port}/", timeout=2)
                if response.status_code in [200, 404]:  # 404 also means server is started
                    click.secho(f"✓ Web API server started: http://127.0.0.1:{web_port}", fg="green")
                    break
            except (requests.RequestException, ConnectionError):
                time.sleep(1)
                waited += 1
                if waited % 3 == 0:
                    click.echo(f"  Waiting... ({waited}/{max_wait} seconds)")
        
        if waited >= max_wait:
            click.secho("Error: Web API server startup timeout", fg="red")
            if web_server_process:
                web_server_process.terminate()
            return
    
    # 2. Start GUI interface server
    click.secho("Step 2/2: Starting GUI interface server...", fg="blue")
    
    # Get frontend directory path
    package_root = Path(__file__).resolve().parent.parent
    frontend_dir = package_root / "frontend"
    
    # Check if frontend directory exists
    if not frontend_dir.exists():
        click.secho(f"Error: Frontend directory does not exist: {frontend_dir}", fg="red")
        if web_server_process:
            web_server_process.terminate()
        return
    
    # Check if index.html exists
    if not (frontend_dir / "index.html").exists():
        click.secho(f"Error: index.html does not exist: {frontend_dir / 'index.html'}", fg="red")
        if web_server_process:
            web_server_process.terminate()
        return
    
    # Set GUI port (try other ports if occupied)
    gui_port_start = gui_port
    gui_started = False
    while gui_port < gui_port_start + 20:  # Try 20 ports
        try:
            # Create custom request handler
            class Handler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=str(frontend_dir), **kwargs)
                
                def end_headers(self):
                    # Add CORS headers
                    self.send_header("Access-Control-Allow-Origin", "*")
                    super().end_headers()
                
                def log_message(self, format, *args):
                    # Print request logs
                    click.echo(f"[{self.log_date_time_string()}] {format % args}")
                
                def do_GET(self):
                    # If requesting root path, ensure returning index.html
                    if self.path == "/":
                        self.path = "/index.html"
                    elif not Path(frontend_dir / self.path.lstrip("/")).exists():
                        # If file doesn't exist, return index.html (for frontend routing)
                        self.path = "/index.html"
                    return super().do_GET()
            
            # Create server
            with socketserver.TCPServer(("", gui_port), Handler) as httpd:
                url = f"http://localhost:{gui_port}/"
                click.secho(f"✓ GUI interface server started: {url}", fg="green")
                click.echo("Press Ctrl+C to stop all servers")
                gui_started = True
                
                # Open in browser
                webbrowser.open(url)
                
                # Start server
                try:
                    httpd.serve_forever()
                except KeyboardInterrupt:
                    click.echo("\nShutting down servers...")
                    httpd.shutdown()
                    httpd.server_close()
                    click.echo("GUI server closed")
            break
        except socket.error:
            gui_port += 1
    
    # If GUI server failed to start, clean up Web server process
    if not gui_started:
        click.secho(f"Error: Cannot find available port (tried {gui_port_start}-{gui_port_start+19})", fg="red")
        if web_server_process:
            click.echo("Closing Web API server...")
            web_server_process.terminate()
            try:
                web_server_process.wait(timeout=5)
                click.echo("Web API server closed")
            except subprocess.TimeoutExpired:
                click.secho("Forcing Web API server shutdown...", fg="yellow")
                web_server_process.kill()
                web_server_process.wait()
                click.echo("Web API server forcibly closed")
        return
    
    # Close Web server process (only if it's our process)
    if web_server_process:
        click.echo("Closing Web API server...")
        web_server_process.terminate()
        try:
            web_server_process.wait(timeout=5)
            click.echo("Web API server closed")
        except subprocess.TimeoutExpired:
            click.secho("Forcing Web API server shutdown...", fg="yellow")
            web_server_process.kill()
            web_server_process.wait()
            click.echo("Web API server forcibly closed")


if __name__ == "__main__":
    cli_app()
    