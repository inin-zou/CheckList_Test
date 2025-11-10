import modal
from src.main import app as fastapi_app

# Create Modal app
app = modal.App("checklist-api")

# Create Modal image with dependencies
image = modal.Image.debian_slim().pip_install_from_requirements("requirements.txt")


@app.function(
    image=image,
    secrets=[modal.Secret.from_name("checklist-secrets")],
)
@modal.asgi_app()
def fastapi_wrapper():
    """Modal ASGI wrapper for FastAPI app"""
    return fastapi_app
