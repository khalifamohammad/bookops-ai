import { Link, NavLink, Outlet } from 'react-router-dom';
import { CalendarDays, Menu, X } from 'lucide-react';
import { useEffect, useState } from 'react';

export default function PublicLayout() {
  const [open, setOpen] = useState(false);
  const [rtl, setRtl] = useState(() => localStorage.getItem('bookops_dir') === 'rtl');
  useEffect(() => {
    document.documentElement.dir = rtl ? 'rtl' : 'ltr';
    localStorage.setItem('bookops_dir', rtl ? 'rtl' : 'ltr');
  }, [rtl]);
  return (
    <div className="public-shell">
      <header className="public-header">
        <Link to="/" className="brand"><span>BO</span> BookOps AI</Link>
        <button className="icon-button mobile-only" onClick={() => setOpen(!open)} aria-label="Toggle menu">
          {open ? <X size={22} /> : <Menu size={22} />}
        </button>
        <nav className={open ? 'public-nav open' : 'public-nav'} onClick={() => setOpen(false)}>
          <NavLink to="/">Home</NavLink>
          <NavLink to="/services">Services</NavLink>
          <NavLink to="/contact">Contact</NavLink>
          <NavLink to="/status">Status</NavLink>
          <NavLink to="/login">Owner login</NavLink>
          <button type="button" className="direction-toggle" onClick={() => setRtl(!rtl)}>{rtl ? 'LTR' : 'RTL'}</button>
          <Link className="button small" to="/book"><CalendarDays size={18} /> Book now</Link>
        </nav>
      </header>
      <main><Outlet /></main>
      <footer className="footer">
        <div><strong>BookOps AI</strong><p>Smart booking for small businesses.</p></div>
        <div><p>Built as a complete Full-Stack + AI + DevOps internship project.</p></div>
      </footer>
    </div>
  );
}
