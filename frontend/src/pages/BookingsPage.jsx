import { useEffect, useState } from 'react';
import { Bot, CalendarClock, CalendarDays, Phone, PlusCircle, StickyNote } from 'lucide-react';
import { api } from '../api';
import Loading from '../components/Loading';
import StatusBadge from '../components/StatusBadge';

const statuses = ['PENDING','CONFIRMED','DONE','CANCELLED','NO_SHOW'];
export default function BookingsPage() {
  const [bookings, setBookings] = useState([]); const [filter, setFilter] = useState(''); const [loading, setLoading] = useState(true); const [error, setError] = useState('');
  async function load() { setLoading(true); try { setBookings(await api(`/bookings${filter ? `?status=${filter}` : ''}`)); } catch(e){ setError(e.message);} finally{setLoading(false);} }
  useEffect(() => { load(); }, [filter]);
  async function changeStatus(booking, status) { let cancellation_reason = null; if(status==='CANCELLED'){ cancellation_reason = prompt('Cancellation reason:'); if(!cancellation_reason) return; } try{ await api(`/bookings/${booking.id}/status`, {method:'PATCH', body:JSON.stringify({status,cancellation_reason})}); load(); }catch(e){setError(e.message);} }
async function reschedule(booking) {
  const booking_date = prompt(
    'New date (YYYY-MM-DD):',
    booking.booking_date
  );

  if (!booking_date) return;

  const start_time = prompt(
    'New start time (HH:MM):',
    booking.start_time.slice(0, 5)
  );

  if (!start_time) return;

  try {
    await api(`/bookings/${booking.id}`, {
      method: 'PUT',
      body: JSON.stringify({
        booking_date,
        start_time,
      }),
    });

    await load();
  } catch (e) {
    setError(e.message);
  }
}

async function addNote(bookingId) {
  const note = prompt('Internal booking note:');

  if (!note?.trim()) return;

  try {
    await api(`/bookings/${bookingId}/notes`, {
      method: 'POST',
      body: JSON.stringify({
        note: note.trim(),
      }),
    });

    await load();
  } catch (e) {
    setError(e.message);
  }
}
async function analyze(id){ try{ const result=await api(`/ai/analyze-booking/${id}`,{method:'POST'}); alert(`${result.priority.toUpperCase()} priority
${result.confirmation_reply}
Upsell: ${result.upsell_suggestion || 'None'}`); load(); }catch(e){setError(e.message);} }
  return <><div className="page-head"><div><span>Operations</span><h1>Bookings</h1></div><a className="button small" href="/book" target="_blank"><PlusCircle/> New booking</a></div><div className="toolbar"><select value={filter} onChange={(e)=>setFilter(e.target.value)}><option value="">All statuses</option>{statuses.map((s)=><option key={s}>{s}</option>)}</select></div>{error&&<div className="alert error">{error}</div>}{loading?<Loading/>:bookings.length?<div className="table-card"><table><thead><tr><th>Date & time</th><th>Customer</th><th>Service</th><th>Status</th><th>Actions</th></tr></thead><tbody>{bookings.map((b)=><tr key={b.id}><td><strong>{b.booking_date}</strong><span>{b.start_time.slice(0,5)}–{b.end_time.slice(0,5)}</span></td><td><strong>{b.customer.name}</strong><a href={`tel:${b.customer.phone}`}><Phone size={14}/>{b.customer.phone}</a></td><td><strong>{b.service.name}</strong><span>₪{b.expected_income.toFixed(0)}</span></td><td><StatusBadge status={b.status}/></td><td><div className="action-row"><select value={b.status} onChange={(e)=>changeStatus(b,e.target.value)}>{statuses.map((s)=><option key={s}>{s}</option>)}</select><button className="icon-button" title="Reschedule" onClick={()=>reschedule(b)}><CalendarClock size={18}/></button><button className="icon-button" title="Add internal note" onClick={()=>addNote(b.id)}><StickyNote size={18}/></button><button className="icon-button" title="Analyze booking" onClick={()=>analyze(b.id)}><Bot size={18}/></button></div></td></tr>)}</tbody></table></div>:<div className="empty card"><CalendarDays/><h3>No bookings found</h3></div>}</>;
}
