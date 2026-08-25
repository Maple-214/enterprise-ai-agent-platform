export type ConversationStatus = 'active' | 'archived';
export type RunStatus = 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';

export interface Conversation {
  id: string;
  title: string;
  agent_id: string;
  status: ConversationStatus;
  is_pinned: boolean;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  run_id?: string | null;
  role: 'user' | 'assistant' | 'tool' | 'system';
  content: string;
  created_at: string;
}

export interface Run {
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
}

export type AgentEventType =
  | 'run.started'
  | 'message.delta'
  | 'tool.started'
  | 'tool.completed'
  | 'citation.created'
  | 'approval.required'
  | 'run.completed'
  | 'run.failed';

export interface AgentEvent {
  type: AgentEventType;
  run_id: string;
  content?: string;
  tool_name?: string;
  result?: string;
  source?: string;
  score?: number;
  approval_id?: string;
  message?: string;
  trace_id?: string;
}
