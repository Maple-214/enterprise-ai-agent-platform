import type { Agent, AgentEvent, Approval, Conversation, ConversationListResponse, Document, Message, Run, User } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const token = localStorage.getItem('agent_access_token');
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(init?.headers ?? {}),
    },
  });
  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `请求失败：${response.status}`);
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export async function login(email: string, password: string) {
  return apiFetch<{ access_token: string; user: User }>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
}
export async function getMe() { return apiFetch<User>('/auth/me'); }
export async function listAgents() { return apiFetch<Agent[]>('/agents'); }
export async function listConversations(params?: { q?: string; page?: number; page_size?: number; status?: 'active' | 'archived' }) {
  const search = new URLSearchParams();
  if (params?.q) search.set('q', params.q);
  if (params?.page) search.set('page', String(params.page));
  if (params?.page_size) search.set('page_size', String(params.page_size));
  if (params?.status) search.set('status', params.status);
  const query = search.toString();
  return apiFetch<ConversationListResponse>(`/conversations${query ? `?${query}` : ''}`);
}
export async function createConversation(agentId: string, title = '新对话') {
  return apiFetch<Conversation>('/conversations', { method: 'POST', body: JSON.stringify({ agent_id: agentId, title }) });
}
export async function getConversation(conversationId: string) {
  return apiFetch<{ conversation: Conversation; messages: Message[] }>(`/conversations/${conversationId}`);
}
export async function getMessages(conversationId: string) { return apiFetch<Message[]>(`/conversations/${conversationId}/messages`); }
export async function updateConversation(conversationId: string, payload: { title?: string; is_pinned?: boolean; status?: 'active' | 'archived' }) {
  return apiFetch<Conversation>(`/conversations/${conversationId}`, { method: 'PATCH', body: JSON.stringify(payload) });
}
export async function deleteConversation(conversationId: string) { return apiFetch<void>(`/conversations/${conversationId}`, { method: 'DELETE' }); }
export async function archiveConversation(conversationId: string) { return apiFetch<Conversation>(`/conversations/${conversationId}/archive`, { method: 'POST' }); }
export async function restoreConversation(conversationId: string) { return apiFetch<Conversation>(`/conversations/${conversationId}/restore`, { method: 'POST' }); }
export async function pinConversation(conversationId: string) { return apiFetch<Conversation>(`/conversations/${conversationId}/pin`, { method: 'POST' }); }
export async function unpinConversation(conversationId: string) { return apiFetch<Conversation>(`/conversations/${conversationId}/pin`, { method: 'DELETE' }); }
export async function clearConversationMessages(conversationId: string) { return apiFetch<void>(`/conversations/${conversationId}/messages`, { method: 'DELETE' }); }
export async function getRun(runId: string) { return apiFetch<Run>(`/runs/${runId}`); }
export async function getRunEvents(runId: string) { return apiFetch<Array<{ id: string; run_id: string; event_type: string; payload: Record<string, unknown>; sequence: number; created_at: string }>>(`/runs/${runId}/events`); }
export async function cancelRun(runId: string) { return apiFetch<Run>(`/runs/${runId}/cancel`, { method: 'POST' }); }

export function createRunStream(conversationId: string, content: string, onEvent: (event: AgentEvent) => void) {
  const token = localStorage.getItem('agent_access_token');
  const controller = new AbortController();
  fetch(`${API_BASE_URL}/runs/conversations/${conversationId}/stream`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    body: JSON.stringify({ content }),
    signal: controller.signal,
  }).then(async (response) => {
    if (!response.ok || !response.body) {
      onEvent({ type: 'run.failed', run_id: '', conversation_id: conversationId, message: await response.text() });
      return;
    }
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const frames = buffer.split('\n\n');
      buffer = frames.pop() ?? '';
      for (const frame of frames) {
        const line = frame.split('\n').find((item) => item.startsWith('data:'));
        if (!line) continue;
        try { onEvent(JSON.parse(line.slice(5).trim()) as AgentEvent); } catch { /* 忽略无效事件 */ }
      }
    }
  }).catch((error: unknown) => {
    if ((error as DOMException).name !== 'AbortError') onEvent({ type: 'run.failed', run_id: '', conversation_id: conversationId, message: String(error) });
  });
  return controller;
}

export async function listDocuments() { return apiFetch<Document[]>('/knowledge/documents'); }
export async function uploadDocument(file: File) {
  const token = localStorage.getItem('agent_access_token');
  const form = new FormData(); form.append('file', file);
  const response = await fetch(`${API_BASE_URL}/knowledge/documents`, { method: 'POST', headers: token ? { Authorization: `Bearer ${token}` } : {}, body: form });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<Document>;
}
export async function listApprovals() { return apiFetch<Approval[]>('/approvals'); }
export async function resolveApproval(id: string, decision: 'approve' | 'reject') { return apiFetch(`/approvals/${id}/resolve`, { method: 'POST', body: JSON.stringify({ decision }) }); }
