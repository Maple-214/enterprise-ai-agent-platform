import { Bot, Database, LayoutDashboard, LogOut, Network, Settings2, ShieldCheck, Workflow } from 'lucide-react';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuthStore } from '../stores/auth';

const navItems = [
  { to: '/', label: '工作台', icon: LayoutDashboard },
  { to: '/agents', label: '智能体', icon: Bot },
  { to: '/chat', label: '对话中心', icon: Network },
  { to: '/knowledge', label: '知识库', icon: Database },
  { to: '/approvals', label: '审批中心', icon: ShieldCheck },
  { to: '/workflows', label: '工作流', icon: Workflow },
  { to: '/settings', label: '系统设置', icon: Settings2 },
];

export function Layout() {
  const { user, logout } = useAuthStore();
  return <div className="app-shell">
    <aside className="sidebar">
      <div className="brand"><div className="brand-mark">AI</div><div><strong>企业智能体平台</strong><span>企业控制台</span></div></div>
      <nav>{navItems.map(({ to, label, icon: Icon }) => <NavLink key={to} to={to} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} end={to === '/'}><Icon size={18}/>{label}</NavLink>)}</nav>
      <div className="sidebar-footer"><div className="user-card"><div className="avatar">{user?.display_name?.[0] ?? 'U'}</div><div className="user-info"><strong>{user?.display_name}</strong><span>{user?.role}</span></div></div><button className="ghost-btn" onClick={logout}><LogOut size={16}/>退出登录</button></div>
    </aside>
    <main className="main-content"><Outlet/></main>
  </div>;
}
