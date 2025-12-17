#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
WebFLow Web Server Startup Script - Web Content Extraction API
"""

import os
import sys
import argparse
import signal
import socket
from pathlib import Path

# Add package root directory to Python path
package_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(package_root))
os.chdir(package_root)  # Change current working directory to package root

# Import server module
from server import create_app
import uvicorn

def is_port_in_use(port):
    """Check if port is already in use"""
    # Check IPv4 address
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            # 0.0.0.0 means all available network interfaces
            s.bind(('0.0.0.0', port))
            return False
        except socket.error:
            return True

def main():
    """Main function: parse arguments and start server"""
    parser = argparse.ArgumentParser(description="Start web content extraction API server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Server host address")
    parser.add_argument("--port", type=int, default=9000, help="Server port")
    parser.add_argument("--workers", type=int, default=1, help="Number of worker processes")
    parser.add_argument("--api-key", type=str, help="DeepSeek API key (optional, can also be set via environment variable)")
    
    args = parser.parse_args()
    
    # Check if port is in use
    if is_port_in_use(args.port):
        print(f"Error: Port {args.port} is already in use. Please choose another port or close the program using this port.")
        sys.exit(1)
    
    # Set environment variable
    if args.api_key:
        os.environ["DEEPSEEK_API_KEY"] = args.api_key
    
    # Output startup information
    print(f"Starting WebFLow web content extraction API server...")
    print(f"Server address: http://{args.host}:{args.port}")
    print(f"Number of worker processes: {args.workers}")
    
    # Register signal handler to ensure graceful shutdown
    def signal_handler(sig, frame):
        print("\nShutting down server...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create FastAPI application and start server
    try:
        app = create_app()
        uvicorn.run(
            app,
            host=args.host,
            port=args.port,
            workers=args.workers,
            limit_concurrency=100,
            limit_max_requests=10000,
        )
    except Exception as e:
        print(f"Error occurred while starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()