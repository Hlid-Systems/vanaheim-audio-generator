
[🇪🇸 Versión en Español](docs/es/README.md)

# 🔊 Vanaheim Audio Generator (Hlid Systems)

![License](https://img.shields.io/github/license/Hlid-Systems/vanaheim-audio-generator?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Architecture](https://img.shields.io/badge/Architecture-Hexagonal-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-V1.0_Gold-success?style=for-the-badge)

A professional audio synthesis microservice powered by **Hlid Systems**. Codenamed **Vanaheim**, it is designed for developers, creators, and teams, combining **LLM-based Script Generation** (OpenAI) with **High-Quality Text-to-Speech** (EdgeTTS) to create realistic voice simulations.

---

## ✨ Features

- **🎭 Dynamic Script Generation**: Creates unique scenarios based on topic, context, and participant count.
- **🗣️ Realistic Voice Synthesis**: Uses neural voices to assign distinct personalities to roles (Lead, PO, Engineers).
- **🏗️ Clean Architecture**: Built with FastAPI, adhering to separation of concerns (Hexagonal).
- **🛡️ Munin Protocol**: Optional Integration with Supabase for auditing and data persistence.
- **🐳 Flexible Deployment**: Run via Poetry (Local) or Docker (Containerized).

---

## 🌍 Environment Configuration

The application can run in **mixed mode**.

1.  **Simple Config (Optional)**: If you only use `/tts/simple` (Direct Text-to-Speech), **NO .env file is required**.
2.  **Full Power (Recommended)**: For AI generation and persistence, create a `.env` file:

```ini
# Required for AI Script Generation (Server-side default)
# If not set here, you MUST provide it via X-OpenAI-Key header in requests.
OPENAI_API_KEY=sk-your-key-here

# Optional: Supabase Persistence (Munin Audit)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-secret-key
```

### 🧠 Supported AI Models
You can select the model in requests (`/ai/prompt`, `/simulation/scenario`).
- `gpt-5.2-pro` (Future/Placeholder)
- `gpt-4.1`
- `gpt-4-turbo` (Recommended default)
- `gpt-4`
- `gpt-3.5-turbo`

---

## ⚙️ Installation & Running

You have two professional ways to run Vanaheim.

### 🐍 Option A: Local Development (Poetry)
Ideal for coding and debugging.

1.  **Install Dependencies**:
    ```bash
    poetry env use python3.11   # Force Python 3.11
    poetry install
    ```
2.  **Run Server**:
    ```bash
    # Activates virtualenv implicitly
    poetry run uvicorn app.main:app --reload
    ```

### 🐳 Option B: Docker (Production/Clean)
Ideal for deployment or testing in isolation.

```bash
# Build and Run
docker-compose up --build
```
The service will be available at `http://localhost:8000`.

---

## 📡 API Endpoints & Usage

Interactive Documentation: `http://localhost:8000/docs`

### 1. 🆓 Free Mode (Direct TTS)
*   **Endpoint**: `POST /api/v1/tts/simple`
*   **Auth**: None required.
*   **Response**: **Direct Audio Download** (Streamed MP3).
*   **Use Case**: Quick text-to-speech without AI processing.

### 2. 👨‍💻 Developer Mode (Prompt)
*   **Endpoint**: `POST /api/v1/ai/prompt`
*   **Auth**: Requires `X-OpenAI-Key` header OR server-side `OPENAI_API_KEY`.
*   **Response**: **Direct Audio Download** (Streamed MP3).
    *   *Metadata (Job ID, Script Preview)* included in Response Headers (`X-Vanaheim-Job-Id`).
*   **Features**: Converts a raw prompt (e.g., "Two pirates arguing about pizza") into a script and then audio.

### 3. 🎬 Scenario Mode (Simulation)
*   **Endpoint**: `POST /api/v1/simulation/scenario`
*   **Auth**: Requires `X-OpenAI-Key` header OR server-side `OPENAI_API_KEY`.
*   **Response**: **Direct Audio Download** (Streamed MP3).
    *   *Metadata (Job ID, Participants)* included in Response Headers.
*   **Features**: Structured simulation (Corporate, Podcast) with precise timing controls.

---

## 🧪 Testing & Quality

We maintain a high standard of code quality (Coverage > 80%).

```bash
# Run Unit & Integration Tests
poetry run pytest
```

---

## 🛡️ Munin Protocol (Data Persistence)

If `SUPABASE_URL` is configured, the system automatically logs simulations to your database for auditing.

**Note on Database Schema**:
Ensure your `vanaheim_audio` table has the following columns to avoid warnings:
- `configuration` (JSONB): Stores model/voice settings.
- `script_content` (Text): Stores the full generated script.

---

## ⚖️ License
[MIT © Hlid Systems](LICENSE)