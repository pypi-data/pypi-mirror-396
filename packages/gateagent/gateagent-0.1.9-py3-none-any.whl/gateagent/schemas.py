from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
import time
import uuid

class Interaction(BaseModel):
    """
    Represents a single execution of a tool.
    """
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: Optional[str] = None
    tool_name: str
    inputs: Dict[str, Any]
    outputs: Optional[Any] = None
    error: Optional[str] = None
    status: str = Field(..., pattern="^(success|error)$")
    
    start_time: float = Field(default_factory=time.time)
    end_time: Optional[float] = None
    duration_ms: Optional[float] = None
    
    parent_run_id: Optional[str] = None
    
    # Metadata about the agent/environment
    metadata: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True
