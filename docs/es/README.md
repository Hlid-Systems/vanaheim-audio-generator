
[🇺🇸 English Version](../../README.md)

# 🔊 Vanaheim Audio Generator (Hlid Systems)

![License](https://img.shields.io/github/license/Hlid-Systems/vanaheim-audio-generator?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Architecture](https://img.shields.io/badge/Arquitectura-Hexagonal-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Estado-V1.0_Gold-success?style=for-the-badge)

Un microservicio profesional de síntesis de audio impulsado por **Hlid Systems**. Bajo el nombre clave **Vanaheim**, está diseñado para desarrolladores, creadores y equipos, combinando **Generación de Guiones basada en LLM** (OpenAI) con **Síntesis de Voz de Alta Calidad** (EdgeTTS) para crear simulaciones de voz realistas.

---

## ✨ Características

- **🎭 Generación Dinámica de Guiones**: Crea escenarios únicos basados en el tema, contexto y número de participantes.
- **🗣️ Síntesis de Voz Realista**: Utiliza voces neurales para asignar personalidades distintas a cada rol (Líder, Product Owner, Ingenieros).
- **🏗️ Arquitectura Limpia**: Construido con FastAPI, siguiendo estrictamente la separación de responsabilidades (Arquitectura Hexagonal).
- **🛡️ Protocolo Munin**: Integración opcional con Supabase para auditoría y persistencia de datos.
- **🐳 Despliegue Flexible**: Ejecute vía Poetry (Local) o Docker (Contenedor).

---

## 🌍 Configuración del Entorno

La aplicación puede ejecutarse en **modo mixto**.

1.  **Configuración Simple (Opcional)**: Si solo usas `/tts/simple` (TTS Directo), **NO requieres archivo .env**.
2.  **Poder Total (Recomendado)**: Para generación con IA y persistencia, crea un archivo `.env`:

```ini
# Requerido para Generación de Guiones IA (Server-side default)
# Si no se configura aquí, DEBES enviarlo vía header X-OpenAI-Key en las peticiones.
OPENAI_API_KEY=sk-tu-clave-aqui

# Opcional: Persistencia con Supabase (Auditoría Munin)
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-clave-secreta
```

### 🧠 Modelos de IA Soportados
Puedes seleccionar el modelo en las peticiones (`/ai/prompt`, `/simulation/scenario`).
- `gpt-5.2-pro` (Futuro/Placeholder)
- `gpt-4.1`
- `gpt-4-turbo` (Default recomendado)
- `gpt-4`
- `gpt-3.5-turbo`

---

## ⚙️ Instalación y Ejecución

Tienes dos formas profesionales de ejecutar Vanaheim.

### 🐍 Opción A: Desarrollo Local (Poetry)
Ideal para programar y depurar.

1.  **Instalar Dependencias**:
    ```bash
    poetry env use python3.11   # Forzar Python 3.11
    poetry install
    ```
2.  **Ejecutar Servidor**:
    ```bash
    # Activa el entorno virtual implícitamente
    poetry run uvicorn app.main:app --reload
    ```

### 🐳 Opción B: Docker (Producción/Limpio)
Ideal para despliegue o pruebas aisladas.

```bash
# Construir y Ejecutar
docker-compose up --build
```
El servicio estará disponible en `http://localhost:8000`.

---

## 📡 Endpoints de la API y Uso

Documentación Interactiva: `http://localhost:8000/docs`

### 1. 🆓 Modo Gratuito (TTS Directo)
*   **Endpoint**: `POST /api/v1/tts/simple`
*   **Auth**: No requerida.
*   **Respuesta**: **Descarga de Audio Directa** (Stream MP3).
*   **Uso**: Texto a voz rápido sin procesamiento de IA.

### 2. 👨‍💻 Modo Desarrollador (Prompt)
*   **Endpoint**: `POST /api/v1/ai/prompt`
*   **Auth**: Requiere header `X-OpenAI-Key` O variable de entorno `OPENAI_API_KEY`.
*   **Respuesta**: **Descarga de Audio Directa** (Stream MP3).
    *   *Metadatos (Job ID, Script Preview)* incluidos en Headers de respuesta (`X-Vanaheim-Job-Id`).
*   **Funciones**: Convierte una instrucción libre (ej: "Dos piratas discutiendo sobre pizza") en guión y audio.

### 3. 🎬 Modo Escenario (Simulación)
*   **Endpoint**: `POST /api/v1/simulation/scenario`
*   **Auth**: Requiere header `X-OpenAI-Key` O variable de entorno `OPENAI_API_KEY`.
*   **Respuesta**: **Descarga de Audio Directa** (Stream MP3).
    *   *Metadatos (Job ID, Participantes)* incluidos en Headers de respuesta.
*   **Funciones**: Simulaciones estructuradas (Corporativo, Podcast) con control preciso de tiempos.

---

## 🧪 Pruebas y Calidad

Mantenemos un alto estándar de calidad de código (Cobertura > 80%).

```bash
# Ejecutar Tests Unitarios y de Integración
poetry run pytest
```

---

## 🛡️ Protocolo Munin (Persistencia de Datos)

Si `SUPABASE_URL` está configurado, el sistema registra automáticamente las simulaciones en tu base de datos para auditoría.

**Nota sobre el Esquema de BD**:
Asegúrate de que tu tabla `vanaheim_audio` tenga las siguientes columnas para evitar advertencias:
- `configuration` (JSONB): Almacena configuración de modelos/voces.
- `script_content` (Text): Almacena el guión generado completo.

---

## ⚖️ Licencia
[MIT © Hlid Systems](LICENSE)