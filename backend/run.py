#!/usr/bin/env python3
"""
HR Avatar Backend Runner

Simple script to run the FastAPI application.
Usage:
    python run.py              # Run in production mode
    python run.py --dev        # Run in development mode with hot reload
    python run.py --port 8080  # Run on custom port
"""

import argparse
import uvicorn
import os
import sys
from dotenv import load_dotenv

load_dotenv(override=True)

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings


def main():
    parser = argparse.ArgumentParser(description="Run HR Avatar Backend")
    parser.add_argument(
        "--dev", 
        action="store_true", 
        help="Run in development mode with hot reload"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=8000, 
        help="Port to run the server on (default: 8000)"
    )
    parser.add_argument(
        "--host", 
        type=str, 
        default="0.0.0.0", 
        help="Host to bind the server to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--workers", 
        type=int, 
        default=1, 
        help="Number of worker processes (default: 1)"
    )
    parser.add_argument(
        "--ssl", 
        action="store_true", 
        help="Enable HTTPS with SSL certificates"
    )
    parser.add_argument(
        "--ssl-key", 
        type=str, 
        default="private.key", 
        help="Path to SSL private key file (default: private.key)"
    )
    parser.add_argument(
        "--ssl-cert", 
        type=str, 
        default="certificate.crt", 
        help="Path to SSL certificate file (default: certificate.crt)"
    )
    
    args = parser.parse_args()
    
    # Check SSL files if SSL is enabled
    if args.ssl:
        if not os.path.exists(args.ssl_key):
            print(f"❌ SSL key file not found: {args.ssl_key}")
            sys.exit(1)
        if not os.path.exists(args.ssl_cert):
            print(f"❌ SSL certificate file not found: {args.ssl_cert}")
            sys.exit(1)
    
    # Print startup info
    print("=" * 50)
    print("HR Avatar Backend")
    print("=" * 50)
    print(f"Mode: {'Development' if args.dev else 'Production'}")
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Protocol: {'HTTPS' if args.ssl else 'HTTP'}")
    print(f"Debug: {settings.DEBUG}")
    print(f"Workers: {args.workers}")
    if args.ssl:
        print(f"SSL Key: {args.ssl_key}")
        print(f"SSL Cert: {args.ssl_cert}")
    print("=" * 50)
    
    # Configure uvicorn settings
    uvicorn_config = {
        "app": "app.main:app",
        "host": args.host,
        "port": args.port,
        "log_level": "info"
    }
    
    # Add SSL configuration if enabled
    if args.ssl:
        uvicorn_config.update({
            "ssl_keyfile": args.ssl_key,
            "ssl_certfile": args.ssl_cert
        })
    
    if args.dev or settings.DEBUG:
        # Development mode with hot reload
        uvicorn_config.update({
            "reload": True,
            "reload_dirs": ["app"],
            "log_level": "debug"
        })
        print("Starting in development mode with hot reload...")
    else:
        # Production mode
        if args.workers > 1:
            uvicorn_config["workers"] = args.workers
        print("Starting in production mode...")
    
    try:
        uvicorn.run(**uvicorn_config)
    except KeyboardInterrupt:
        print("\nShutdown requested by user")
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()