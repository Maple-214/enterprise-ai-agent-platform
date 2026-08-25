import { useEffect, useMemo, useState } from 'react';
import { Archive, Bot, Ellipsis, MessageSquare, Pin, Plus, Search, Send, Trash2, XCircle } from 'lucide-react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { archiveConversation, cancelRun, clearConversationMessages, createConversation, createRunStream, deleteConversation, getMessages, listAgents, listConversations, pinConversation, unpinConversation, updateConversation } from '../lib/api';
import type { AgentEvent, Conversation, Message } from '../types';

const roleLabel: Record<Message['role'], string> = { user: '你', assistant: '智能体', tool: '工具', system: '系统' };

export function ChatPage() {
  const queryClient = useQueryClient();
  const agentsQuery = useQuery({ queryKey: ['agents'], queryFn: listAgents });
  const [searchText, setSearchText] = useState('');
  const [page, setPage] = useState(1);
  const conversationsQuery = useQuery({ queryKey: ['conversations', searchText, page], queryFn: () => listConversations({ q: searchText, page, page_size: 30 }), refetchInterval: 3000 });
  const [conversationId, setConversationId] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [selectedAgent, setSelectedAgent] = useState('');
  const [runIdsByConversation, setRunIdsByConversation] = useState<Record<string, string>>({});
  const [localRunningConversations, setLocalRunningConversations] = useState<Set<string>>(new Set());
  const [toolStatus, setToolStatus] = useState('');
  const conversations = useMemo(() => conversationsQuery.data?.items ?? [], [conversationsQuery.data]);
  const selectedConversation = conversations.find((item) => item.id === conversationId) ?? null;
  const currentConversationRunning = Boolean(selectedConversation?.is_running || localRunningConversations.has(conversationId));
  const activeRunId = conversationId ? runIdsByConversation[conversationId] ?? selectedConversation?.latest_run?.id ?? '' : '';

  useEffect(() => {
    if (!selectedAgent && agentsQuery.data?.[0]) setSelectedAgent(agentsQuery.data[0].id);
  }, [agentsQuery.data, selectedAgent]);

  async function selectConversation(item: Conversation) {
    setConversationId(item.id);
    setSelectedAgent(item.agent_id);
    setMessages(await getMessages(item.id));
    setToolStatus(item.is_running ? '该对话正在执行任务' : '');
  }

  async function newConversation() {
    if (!selectedAgent) return;
    const row = await createConversation(selectedAgent, '新对话');
    setConversationId(row.id);
    setMessages([]);
    setToolStatus('');
    await queryClient.invalidateQueries({ queryKey: ['conversations'] });
  }

  async function deleteCurrent(item: Conversation) {
    if (!window.confirm(`确定删除“${item.title}”吗？删除后仍可在数据库层恢复。`)) return;
    await deleteConversation(item.id);
    if (item.id === conversationId) {
      setConversationId('');
      setMessages([]);
      setToolStatus('');
    }
    await queryClient.invalidateQueries({ queryKey: ['conversations'] });
  }

  async function rename(item: Conversation) {
    const title = window.prompt('请输入新的对话标题', item.title);
    if (!title?.trim()) return;
    await updateConversation(item.id, { title: title.trim() });
    await queryClient.invalidateQueries({ queryKey: ['conversations'] });
  }

  async function togglePin(item: Conversation) {
    await (item.is_pinned ? unpinConversation(item.id) : pinConversation(item.id));
    await queryClient.invalidateQueries({ queryKey: ['conversations'] });
  }

  function setConversationRunning(id: string, running: boolean) {
    setLocalRunningConversations((prev) => {
      const next = new Set(prev);
      if (running) next.add(id);
      else next.delete(id);
      return next;
    });
  }

  function appendAssistant(conversationIdForEvent: string, runId: string, text: string) {
    if (conversationIdForEvent !== conversationId) return;
    setMessages((prev) => {
      const last = prev[prev.length - 1];
      if (last?.role === 'assistant' && last.run_id === runId) {
        return [...prev.slice(0, -1), { ...last, content: last.content + text }];
      }
      return [...prev, { id: `stream-${Date.now()}`, conversation_id: conversationIdForEvent, run_id: runId, role: 'assistant', content: text, created_at: new Date().toISOString() }];
    });
  }

  async function send() {
    if (!input.trim() || currentConversationRunning || !conversationId) return;
    const content = input.trim();
    const targetConversationId = conversationId;
    setInput('');
    setConversationRunning(targetConversationId, true);
    setToolStatus('任务已提交，正在等待执行');
    setMessages((prev) => [...prev, { id: `user-${Date.now()}`, conversation_id: targetConversationId, run_id: null, role: 'user', content, created_at: new Date().toISOString() }]);

    createRunStream(targetConversationId, content, (event: AgentEvent) => {
      setConversationRunning(event.conversation_id, event.type !== 'run.completed' && event.type !== 'run.failed');

      if (event.type === 'run.started') {
        setRunIdsByConversation((prev) => ({ ...prev, [event.conversation_id]: event.run_id }));
        if (event.conversation_id === conversationId) setToolStatus('任务执行中');
      }
      if (event.type === 'tool.started' && event.conversation_id === conversationId) setToolStatus(`正在调用：${event.tool_name}`);
      if (event.type === 'tool.completed' && event.conversation_id === conversationId) setToolStatus(`工具已完成：${event.tool_name}`);
      if (event.type === 'message.delta') appendAssistant(event.conversation_id, event.run_id, event.content);
      if (event.type === 'citation.created' && event.conversation_id === conversationId) setToolStatus(`已引用知识库：${event.source}`);
      if (event.type === 'run.completed') {
        if (event.conversation_id === conversationId) setToolStatus('本次执行已完成');
        void queryClient.invalidateQueries({ queryKey: ['conversations'] });
      }
      if (event.type === 'run.failed' && event.conversation_id === conversationId) setToolStatus(event.message);
    });
  }

  async function cancelActiveRun() {
    if (!activeRunId) return;
    await cancelRun(activeRunId);
    setConversationRunning(conversationId, false);
    setToolStatus('已请求停止本次执行');
    await queryClient.invalidateQueries({ queryKey: ['conversations'] });
  }

  async function clearMessages() {
    if (!conversationId || !window.confirm('确定清空当前对话消息吗？')) return;
    await clearConversationMessages(conversationId);
    setMessages([]);
    await queryClient.invalidateQueries({ queryKey: ['conversations'] });
  }

  return <div className="page chat-page">
    <div className="page-header">
      <div><h1>对话中心</h1><p>管理会话，并观察一次智能体执行中的工具调用、知识库引用和最终结果。</p></div>
      <div className="chat-header-actions">
        <select aria-label="选择智能体" value={selectedAgent} onChange={(e) => setSelectedAgent(e.target.value)}>{agentsQuery.data?.map((agent) => <option key={agent.id} value={agent.id}>{agent.name}</option>)}</select>
        <button className="primary-btn" onClick={() => void newConversation()} disabled={!selectedAgent}><Plus size={16}/>新建对话</button>
      </div>
    </div>
    <div className="chat-layout">
      <aside className="conversation-list">
        <div className="section-title"><MessageSquare size={16}/>会话列表</div>
        <div className="conversation-search"><Search size={15}/><input value={searchText} placeholder="搜索对话" onChange={(e) => { setSearchText(e.target.value); setPage(1); }}/></div>
        <div className="conversation-items">
          {conversations.map((item) => <div className={`conversation-item-wrap ${conversationId === item.id ? 'active' : ''}`} key={item.id}>
            <button className="conversation-item" onClick={() => void selectConversation(item)}>
              <div className="conversation-title-row">
                <span className="conversation-title">{item.is_pinned && <Pin size={12}/>} {item.title}</span>
                {item.is_running && <span className="conversation-status running"><span className="running-dot"/>执行中</span>}
              </div>
              <span className="conversation-time">{new Date(item.updated_at).toLocaleString()}</span>
            </button>
            <div className="conversation-actions">
              <button className="icon-btn" title="重命名" onClick={() => void rename(item)}><Ellipsis size={15}/></button>
              <button className="icon-btn" title={item.is_pinned ? '取消置顶' : '置顶'} onClick={() => void togglePin(item)}><Pin size={14}/></button>
              <button className="icon-btn" title="归档" onClick={() => void archiveConversation(item.id).then(() => queryClient.invalidateQueries({ queryKey: ['conversations'] }))}><Archive size={14}/></button>
              <button className="icon-btn danger" title="删除" onClick={() => void deleteCurrent(item)}><Trash2 size={14}/></button>
            </div>
          </div>)}
        </div>
        {!conversations.length && <div className="empty">暂无对话<br/>点击右上角新建对话。</div>}
        {conversationsQuery.data?.has_next && <button className="secondary-btn full" onClick={() => setPage((value) => value + 1)}>加载更多</button>}
      </aside>

      <section className="chat-panel">
        <div className="chat-toolbar">
          <div><strong>{selectedConversation?.title ?? '未选择对话'}</strong><span>{toolStatus || (conversationId ? (currentConversationRunning ? '任务执行中' : '可以继续发送消息') : '请先新建或选择对话')}</span></div>
          {conversationId && <button className="secondary-btn" onClick={() => void clearMessages()}><Trash2 size={15}/>清空消息</button>}
        </div>
        <div className="messages">
          {messages.length === 0 ? <div className="empty-chat"><div className="empty-icon"><Bot size={30}/></div><h2>开始一段新的对话</h2><p>先创建对话，再输入任务。可以试试“计算 12800 * 0.18 + 300”。</p></div> : messages.map((message) => <div key={message.id} className={`message ${message.role}`}><div className="message-role">{roleLabel[message.role]}</div><div className="message-body">{message.content}</div></div>)}
        </div>
        <div className="composer">
          <textarea disabled={!conversationId || currentConversationRunning} value={input} onChange={(e) => setInput(e.target.value)} placeholder={conversationId ? (currentConversationRunning ? '当前对话正在执行任务，请等待完成' : '输入你的任务，回车发送，Shift + Enter 换行') : '请先创建或选择一个对话'} onKeyDown={(e) => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); void send(); } }}/>
          {currentConversationRunning ? <button className="secondary-btn send-btn" onClick={() => void cancelActiveRun()}><XCircle size={17}/>停止执行</button> : <button className="primary-btn send-btn" disabled={!conversationId || !input.trim()} onClick={() => void send()}><Send size={17}/>发送消息</button>}
        </div>
      </section>
    </div>
  </div>;
}
