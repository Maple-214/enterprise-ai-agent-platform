from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    email: str
    display_name: str
    role: str
    tenant_id: str

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

class AgentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    description: str
    system_prompt: str
    model: str
    enabled_tools: list[str]

class ConversationCreate(BaseModel):
    agent_id: str
    title: str = "New Conversation"

class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    agent_id: str
    updated_at: datetime

class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    role: str
    content: str
    created_at: datetime

class ChatRequest(BaseModel):
    conversation_id: str
    content: str

class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    filename: str
    status: str
    created_at: datetime

class ApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    status: str
    tool_name: str
    reason: str
    created_at: datetime

class ApprovalResolve(BaseModel):
    decision: str
