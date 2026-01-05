import pytest
from pydantic import ValidationError
from app.schemas.simulation import SimulationRequest, ScriptSegment

def test_simulation_request_valid():
    req = SimulationRequest(
        participants=4, 
        duration_minutes=10, 
        topic="Scrum", 
        context="Daily"
    )
    assert req.participants == 4

def test_simulation_request_invalid_participants():
    with pytest.raises(ValidationError):
        SimulationRequest(participants=0, duration_minutes=10, topic="A", context="B")

def test_simulation_request_invalid_duration():
    with pytest.raises(ValidationError):
        SimulationRequest(participants=2, duration_minutes=300, topic="A", context="B")

def test_script_segment_valid():
    seg = ScriptSegment(
        voice="voice-id",
        role="Dev",
        name="Juan",
        text="Hello"
    )
    assert seg.name == "Juan"