import { useEffect, useState } from 'react';
import { Banknote, Bot, CalendarClock, CalendarDays, CircleCheckBig, Users } from 'lucide-react';
import { api } from '../api';
import MetricCard from '../components/MetricCard';
import StatusBadge from '../components/StatusBadge';
import Loading from '../components/Loading';

export default function DashboardPage() {
  const [stats, setStats] = useState(null);
  const [bookings, setBookings] = useState([]);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState('');
  const today = new Date().toISOString().slice(0,10);
  useEffect(() => { Promise.all([api('/stats/overview'), api(`/bookings?day=${today}`), api('/ai/summaries')]).then(([s,b,a]) => { setStats(s); setBookings(b); setSummary(a[0] || null); }).catch((e) => setError(e.message)); }, []);
  if (!stats && !error) return <Loading label="Loading dashboard..." />;
  return <><div className="page-head"><div><span>Today</span><h1>Business overview</h1></div></div>{error && <div className="alert error">{error}</div>}{stats && <div className="metric-grid"><MetricCard label="Total bookings" value={stats.total_bookings} helper="Last 30 days" icon={CalendarDays}/><MetricCard label="Confirmed" value={stats.confirmed} helper="Ready to serve" icon={CircleCheckBig}/><MetricCard label="New customers" value={stats.new_customers} helper="Last 30 days" icon={Users}/><MetricCard label="Expected income" value={`₪${stats.expected_income.toFixed(0)}`} helper="Excludes cancelled" icon={Banknote}/></div>}<div className="dashboard-grid"><section className="card panel"><div className="panel-head"><div><span>Schedule</span><h2>Today's bookings</h2></div><a href="/dashboard/bookings">View all</a></div>{bookings.length ? <div className="booking-list">{bookings.map((b) => <div className="booking-row" key={b.id}><div className="time-box">{b.start_time.slice(0,5)}</div><div className="grow"><strong>{b.customer.name}</strong><span>{b.service.name}</span></div><StatusBadge status={b.status}/><a className="call-link" href={`tel:${b.customer.phone}`}>Call</a></div>)}</div> : <div className="empty"><CalendarClock/><h3>No bookings today</h3><p>Open slots are ready for customers.</p></div>}</section><section className="card panel ai-panel"><div className="panel-head"><div><span>AI assistant</span><h2>Latest summary</h2></div><Bot/></div>{summary ? <><p className="summary-copy">{summary.content}</p><ul>{summary.recommendations?.map((r) => <li key={r}>{r}</li>)}</ul></> : <div className="empty"><Bot/><h3>No summary yet</h3><p>Generate the first daily report from the AI page.</p></div>}</section></div></>;
}
