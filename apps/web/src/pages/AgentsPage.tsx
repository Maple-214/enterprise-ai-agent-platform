import { Bot, Wrench } from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { listAgents } from '../lib/api';

export function AgentsPage() {
  const query = useQuery({ queryKey: ['agents'], queryFn: listAgents });
  return <div className="page"><div className="page-header"><div><h1>Agents</h1><p>管理 Agent 定义、Prompt 和工具能力。</p></div><button className="primary-btn">创建 Agent</button></div>
  <div className="card-grid">{query.data?.map(agent => <div className="agent-card" key={agent.id}><div className="agent-card-icon"><Bot size={22}/></div><div className="agent-card-body"><div className="row-between"><h3>{agent.name}</h3><span className="status-pill success">Active</span></div><p>{agent.description}</p><div className="tool-tags">{agent.enabled_tools.map(tool => <span key={tool}><Wrench size={12}/>{tool}</span>)}</div></div></div>)}</div>
  </div>;
}
