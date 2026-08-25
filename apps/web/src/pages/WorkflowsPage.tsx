import { GitBranch } from 'lucide-react';
export function WorkflowsPage(){ return <div className="page"><div className="page-header"><div><h1>工作流</h1><p>管理智能体任务编排和流程定义。</p></div><button className="primary-btn">创建工作流</button></div><div className="panel workflow-placeholder"><GitBranch size={38}/><h2>工作流设计器</h2><p className="muted">后续接入 React Flow，将智能体、条件、工具和人工审批组合成可视化流程。</p></div></div> }
