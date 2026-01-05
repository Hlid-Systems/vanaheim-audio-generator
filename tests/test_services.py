import pytest
import os
import json
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from app.services.script_service import ScriptService
from app.services.audio_service import AudioService
from app.schemas.simulation import SimulationRequest, ScriptSegment

# --- ScriptService Tests ---
@pytest.mark.anyio
async def test_generate_script_success():
    mock_segments = [
        {"voice": "es-ES", "role": "Dev", "name": "Pepe", "text": "Hola"}
    ]
    mock_response = MagicMock()
    mock_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps(mock_segments)))
    ]
    
    with patch("app.services.script_service.AsyncOpenAI") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.chat.completions.create = AsyncMock(return_value=mock_response)
        
        service = ScriptService()
        req = SimulationRequest(participants=2, duration_minutes=1, topic="Test", context="Ctx")
        
        result = await service.generate_script(req)
        
        assert len(result) == 1
        assert result[0].name == "Pepe"

# --- AudioService Tests ---
@pytest.mark.anyio
async def test_audio_service_full_flow():
    """Test process_script calling generate_segment_audio and concatenate."""
    segments = [ScriptSegment(voice="v1", role="r1", name="n1", text="t1")]
    
    # Mock EdgeTTS to avoid network/file creation
    with patch("app.services.audio_service.edge_tts.Communicate") as MockComm:
        mock_comm_instance = MockComm.return_value
        mock_comm_instance.save = AsyncMock()
        
        # Mock File operations to avoid disk usage
        with patch("builtins.open", mock_open()), \
             patch("shutil.copyfileobj"), \
             patch("os.makedirs"), \
             patch("shutil.rmtree"), \
             patch("os.path.exists", return_value=False):
            
            service = AudioService()
            output = await service.process_script(segments, "final_test.mp3")
            
            # Verifications
            assert "final_test.mp3" in output
            # Check if edge_tts was called (means generate_segment_audio was executed)
            MockComm.assert_called() 
            mock_comm_instance.save.assert_called()