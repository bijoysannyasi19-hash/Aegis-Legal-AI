from pydantic import BaseModel, Field
from typing import List, Dict, Any

class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Unique identifier for the chat/redlining session tracking")
    prompt: str = Field(..., description="User's contextual prompt or editing instruction")

class ChatResponse(BaseModel):
    draft: str
    sources: List[Dict[str, Any]]

class AuditRequest(BaseModel):
    draft: str = Field(..., description="The generated legal text to be automatically audited")

class Risk(BaseModel):
    risk_level: str
    issue: str
    fix: str

class AuditResponse(BaseModel):
    risks: List[Risk]
