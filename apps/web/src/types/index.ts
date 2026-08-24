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

export type Conversation = {
  id: string;
  title: string;
  agent_id: string;
  updated_at: string;
};

export type Message = {
  id: string;
  role: 'user' | 'assistant' | 'tool' | 'system';
  content: string;
  created_at: string;
};

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

export type AgentEvent =
  | { type: 'run.started'; run_id: string }
  | { type: 'message.delta'; content: string }
  | { type: 'tool.started'; tool_name: string }
  | { type: 'tool.completed'; tool_name: string; result: string }
  | { type: 'citation.created'; source: string; score: number }
  | { type: 'approval.required'; approval_id: string; tool_name: string }
  | { type: 'run.completed'; run_id: string }
  | { type: 'run.failed'; message: string };
