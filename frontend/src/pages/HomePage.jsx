import { Link } from 'react-router-dom';
import { ArrowRight, Bot, CalendarCheck, CheckCircle2, Clock3, ShieldCheck, Sparkles } from 'lucide-react';

export default function HomePage() {
  return (
    <>
      <section className="hero section">
        <div className="hero-copy">
          <div className="eyebrow"><Sparkles size={16} /> Smart booking, less admin</div>
          <h1>Appointments organized from first click to daily summary.</h1>
          <p>Customers book online. You manage every appointment from one clean dashboard. BookOps AI checks conflicts, drafts replies and highlights what matters.</p>
          <div className="hero-actions">
            <Link className="button" to="/book">Book an appointment <ArrowRight size={18} /></Link>
            <Link className="button ghost" to="/services">Explore services</Link>
          </div>
          <div className="trust-row">
            <span><CheckCircle2 size={17} /> Real-time availability</span>
            <span><CheckCircle2 size={17} /> Quick confirmations</span>
            <span><CheckCircle2 size={17} /> Mobile friendly</span>
          </div>
        </div>
        <div className="hero-panel">
          <div className="phone-card">
            <div className="phone-top"><span>Today</span><strong>4 appointments</strong></div>
            {[
              ['09:30', 'Classic Haircut', 'Confirmed'],
              ['11:00', 'Facial Treatment', 'Pending'],
              ['14:00', 'Haircut + Dye', 'Confirmed'],
              ['16:30', 'Classic Haircut', 'Done']
            ].map(([time, service, status]) => (
              <div className="mini-booking" key={time}><b>{time}</b><span>{service}</span><em>{status}</em></div>
            ))}
            <div className="ai-tip"><Bot size={20} /><div><strong>AI daily note</strong><p>Afternoon demand is highest. Promote the 11:00 opening.</p></div></div>
          </div>
        </div>
      </section>
      <section className="section compact feature-grid">
        <article><CalendarCheck /><h3>Easy online booking</h3><p>Customers choose a service and a genuinely available time.</p></article>
        <article><Bot /><h3>Useful AI assistant</h3><p>Priority, conflict checks, reply drafts, upsells and daily summaries.</p></article>
        <article><Clock3 /><h3>Automatic reminders</h3><p>Reduce missed appointments with scheduled notifications.</p></article>
        <article><ShieldCheck /><h3>Owner-only dashboard</h3><p>Protected management tools, logs, backups and health checks.</p></article>
      </section>
      <section className="section steps-section">
        <div className="section-heading"><span>How it works</span><h2>One simple booking lifecycle</h2></div>
        <div className="steps">
          {['Customer books', 'System validates', 'AI analyzes', 'Owner confirms', 'Reminder fires', 'Daily summary'].map((item, index) => (
            <div className="step" key={item}><b>{index + 1}</b><span>{item}</span></div>
          ))}
        </div>
      </section>
      <section className="section cta"><div><span>Ready when you are</span><h2>Choose a service and reserve your time.</h2></div><Link className="button light-button" to="/book">Book now <ArrowRight size={18} /></Link></section>
    </>
  );
}
