#!/usr/bin/env python3
"""
Simple local runner for TTS system without Docker
"""
import subprocess
import sys
import os
import time
from pathlib import Path

def install_requirements():
    """Install requirements for all engines"""
    engines = ['kokkoro', 'chatterbox', 'coqui', 'gateway']
    
    for engine in engines:
        req_file = Path(f"engines/{engine}/requirements.txt") if engine != 'gateway' else Path("gateway/requirements.txt")
        if req_file.exists():
            print(f"Installing requirements for {engine}...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(req_file)], check=True)

def run_engine(engine_name, port, engine_dir):
    """Run a single engine"""
    app_file = Path(engine_dir) / "app.py"
    if not app_file.exists():
        print(f"Error: {app_file} not found")
        return None
    
    print(f"Starting {engine_name} on port {port}...")
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "app:app", 
        "--host", "0.0.0.0", 
        "--port", str(port)
    ], cwd=engine_dir)

def main():
    print("TTS System Local Runner")
    print("======================")
    
    # Install requirements
    try:
        install_requirements()
    except subprocess.CalledProcessError as e:
        print(f"Failed to install requirements: {e}")
        return
    
    # Start engines
    processes = []
    
    engines = [
        ("kokkoro", 8001, "engines/kokkoro"),
        ("chatterbox", 8002, "engines/chatterbox"), 
        ("coqui", 8003, "engines/coqui"),
        ("gateway", 8000, "gateway")
    ]
    
    for name, port, directory in engines:
        if Path(directory).exists():
            proc = run_engine(name, port, directory)
            if proc:
                processes.append((name, proc))
                time.sleep(2)  # Give each service time to start
    
    print("\nServices started:")
    print("- Gateway: http://localhost:8000")
    print("- Kokkoro: http://localhost:8001") 
    print("- Chatterbox: http://localhost:8002")
    print("- Coqui: http://localhost:8003")
    print("\nPress Ctrl+C to stop all services")
    
    try:
        # Wait for all processes
        for name, proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        print("\nStopping services...")
        for name, proc in processes:
            proc.terminate()
            print(f"Stopped {name}")

if __name__ == "__main__":
    main()