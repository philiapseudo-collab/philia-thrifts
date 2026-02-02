import os
import sys
import uvicorn

print("=== PHILIA THRIFTS BOT STARTING ===", flush=True)
print(f"Python: {sys.executable}", flush=True)
print(f"PORT env: {os.environ.get('PORT', 'NOT SET')}", flush=True)

port = int(os.environ.get("PORT", "8080"))
print(f"Using port: {port}", flush=True)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)
