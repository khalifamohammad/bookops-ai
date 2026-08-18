import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LockKeyhole } from 'lucide-react';
import { api, setToken } from '../api';

export default function LoginPage() {
  const [form, setForm] = useState({ email: 'owner@bookops.local', password: 'ChangeMe123!' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  async function submit(event) {
    event.preventDefault(); setLoading(true); setError('');
    try { const data = await api('/auth/login', { method: 'POST', body: JSON.stringify(form) }); setToken(data.access_token); navigate('/dashboard'); }
    catch (e) { setError(e.message); } finally { setLoading(false); }
  }
  return <section className="login-section"><form className="card login-card" onSubmit={submit}><div className="login-icon"><LockKeyhole/></div><h1>Owner login</h1><p>Access bookings, customers, services, statistics and AI summaries.</p>{error && <div className="alert error">{error}</div>}<label>Email<input type="email" value={form.email} onChange={(e) => setForm({...form, email:e.target.value})} required /></label><label>Password<input type="password" value={form.password} onChange={(e) => setForm({...form, password:e.target.value})} required /></label><button className="button full" disabled={loading}>{loading ? 'Signing in...' : 'Sign in'}</button><small>Change the seeded credentials in your environment variables before deployment.</small></form></section>;
}
