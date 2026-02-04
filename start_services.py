#!/usr/bin/env python3
"""
Start both web server and Celery worker in the same container.
This simplifies Railway deployment by using a single service.
"""
import os
import sys
import subprocess
import signal
import time

# Configuration
PORT = int(os.environ.get("PORT", "8080"))

def start_celery():
    """Start Celery worker as a subprocess."""
    return subprocess.Popen(
        ["celery", "-A", "app.worker.celery_app", "worker", "--loglevel=info", "--concurrency=2"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

def start_web():
    """Start web server using uvicorn."""
    return subprocess.Popen(
        ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(PORT)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

def log_output(process, name):
    """Log output from a process."""
    for line in process.stdout:
        print(f"[{name}] {line}", end='')

def main():
    print("=== PHILIA THRIFTS BOT - Starting Services ===")
    print(f"Port: {PORT}")
    
    # Start Celery worker
    print("Starting Celery worker...")
    celery_process = start_celery()
    
    # Give Celery a moment to start
    time.sleep(2)
    
    # Start web server
    print("Starting web server...")
    web_process = start_web()
    
    # Import threading for logging
    import threading
    
    # Start log threads
    threading.Thread(target=log_output, args=(celery_process, "WORKER"), daemon=True).start()
    threading.Thread(target=log_output, args=(web_process, "WEB"), daemon=True).start()
    
    print("\n=== Both services started ===")
    print("Web: http://0.0.0.0:{}".format(PORT))
    print("Celery: Processing tasks...")
    
    # Wait for processes
    try:
        while True:
            # Check if processes are still running
            celery_status = celery_process.poll()
            web_status = web_process.poll()
            
            if celery_status is not None:
                print(f"Celery exited with code {celery_status}")
                break
                
            if web_status is not None:
                print(f"Web server exited with code {web_status}")
                break
                
            time.sleep(1)
    
    except KeyboardInterrupt:
        print("\n=== Shutting down ===")
        celery_process.terminate()
        web_process.terminate()
        
        # Wait for graceful shutdown
        try:
            celery_process.wait(timeout=5)
            web_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            celery_process.kill()
            web_process.kill()
        
        print("Services stopped.")

if __name__ == "__main__":
    main()
