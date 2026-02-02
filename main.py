#!/usr/bin/env python3
import os
import sys

# Print immediately
os.write(1, b"=== PHILIA THRIFTS BOT STARTING ===\n")
os.write(1, f"Python: {sys.version}\n".encode())
os.write(1, f"Args: {sys.argv}\n".encode())

try:
    os.write(1, b"Getting PORT...\n")
    port = int(os.environ.get("PORT", "8080"))
    os.write(1, f"Port: {port}\n".encode())
    
    os.write(1, b"Importing uvicorn...\n")
    import uvicorn
    
    os.write(1, b"Starting uvicorn...\n")
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
    
except Exception as e:
    os.write(2, f"ERROR: {e}\n".encode())
    import traceback
    os.write(2, traceback.format_exc().encode())
    sys.exit(1)
