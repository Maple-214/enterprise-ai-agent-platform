import { FileText, UploadCloud } from 'lucide-react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { listDocuments, uploadDocument } from '../lib/api';

export function KnowledgePage() {
  const queryClient = useQueryClient();
  const query = useQuery({ queryKey: ['documents'], queryFn: listDocuments });
  async function onUpload(file?: File) {
    if (!file) return;
    await uploadDocument(file);
    await queryClient.invalidateQueries({ queryKey: ['documents'] });
  }
  return <div className="page"><div className="page-header"><div><h1>Knowledge Base</h1><p>上传企业文档并进入 RAG 检索。</p></div><label className="primary-btn upload-btn"><UploadCloud size={17}/>上传文档<input type="file" hidden accept=".txt,.md,.markdown,.csv,.pdf" onChange={e => void onUpload(e.target.files?.[0])}/></label></div>
    <div className="panel"><div className="panel-title"><h2>Documents</h2><span>{query.data?.length ?? 0} files</span></div>{query.data?.length ? <div className="table">{query.data.map(doc => <div className="table-row" key={doc.id}><div className="file-name"><FileText size={17}/>{doc.filename}</div><span className={`status-pill ${doc.status === 'ready' ? 'success' : 'warning'}`}>{doc.status}</span><span className="muted">{new Date(doc.created_at).toLocaleString()}</span></div>)}</div> : <div className="empty">尚无文档。上传一份 Markdown 或 PDF 即可开始。</div>}</div>
  </div>;
}
