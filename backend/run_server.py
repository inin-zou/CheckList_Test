"""Direct server startup script to diagnose uvicorn hanging issue."""
import sys
sys.path.insert(0, 'src')

print("Starting server...")
import uvicorn
from src.main import app

if __name__ == "__main__":
    print("Running uvicorn...")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
