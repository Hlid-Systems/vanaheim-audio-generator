import pytest
import json
from httpx import AsyncClient
from app.main import app
from unittest.mock import AsyncMock, patch, mock_open
from app.schemas.simulation import ScriptSegment

@pytest.fixture
def anyio_backend():
    return 'asyncio'

@pytest.mark.anyio
async def test_root_redirect():
    """Test that root redirects to docs."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/docs"

@pytest.mark.anyio
async def test_generate_simulation():
    """Test the generation endpoint with mocked services and NO file writing."""
    
    # Mock data
    mock_segments = [
        ScriptSegment(voice="es-ES-AlvaroNeural", role="PO", name="Carlos", text="Hola test")
    ]
    mock_output_path = "data/output/mock_audio.mp3"

    # Patch ALL file system operations in endpoints.py
    with patch("app.services.script_service.ScriptService.generate_script", new_callable=AsyncMock) as mock_gen_script, \
         patch("app.services.audio_service.AudioService.process_script", new_callable=AsyncMock) as mock_proc_audio, \
         patch("builtins.open", mock_open()), \
         patch("json.dump"): # Mock json dumping prevents writing to the mocked open file
        
        mock_gen_script.return_value = mock_segments
        mock_proc_audio.return_value = mock_output_path

        payload = {
            "participants": 3,
            "duration_minutes": 2,
            "topic": "Test Topic",
            "context": "Test Context"
        }

        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/v1/simulation/generate", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["output_file"] == mock_output_path

@pytest.mark.anyio
async def test_upload_script_file():
    """Test generating audio from uploaded file."""
    mock_segments = [ScriptSegment(voice="v1", role="r1", name="n1", text="t1")]
    
    with patch("app.services.script_service.ScriptService.analyze_script", return_value=(2, 1)), \
         patch("app.api.v1.endpoints.audio_service.process_script", new_callable=AsyncMock) as mock_proc, \
         patch("builtins.open", mock_open()), \
         patch("json.dump"):
         
         mock_proc.return_value = "data/output/test.mp3"
         
         files = {'file': ('test.json', json.dumps([s.model_dump() for s in mock_segments]), 'application/json')}
         
         async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.post("/api/v1/simulation/audio-from-file", files=files)
            
         assert response.status_code == 200, f"Failed: {response.text}"
         assert response.json()["status"] == "success"