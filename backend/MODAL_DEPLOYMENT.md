# Modal Deployment Guide

## Prerequisites

1. Install Modal CLI:
```bash
pip install modal
```

2. Authenticate with Modal:
```bash
modal token new
```

## Required Secrets

You need to create a Modal secret named `checklist-secrets` with the following environment variables:

### Required Variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `ANTHROPIC_API_KEY`: Your Anthropic API key (for Claude)
- `WEAVIATE_URL`: Weaviate instance URL (use Modal's Weaviate or external service)
- `WEAVIATE_API_KEY`: Weaviate API key (if using cloud Weaviate)

### Optional Variables:
- `ALLOWED_ORIGINS`: Comma-separated list of CORS origins (default: http://localhost:3000,https://*.vercel.app)
- `OPENAI_MODEL`: OpenAI model to use (default: gpt-4-turbo-preview)
- `ANTHROPIC_MODEL`: Anthropic model to use (default: claude-3-5-sonnet-20241022)

## Creating Secrets

### Via Modal Dashboard:
1. Go to https://modal.com/secrets
2. Click "Create new secret"
3. Name it `checklist-secrets`
4. Add all required environment variables
5. Save the secret

### Via Modal CLI:
```bash
modal secret create checklist-secrets \
  OPENAI_API_KEY=sk-... \
  ANTHROPIC_API_KEY=sk-ant-... \
  WEAVIATE_URL=https://your-weaviate-instance.weaviate.network \
  WEAVIATE_API_KEY=your-weaviate-key
```

## Deployment Steps

1. Navigate to the backend directory:
```bash
cd backend
```

2. Deploy to Modal:
```bash
modal deploy src/modal_app.py
```

3. The deployment will:
   - Build a Docker image with all dependencies
   - Install system packages (poppler-utils, tesseract-ocr) for PDF processing
   - Create a persistent volume for data storage
   - Deploy the FastAPI application
   - Provide you with a public URL

## Testing the Deployment

After deployment, Modal will provide a URL like:
```
https://your-workspace--checklist-api-fastapi-wrapper.modal.run
```

Test the endpoints:
```bash
# Health check
curl https://your-url.modal.run/health

# Root endpoint
curl https://your-url.modal.run/
```

## Updating the Deployment

To update the deployment after making changes:
```bash
modal deploy src/modal_app.py
```

## Monitoring and Logs

View logs in real-time:
```bash
modal app logs checklist-api
```

Or visit the Modal dashboard: https://modal.com/apps

## Data Persistence

The application uses a persistent Modal Volume named `checklist-data` mounted at `/data`. This ensures:
- Uploaded files persist across deployments
- Database files are retained
- Vector store data is preserved

## Configuration Notes

- **Memory**: Set to 2GB RAM for handling PDF processing and embeddings
- **Timeout**: 5 minutes for long-running operations
- **Keep Warm**: 1 instance kept warm to reduce cold starts
- **Volumes**: `/data` volume for persistent storage

## Troubleshooting

### Common Issues:

1. **Import errors**: Ensure all dependencies are in `requirements.txt`
2. **Secret not found**: Verify the secret name is exactly `checklist-secrets`
3. **Permission errors**: Check that API keys have proper permissions
4. **Timeout errors**: Consider increasing the timeout value in `modal_app.py`

### Debug Mode:

Run in development mode to see detailed logs:
```bash
modal serve src/modal_app.py
```

This will give you a live-reloading development server with detailed logs.