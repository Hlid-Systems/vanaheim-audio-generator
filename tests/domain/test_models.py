import pytest
from app.domain.models import ScriptSegment, SimulationRequest, ScenarioType

def test_script_segment_creation():
    segment = ScriptSegment(
        voice="es-MX-DaliaNeural",
        role="Host",
        name="Dalia",
        text="Hola mundo"
    )
    assert segment.voice == "es-MX-DaliaNeural"
    assert segment.text == "Hola mundo"

def test_simulation_request_validation():
    # Valid
    req = SimulationRequest(
        participants=2,
        duration_minutes=5,
        topic="Test",
        context="Context",
        scenario=ScenarioType.PODCAST
    )
    assert req.participants == 2

    # Invalid (too few participants)
    with pytest.raises(ValueError):
         SimulationRequest(
            participants=1,
            duration_minutes=5,
            topic="Test",
            context="Context"
        )