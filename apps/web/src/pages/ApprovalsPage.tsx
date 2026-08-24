import { ShieldCheck } from 'lucide-react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { listApprovals, resolveApproval } from '../lib/api';

export function ApprovalsPage() {
  const client = useQueryClient();
  const query = useQuery({ queryKey: ['approvals'], queryFn: listApprovals });
  async function resolve(id: string, decision: 'approve'|'reject') { await resolveApproval(id, decision); await client.invalidateQueries({ queryKey: ['approvals'] }); }
  return <div className="page"><div className="page-header"><div><h1>Approvals</h1><p>高风险 Tool 的人工确认中心。</p></div></div><div className="panel"><div className="table">{query.data?.map(item => <div className="approval-row" key={item.id}><div><div className="file-name"><ShieldCheck size={17}/>{item.tool_name}</div><p className="muted">{item.reason}</p></div><span className="status-pill warning">{item.status}</span><div className="actions">{item.status === 'pending' && <><button className="secondary-btn" onClick={() => void resolve(item.id,'reject')}>Reject</button><button className="primary-btn" onClick={() => void resolve(item.id,'approve')}>Approve</button></>}</div></div>)}</div>{!query.data?.length && <div className="empty">当前没有待审批任务。</div>}</div></div>;
}
