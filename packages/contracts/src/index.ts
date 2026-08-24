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
  run_id?: string;
  content?: string;
  tool_name?: string;
  result?: string;
  source?: string;
  score?: number;
  approval_id?: string;
  message?: string;
}
