import pytest
from unittest.mock import AsyncMock, MagicMock
from app.domain.models import SimulationRequest, ScriptSegment, Script, ScenarioType
from app.application.services.script_generator import ScriptGenerationService
from app.application.services.audio_generator import AudioGenerationService
import unittest.mock
import os

@pytest.mark.asyncio
async def test_script_generation_flow_v2():
    # Mock LLM Provider
    mock_llm = MagicMock()
    # Return a JSON string that matches the expected structure including 'name'
    mock_llm.generate_text = AsyncMock(return_value='{"segments": [{"voice": "v1", "role": "r1", "name": "n1", "text": "test"}]}')
    
    service = ScriptGenerationService(mock_llm)
    req = SimulationRequest(
        participants=2, 
        duration_minutes=1, 
        topic="T", 
        context="C", 
        scenario=ScenarioType.CORPORATE
    )
    
    script = await service.generate_script(req)
    
    assert isinstance(script, Script)
    # logic produces multiple segments due to loop, at least 1
    assert len(script.segments) >= 1
    assert script.segments[0].text == "test"
    assert script.segments[0].name == "n1"

@pytest.mark.asyncio
async def test_audio_generation_flow_v2():
    # Mock Ports
    mock_tts = MagicMock()
    mock_tts.generate_audio = AsyncMock(return_value="/tmp/seg1.mp3")
    
    # Mock Storage
    mock_storage = MagicMock()
    mock_storage.create_temp_dir = MagicMock(return_value="/tmp/test_dir")
    mock_storage.concatenate_files = AsyncMock(return_value="/out/final.mp3")
    mock_storage.cleanup_temp_dir = MagicMock()

    # AudioService now accepts cloud_storage (optional). pass None.
    service = AudioGenerationService(mock_tts, mock_storage, cloud_storage=None)
    
    # Patch settings.OUTPUT_DIR
    with unittest.mock.patch("app.application.services.audio_generator.settings") as mock_settings:
        mock_settings.OUTPUT_DIR = "/mock/output"
        
        script = Script(segments=[ScriptSegment(voice="v1", role="r1", name="n1", text="text")])
        result_path = await service.generate_script_audio(script, "final.mp3")
        
        expected_path = os.path.join("/mock/output", "final.mp3")
        assert result_path == expected_path
        mock_tts.generate_audio.assert_called_once()
        mock_storage.concatenate_files.assert_called_once()