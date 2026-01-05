# Simulation Audio Generator

A professional microservice designed to generate realistic corporate team audio simulations. It combines **LLM-based Script Generation** (OpenAI) with **High-Quality Text-to-Speech** (EdgeTTS).

## Features

- **Dynamic Script Generation**: Creates unique scenarios based on topic, context, and participant count.
- **Realistic Voice Synthesis**: Uses neural voices to assign distinct personalities to roles (Lead, PO, Engineers).
- **Clean Architecture**: Built with FastAPI, adhering to separation of concerns.
- **Type Safety**: Fully typed with Pydantic.
- **Structured Logging**: Production-ready logging configuration.

## Prerequisites

- Python 3.9+
- Poetry (Dependency Manager)
- OpenAI API Key

## Installation

1.  **Install Dependencies**:
    ```bash
    poetry install
    ```
2.  **Environment Setup**:
    Create a `.env` file:
    ```ini
    OPENAI_API_KEY=sk-your-key
    ```

## Usage

### Running the Server
```bash
poetry run uvicorn app.main:app --reload
```
The API will be available at `http://localhost:8000`.
Documentation: `http://localhost:8000/docs`.

### Running Tests
This project includes a robust test suite with **Code Coverage**.
The `pytest.ini` file defines standard configuration (paths, async mode).

```bash
# Run tests and view coverage report
poetry run pytest --cov=app --cov-report=term
```

### File Conventions
Generated files (Script and Audio) follow the format: `{ShortID}_p{Participants}_t{Duration}m.[json|mp3]`
Example: `a1b2_p4_t5m.mp3`

### Logs
Structured logging is implemented in `app/core/logging.py`. Logs are output to the console.

### API Endpoints

#### 1. Generate New Simulation
`POST /api/v1/simulation/generate`

Generates a script from scratch and then the audio.

**Payload:**
```json
{
  "participants": 4,
  "duration_minutes": 2,
  "topic": "Project Post-Mortem",
  "context": "The team missed the Q3 deadline due to unexpected integration issues."
}
```

#### 2. Generate Audio from Existing Script
`POST /api/v1/simulation/audio-only`

**Payload:**
```json
{
  "script_name": "generated_script_name",
  "output_filename": "optional_custom_name.mp3"
}
```

#### 3. Upload Script File
`POST /api/v1/simulation/audio-from-file`
Upload a `.json` file via form-data (`key="file"`).

#### 4. Paste Script JSON
`POST /api/v1/simulation/audio-from-json`
Paste the raw segment list in the request body.