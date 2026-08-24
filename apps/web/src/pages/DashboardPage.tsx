import { Activity, Bot, Database, ShieldCheck, Workflow } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { listAgents, listApprovals, listConversations, listDocuments } from '../lib/api';

export function DashboardPage() {
  const agents = useQuery({ queryKey: ['agents'], queryFn: listAgents });
  const conversations = useQuery({ queryKey: ['conversations'], queryFn: listConversations });
  const docs = useQuery({ queryKey: ['documents'], queryFn: listDocuments });
  const approvals = useQuery({ queryKey: ['approvals'], queryFn: listApprovals });

  const cards = [
    { title: 'Active Agents', value: agents.data?.length ?? 0, icon: Bot },
    { title: 'Conversations', value: conversations.data?.length ?? 0, icon: Activity },
    { title: 'Knowledge Docs', value: docs.data?.length ?? 0, icon: Database },
    { title: 'Pending Approvals', value: approvals.data?.filter(a => a.status === 'pending').length ?? 0, icon: ShieldCheck },
  ];

  return <div className="page">
    <div className="page-header"><div><h1>Dashboard</h1><p>企业 Agent 平台运行概览。</p></div></div>
    <div className="stat-grid">
      {cards.map(({ title, value, icon: Icon }) => <div className="stat-card" key={title}><div className="stat-icon"><Icon size={20}/></div><div><span>{title}</span><strong>{value}</strong></div></div>)}
    </div>
    <div className="panel-grid">
      <section className="panel"><div className="panel-title"><h2>Runtime</h2><span className="status-pill success">Healthy</span></div><div className="runtime-list"><div><span>API</span><b>FastAPI</b></div><div><span>Agent</span><b>LangGraph</b></div><div><span>Vector DB</span><b>Qdrant</b></div><div><span>Queue</span><b>Redis</b></div></div></section>
      <section className="panel"><div className="panel-title"><h2>Architecture</h2><Workflow size={20}/></div><p className="muted">React SPA → FastAPI → LangGraph → Tools / RAG / Memory → Model Gateway。</p></section>
    </div>
  </div>;
}
