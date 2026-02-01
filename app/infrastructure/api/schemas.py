from pydantic import BaseModel
from typing import Optional

class GenerationResponse(BaseModel):
    job_id: str
    status: str
    message: str
    output_file: Optional[str] = None
