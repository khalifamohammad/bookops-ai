import { useEffect, useState } from 'react';
import { api } from '../api';

export default function StatusPage() {
  const [health, setHealth] = useState(null);
  const [error, setError] = useState('');

  async function refresh() {
    try {
      setError('');
      setHealth(await api('/health'));
    } catch (err) {
      setError(err.message || 'Health check failed');
      setHealth(null);
    }
  }

  useEffect(() => {
    refresh();
    const timer = setInterval(refresh, 30000);
    return () => clearInterval(timer);
  }, []);

  const ok = health?.status === 'ok';

  return (
    <section className="section compact page-section">
      <div className="section-heading centered">
        <span>System status</span>
        <h1>BookOps AI health</h1>
        <p>Live application, database, and AI-agent health. Refreshes every 30 seconds.</p>
      </div>

      <div className="status-grid">
        <div className="card status-card">
          <span>API</span>
          <strong>{error ? 'Unavailable' : ok ? 'Operational' : 'Checking…'}</strong>
          <small>{error || health?.service || 'Waiting for health check'}</small>
        </div>
        <div className="card status-card">
          <span>Database</span>
          <strong>{health?.database === 'ok' ? 'Operational' : error ? 'Unavailable' : 'Checking…'}</strong>
          <small>PostgreSQL connectivity</small>
        </div>
        <div className="card status-card">
          <span>AI Agent</span>
          <strong>{health?.ai === 'ok' ? 'Operational' : error ? 'Unavailable' : 'Checking…'}</strong>
          <small>Booking analysis and summaries</small>
        </div>
      </div>

      <div className="status-actions">
        <button className="button" type="button" onClick={refresh}>Refresh status</button>
      </div>
    </section>
  );
}
