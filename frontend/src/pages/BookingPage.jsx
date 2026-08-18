import { useEffect, useMemo, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { CalendarCheck, CheckCircle2, Clock3 } from 'lucide-react';
import { api } from '../api';

const initialForm = { customer_name: '', customer_phone: '', customer_email: '', service_id: '', booking_date: '', start_time: '', customer_notes: '' };

export default function BookingPage() {
  const [searchParams] = useSearchParams();
  const [services, setServices] = useState([]);
  const [slots, setSlots] = useState([]);
  const [form, setForm] = useState({ ...initialForm, service_id: searchParams.get('service') || '' });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const minDate = useMemo(() => new Date().toISOString().slice(0, 10), []);

  useEffect(() => { api('/services').then(setServices).catch((e) => setError(e.message)); }, []);
  useEffect(() => {
    setSlots([]);
    setForm((old) => ({ ...old, start_time: '' }));
    if (!form.service_id || !form.booking_date) return;
    api(`/availability?service_id=${form.service_id}&date=${form.booking_date}`)
      .then((data) => setSlots(data.slots))
      .catch((e) => setError(e.message));
  }, [form.service_id, form.booking_date]);

  function update(event) { setForm({ ...form, [event.target.name]: event.target.value }); }
  async function submit(event) {
    event.preventDefault(); setLoading(true); setError(''); setMessage('');
    try {
      const payload = { ...form, service_id: Number(form.service_id), customer_email: form.customer_email || null, customer_notes: form.customer_notes || null };
      const booking = await api('/bookings/public', { method: 'POST', body: JSON.stringify(payload) });
      setMessage(`Booking #${booking.id} received for ${booking.booking_date} at ${booking.start_time.slice(0, 5)}.`);
      setForm(initialForm); setSlots([]);
    } catch (e) { setError(e.message); } finally { setLoading(false); }
  }

  return (
    <section className="section page-section booking-page">
      <div className="booking-intro"><span className="eyebrow"><CalendarCheck size={16} /> Online booking</span><h1>Reserve your appointment</h1><p>Pick a service and date. Only available appointment times will appear.</p>
        <div className="booking-benefits"><span><CheckCircle2 /> Instant availability check</span><span><CheckCircle2 /> Confirmation notification</span><span><Clock3 /> Takes about one minute</span></div>
      </div>
      <form className="card form-card" onSubmit={submit}>
        {message && <div className="alert success">{message}</div>}
        {error && <div className="alert error">{error}</div>}
        <div className="form-grid">
          <label>Full name<input name="customer_name" value={form.customer_name} onChange={update} required /></label>
          <label>Phone number<input name="customer_phone" value={form.customer_phone} onChange={update} required /></label>
          <label>Email, optional<input type="email" name="customer_email" value={form.customer_email} onChange={update} /></label>
          <label>Service<select name="service_id" value={form.service_id} onChange={update} required><option value="">Select a service</option>{services.map((s) => <option value={s.id} key={s.id}>{s.name} — ₪{s.price}</option>)}</select></label>
          <label>Date<input type="date" name="booking_date" min={minDate} value={form.booking_date} onChange={update} required /></label>
          <label>Available time<select name="start_time" value={form.start_time} onChange={update} required disabled={!slots.length}><option value="">{form.booking_date && form.service_id ? (slots.length ? 'Select a time' : 'No slots available') : 'Choose service and date'}</option>{slots.map((slot) => <option key={slot} value={slot}>{slot.slice(0, 5)}</option>)}</select></label>
          <label className="wide">Notes, optional<textarea name="customer_notes" value={form.customer_notes} onChange={update} rows="4" placeholder="Tell us anything useful, for example: urgent before an event." /></label>
        </div>
        <button className="button full" disabled={loading}>{loading ? 'Creating booking...' : 'Confirm booking'}</button>
      </form>
    </section>
  );
}
