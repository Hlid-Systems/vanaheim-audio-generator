from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from fastapi import Response
from app.infrastructure.api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "operational"

@patch("app.infrastructure.api.v1.router.audio_service")
def test_simple_tts_endpoint(mock_audio_service):
    # Mock service to return a path
    mock_audio_service.generate_script_audio = AsyncMock(return_value="dummy.mp3")
    
    # Mock FileResponse to return a simple Response object with audio content
    with patch("app.infrastructure.api.v1.router.FileResponse") as mock_file_response:
        mock_file_response.side_effect = lambda path, **kwargs: Response(content=b"fake-audio-bytes", media_type="audio/mpeg")
        
        payload = {
            "text": "Hello World",
            "voice": "en-US-AriaNeural"
        }
        
        response = client.post("/api/v1/tts/simple", json=payload)
        
        assert response.status_code == 200
        assert response.content == b"fake-audio-bytes"
        assert response.headers["content-type"] == "audio/mpeg"