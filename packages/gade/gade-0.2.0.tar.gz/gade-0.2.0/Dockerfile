FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir . fastapi uvicorn

# Expose port
EXPOSE 8000

# Run the API server
CMD ["python", "-m", "gade.api.server"]
