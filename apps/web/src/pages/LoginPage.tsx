import { useState } from 'react';
import { Bot, LockKeyhole } from 'lucide-react';
import { login } from '../lib/api';
import { useAuthStore } from '../stores/auth';

export function LoginPage() {
  const { setUser } = useAuthStore();
  const [email, setEmail] = useState('demo@company.local');
  const [password, setPassword] = useState('Demo123!');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError('');
    setLoading(true);
    try {
      const result = await login(email, password);
      localStorage.setItem('agent_access_token', result.access_token);
      setUser(result.user);
    } catch (e) {
      setError(e instanceof Error ? e.message : '登录失败');
    } finally {
      setLoading(false);
    }
  }

  return <div className="login-page">
    <div className="login-card">
      <div className="login-logo"><Bot size={28} /></div>
      <h1>Enterprise AI Agent</h1>
      <p className="muted">企业级 Agent 平台控制台</p>
      <form onSubmit={handleSubmit}>
        <label>邮箱<input value={email} onChange={(e) => setEmail(e.target.value)} /></label>
        <label>密码<div className="input-icon"><LockKeyhole size={16} /><input type="password" value={password} onChange={(e) => setPassword(e.target.value)} /></div></label>
        {error && <div className="error-box">{error}</div>}
        <button className="primary-btn full" disabled={loading}>{loading ? '登录中...' : '登录'}</button>
      </form>
      <div className="demo-note">本地 Demo：demo@company.local / Demo123!</div>
    </div>
  </div>;
}
