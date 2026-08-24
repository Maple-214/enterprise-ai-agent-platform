import { Bot, Database, FileCheck2, LayoutDashboard, LogOut, Network, Settings2, ShieldCheck, Workflow } from 'lucide-react';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuthStore } from '../stores/auth';

const navItems = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/agents', label: 'Agents', icon: Bot },
  { to: '/chat', label: 'Conversations', icon: Network },
  { to: '/knowledge', label: 'Knowledge', icon: Database },
  { to: '/approvals', label: 'Approvals', icon: ShieldCheck },
  { to: '/workflows', label: 'Workflows', icon: Workflow },
  { to: '/settings', label: 'Settings', icon: Settings2 },
];

export function Layout() {
  const { user, logout } = useAuthStore();
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark">AI</div><div><strong>Agent Platform</strong><span>Enterprise Console</span></div></div>
        <nav>
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} end={to === '/'}>
              <Icon size={18} />{label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="user-card"><div className="avatar">{user?.display_name?.[0] ?? 'U'}</div><div className="user-info"><strong>{user?.display_name}</strong><span>{user?.role}</span></div></div>
          <button className="ghost-btn" onClick={logout}><LogOut size={16} />退出</button>
        </div>
      </aside>
      <main className="main-content"><Outlet /></main>
    </div>
  );
}
