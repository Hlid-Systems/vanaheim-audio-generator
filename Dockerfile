FROM python:3.11-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Poetry
RUN pip install poetry
COPY pyproject.toml poetry.lock* ./
COPY README.md ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# Application Code
COPY app ./app
RUN mkdir data

EXPOSE 8000

# Dynamic Port Binding
CMD ["sh", "-c", "uvicorn app.infrastructure.api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]