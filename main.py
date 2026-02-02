#!/usr/bin/env python3
import os
import sys

print("=== PHILIA THRIFTS BOT ===", flush=True)
print(f"Args: {sys.argv}", flush=True)
print(f"PORT: {os.environ.get('PORT', 'NOT SET')}", flush=True)

try:
    port = int(os.environ.get("PORT", "8080"))
    print(f"Starting on port {port}", flush=True)
    
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
except Exception as e:
    print(f"ERROR: {e}", flush=True)
    import traceback
    traceback.print_exc()
    sys.exit(1)
