#!/usr/bin/env python3
import os
import sys

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
sys.stderr.reconfigure(line_buffering=True)

print("=" * 50, flush=True)
print("PHILIA THRIFTS BOT STARTING", flush=True)
print("=" * 50, flush=True)
print(f"Python version: {sys.version}", flush=True)
print(f"Working dir: {os.getcwd()}", flush=True)
print(f"PORT env var: {os.environ.get('PORT', 'NOT SET')}", flush=True)
print(f"All env vars: {dict(os.environ)}", flush=True)

try:
    port = int(os.environ.get("PORT", "8080"))
    print(f"Using port: {port}", flush=True)
    
    print("Importing uvicorn...", flush=True)
    import uvicorn
    
    print("Starting uvicorn...", flush=True)
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
    
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
