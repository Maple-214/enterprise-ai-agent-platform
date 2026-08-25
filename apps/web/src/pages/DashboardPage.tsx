import { Activity, Bot, Database, ShieldCheck, Workflow } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { listAgents, listApprovals, listConversations, listDocuments } from '../lib/api';

export function DashboardPage() {
  const agents = useQuery({ queryKey: ['agents'], queryFn: listAgents });
  const conversations = useQuery({ queryKey: ['conversations', 'dashboard'], queryFn: () => listConversations({ page_size: 1 }) });
  const docs = useQuery({ queryKey: ['documents'], queryFn: listDocuments });
  const approvals = useQuery({ queryKey: ['approvals'], queryFn: listApprovals });
  const cards = [
    { title: '启用中的智能体', value: agents.data?.length ?? 0, icon: Bot },
    { title: '对话总数', value: conversations.data?.total ?? 0, icon: Activity },
    { title: '知识文档', value: docs.data?.length ?? 0, icon: Database },
    { title: '待审批任务', value: approvals.data?.filter((item) => item.status === 'pending').length ?? 0, icon: ShieldCheck },
  ];
  return <div className="page"><div className="page-header"><div><h1>工作台</h1><p>企业智能体平台运行概览。</p></div></div>
    <div className="stat-grid">{cards.map(({ title, value, icon: Icon }) => <div className="stat-card" key={title}><div className="stat-icon"><Icon size={20}/></div><div><span>{title}</span><strong>{value}</strong></div></div>)}</div>
    <div className="panel-grid"><section className="panel"><div className="panel-title"><h2>运行环境</h2><span className="status-pill success">正常</span></div><div className="runtime-list"><div><span>接口服务</span><b>FastAPI</b></div><div><span>智能体编排</span><b>LangGraph</b></div><div><span>向量数据库</span><b>Qdrant</b></div><div><span>任务队列</span><b>Redis</b></div></div></section><section className="panel"><div className="panel-title"><h2>系统架构</h2><Workflow size={20}/></div><p className="muted">React + TypeScript → FastAPI → 会话管理 → 执行任务 → LangGraph → 工具 / RAG / 记忆 → 模型网关。</p></section></div>
  </div>;
}
