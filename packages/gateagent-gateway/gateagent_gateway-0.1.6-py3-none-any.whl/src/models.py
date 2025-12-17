# gate/ext/models.py

from typing import Optional, TypedDict, List
from pydantic import BaseModel

class TrackEvent(TypedDict):
    event: str             # "start" or "end"
    agent: str
    action: str
    timestamp: float       # UNIX epoch
    success: Optional[bool]
    affected_apps: Optional[List[str]]
    

class StoredEvent(TypedDict):
    id: int
    event: str
    agent: str
    action: str
    timestamp: float
    success: Optional[bool]
    created_at: str
    affected_apps: List[str]

class AgentRegistration(BaseModel):
    name: str
