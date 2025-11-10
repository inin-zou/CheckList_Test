import modal
import sys
from pathlib import Path

# Create Modal app
app = modal.App("checklist-api")

# Create persistent volume for data storage
volume = modal.Volume.from_name("checklist-data", create_if_missing=True)

# Create Modal image with dependencies
image = (
    modal.Image.debian_slim()
    .pip_install_from_requirements("requirements.txt")
    .run_commands(
        "apt-get update",
        "apt-get install -y poppler-utils tesseract-ocr",  # For PDF processing
    )
)


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("checklist-secrets")],
    volumes={"/data": volume},
    memory=2048,  # 2GB RAM
    timeout=300,  # 5 minutes timeout
    min_containers=1,  # Keep 1 instance warm
)
@modal.asgi_app()
def fastapi_wrapper():
    """Modal ASGI wrapper for FastAPI app"""
    # Add src to Python path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    
    from src.main import app as fastapi_app
    return fastapi_app