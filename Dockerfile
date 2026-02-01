FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (if any needed for edge-tts, usually none)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml poetry.lock* ./
COPY README.md ./

# Install dependencies (without creating a virtualenv inside the container)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Copy app code
COPY app ./app
COPY data ./data

# Expose port
EXPOSE 8000

# Run commands
CMD ["uvicorn", "app.infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8000"]