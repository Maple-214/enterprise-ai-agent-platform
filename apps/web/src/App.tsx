import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import { useEffect, useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { getMe } from './lib/api';
import { useAuthStore } from './stores/auth';
import { Layout } from './components/Layout';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { AgentsPage } from './pages/AgentsPage';
import { ChatPage } from './pages/ChatPage';
import { KnowledgePage } from './pages/KnowledgePage';
import { ApprovalsPage } from './pages/ApprovalsPage';
import { SettingsPage } from './pages/SettingsPage';
import { WorkflowsPage } from './pages/WorkflowsPage';
import './styles.css';

const queryClient = new QueryClient({ defaultOptions: { queries: { staleTime: 10_000 } } });

function AppRouter(){
  const { user, setUser } = useAuthStore();
  const [ready, setReady] = useState(false);
  useEffect(() => {
    if (!localStorage.getItem('agent_access_token')) { setReady(true); return; }
    getMe().then(setUser).catch(() => localStorage.removeItem('agent_access_token')).finally(() => setReady(true));
  }, [setUser]);
  if (!ready) return <div className="loading-screen">Loading...</div>;
  if (!user) return <Routes><Route path="*" element={<LoginPage/>}/></Routes>;
  return <Routes><Route element={<Layout/>}><Route path="/" element={<DashboardPage/>}/><Route path="/agents" element={<AgentsPage/>}/><Route path="/chat" element={<ChatPage/>}/><Route path="/knowledge" element={<KnowledgePage/>}/><Route path="/approvals" element={<ApprovalsPage/>}/><Route path="/workflows" element={<WorkflowsPage/>}/><Route path="/settings" element={<SettingsPage/>}/><Route path="*" element={<Navigate to="/" replace/>}/></Route></Routes>;
}

export default function App(){ return <QueryClientProvider client={queryClient}><BrowserRouter><AppRouter/></BrowserRouter></QueryClientProvider> }
