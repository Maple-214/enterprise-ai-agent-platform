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
    throw new Error(message || `Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function login(email: string, password: string) {
  return apiFetch<{ access_token: string; user: import('../types').User }>('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ email, password }),
  });
}

export async function getMe() {
  return apiFetch<import('../types').User>('/auth/me');
}

export async function listAgents() {
  return apiFetch<import('../types').Agent[]>('/agents');
}

export async function listConversations() {
  return apiFetch<import('../types').Conversation[]>('/conversations');
}

export async function createConversation(agentId: string, title: string) {
  return apiFetch<import('../types').Conversation>('/conversations', {
    method: 'POST',
    body: JSON.stringify({ agent_id: agentId, title }),
  });
}

export async function getMessages(conversationId: string) {
  return apiFetch<import('../types').Message[]>(`/conversations/${conversationId}/messages`);
}

export async function listDocuments() {
  return apiFetch<import('../types').Document[]>('/knowledge/documents');
}

export async function uploadDocument(file: File) {
  const token = localStorage.getItem('agent_access_token');
  const form = new FormData();
  form.append('file', file);
  const response = await fetch(`${API_BASE_URL}/knowledge/documents`, {
    method: 'POST',
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: form,
  });
  if (!response.ok) throw new Error(await response.text());
  return response.json() as Promise<import('../types').Document>;
}

export async function listApprovals() {
  return apiFetch<import('../types').Approval[]>('/approvals');
}

export async function resolveApproval(id: string, decision: 'approve' | 'reject') {
  return apiFetch(`/approvals/${id}/resolve`, {
    method: 'POST',
    body: JSON.stringify({ decision }),
  });
}

export function createChatStream(conversationId: string, content: string, onEvent: (event: import('../types').AgentEvent) => void) {
  const token = localStorage.getItem('agent_access_token');
  const controller = new AbortController();

  fetch(`${API_BASE_URL}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({ conversation_id: conversationId, content }),
    signal: controller.signal,
  }).then(async (response) => {
    if (!response.ok || !response.body) {
      onEvent({ type: 'run.failed', message: await response.text() });
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const chunks = buffer.split('\n\n');
      buffer = chunks.pop() ?? '';

      for (const chunk of chunks) {
        const dataLine = chunk.split('\n').find((line) => line.startsWith('data:'));
        if (!dataLine) continue;
        try {
          const event = JSON.parse(dataLine.slice(5).trim()) as import('../types').AgentEvent;
          onEvent(event);
        } catch {
          // Ignore malformed keep-alive frames.
        }
      }
    }
  }).catch((error: unknown) => {
    if ((error as DOMException).name !== 'AbortError') {
      onEvent({ type: 'run.failed', message: String(error) });
    }
  });

  return controller;
}
