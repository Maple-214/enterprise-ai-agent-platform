export type User = {
  id: string;
  email: string;
  display_name: string;
  role: string;
  tenant_id: string;
};

export type Agent = {
  id: string;
  name: string;
  description: string;
  system_prompt: string;
  model: string;
  enabled_tools: string[];
};

export type RunStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';

export type RunSummary = {
  id: string;
  status: RunStatus;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
};

export type Conversation = {
  id: string;
  title: string;
  agent_id: string;
  status: 'active' | 'archived';
  is_pinned: boolean;
  is_running: boolean;
  latest_run: RunSummary | null;
  created_at: string;
  updated_at: string;
};

export type ConversationListResponse = {
  items: Conversation[];
  page: number;
  page_size: number;
  total: number;
  has_next: boolean;
};

export type Message = {
  id: string;
  conversation_id?: string;
  run_id?: string | null;
  role: 'user' | 'assistant' | 'tool' | 'system';
  content: string;
  created_at: string;
};

export type Run = {
  id: string;
  conversation_id: string;
  agent_id: string;
  status: RunStatus;
  input_text: string;
  model: string;
  trace_id: string;
  error_message: string | null;
  started_at: string | null;
  completed_at: string | null;
  created_at: string;
};

export type AgentEvent =
  | { type: 'run.started'; run_id: string; conversation_id: string; trace_id?: string }
  | { type: 'message.delta'; run_id: string; conversation_id: string; content: string }
  | { type: 'tool.started'; run_id: string; conversation_id: string; tool_name: string }
  | { type: 'tool.completed'; run_id: string; conversation_id: string; tool_name: string; result: string }
  | { type: 'citation.created'; run_id: string; conversation_id: string; source: string; score: number }
  | { type: 'approval.required'; run_id: string; conversation_id: string; approval_id: string; tool_name: string }
  | { type: 'run.completed'; run_id: string; conversation_id: string }
  | { type: 'run.failed'; run_id: string; conversation_id: string; message: string };

export type Document = {
  id: string;
  filename: string;
  status: string;
  created_at: string;
};

export type Approval = {
  id: string;
  status: string;
  tool_name: string;
  reason: string;
  created_at: string;
};
