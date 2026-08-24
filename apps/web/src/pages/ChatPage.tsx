import { useEffect, useMemo, useState } from 'react';
import { MessageSquare, Send } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { createChatStream, createConversation, getMessages, listAgents, listConversations } from '../lib/api';
import type { AgentEvent, Message } from '../types';

export function ChatPage() {
  const agentsQuery = useQuery({ queryKey: ['agents'], queryFn: listAgents });
  const conversationsQuery = useQuery({ queryKey: ['conversations'], queryFn: listConversations });
  const [conversationId, setConversationId] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [streaming, setStreaming] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState('');

  useEffect(() => {
    const firstAgent = agentsQuery.data?.[0];
    if (firstAgent && !selectedAgent) setSelectedAgent(firstAgent.id);
  }, [agentsQuery.data, selectedAgent]);

  const conversations = useMemo(() => conversationsQuery.data ?? [], [conversationsQuery.data]);

  async function ensureConversation() {
    if (conversationId) return conversationId;
    const conversation = conversations[0] ?? await createConversation(selectedAgent, 'New Agent Conversation');
    setConversationId(conversation.id);
    const existing = await getMessages(conversation.id);
    setMessages(existing);
    return conversation.id;
  }

  function appendAssistantDelta(delta: string) {
    setMessages(prev => {
      const last = prev[prev.length - 1];
      if (last?.role === 'assistant') return [...prev.slice(0, -1), { ...last, content: last.content + delta }];
      return [...prev, { id: `stream-${Date.now()}`, role: 'assistant', content: delta, created_at: new Date().toISOString() }];
    });
  }

  async function send() {
    if (!input.trim() || streaming) return;
    const content = input.trim();
    setInput('');
    const id = await ensureConversation();
    setMessages(prev => [...prev, { id: `user-${Date.now()}`, role: 'user', content, created_at: new Date().toISOString() }]);
    setStreaming(true);
    createChatStream(id, content, (event: AgentEvent) => {
      if (event.type === 'message.delta') appendAssistantDelta(event.content);
      if (event.type === 'tool.started') setMessages(prev => [...prev, { id: `tool-${Date.now()}`, role: 'tool', content: `正在调用工具：${event.tool_name}`, created_at: new Date().toISOString() }]);
      if (event.type === 'tool.completed') setMessages(prev => [...prev, { id: `tool-result-${Date.now()}`, role: 'tool', content: `工具结果：${event.result}`, created_at: new Date().toISOString() }]);
      if (event.type === 'run.completed' || event.type === 'run.failed') setStreaming(false);
    });
  }

  return <div className="page chat-page"><div className="page-header"><div><h1>Conversations</h1><p>实时观察 Agent、Tool 和最终回答。</p></div><select value={selectedAgent} onChange={e => setSelectedAgent(e.target.value)}>{agentsQuery.data?.map(a => <option key={a.id} value={a.id}>{a.name}</option>)}</select></div>
    <div className="chat-layout"><aside className="conversation-list"><div className="section-title"><MessageSquare size={16}/>会话</div>{conversations.map(item => <button key={item.id} className={conversationId === item.id ? 'conversation-item active' : 'conversation-item'} onClick={async () => { setConversationId(item.id); setMessages(await getMessages(item.id)); }}>{item.title}</button>)}{conversations.length === 0 && <div className="muted empty">尚无会话，发送第一条消息后会创建。</div>}</aside>
      <section className="chat-panel"><div className="messages">{messages.length === 0 ? <div className="empty-chat"><BotIcon/><h2>开始与 Agent 对话</h2><p>试试“计算 12800 * 0.18 + 300”或“检查系统状态”。</p></div> : messages.map(m => <div key={m.id} className={`message ${m.role}`}><div className="message-role">{m.role}</div><div className="message-body">{m.content}</div></div>)}</div><div className="composer"><textarea value={input} onChange={e => setInput(e.target.value)} placeholder="输入你的任务..." onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); void send(); }}}/><button className="primary-btn send-btn" onClick={() => void send()} disabled={streaming}><Send size={17}/>{streaming ? '执行中' : '发送'}</button></div></section>
    </div>
  </div>;
}
function BotIcon(){return <div className="empty-icon"><BotIconSvg/></div>}
function BotIconSvg(){return <svg width="34" height="34" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7"><rect x="4" y="6" width="16" height="13" rx="3"/><path d="M8 10h.01M16 10h.01M8 15h8M12 2v4"/></svg>}
