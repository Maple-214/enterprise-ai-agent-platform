from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

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
    title: str = Field(default="新对话", min_length=1, max_length=200)

class ConversationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    is_pinned: bool | None = None
    status: str | None = Field(default=None, pattern="^(active|archived)$")

class RunSummaryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    status: str
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    agent_id: str
    status: str
    is_pinned: bool
    is_running: bool = False
    latest_run: RunSummaryOut | None = None
    created_at: datetime
    updated_at: datetime

class ConversationListResponse(BaseModel):
    items: list[ConversationOut]
    page: int
    page_size: int
    total: int
    has_next: bool

class ConversationDetailResponse(BaseModel):
    conversation: ConversationOut
    messages: list['MessageOut']

class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    conversation_id: str
    run_id: str | None = None
    role: str
    content: str
    created_at: datetime

class ChatRequest(BaseModel):
    conversation_id: str
    content: str = Field(min_length=1, max_length=20000)

class RunCreate(BaseModel):
    content: str = Field(min_length=1, max_length=20000)

class RunOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    conversation_id: str
    agent_id: str
    status: str
    input_text: str
    model: str
    trace_id: str
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime

class RunEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    run_id: str
    event_type: str
    payload: dict
    sequence: int
    created_at: datetime

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
