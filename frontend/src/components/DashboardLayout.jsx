import { NavLink, Outlet, useNavigate } from 'react-router-dom';
import { Bot, CalendarDays, ChartNoAxesCombined, LogOut, Menu, Scissors, Users, X } from 'lucide-react';
import { useState } from 'react';
import { setToken } from '../api';

const links = [
  ['/', CalendarDays, 'Overview'],
  ['/bookings', CalendarDays, 'Bookings'],
  ['/customers', Users, 'Customers'],
  ['/services', Scissors, 'Services'],
  ['/stats', ChartNoAxesCombined, 'Statistics'],
  ['/ai', Bot, 'AI assistant']
];

export default function DashboardLayout() {
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  function logout() {
    setToken(null);
    navigate('/login');
  }
  return (
    <div className="dashboard-shell">
      <aside className={open ? 'sidebar open' : 'sidebar'}>
        <div className="sidebar-head">
          <div className="brand light"><span>BO</span> BookOps AI</div>
          <button className="icon-button mobile-only" onClick={() => setOpen(false)}><X size={22} /></button>
        </div>
        <nav>
          {links.map(([path, Icon, label]) => (
            <NavLink key={label} end={path === '/'} to={`/dashboard${path === '/' ? '' : path}`} onClick={() => setOpen(false)}>
              <Icon size={19} /> {label}
            </NavLink>
          ))}
        </nav>
        <button className="sidebar-logout" onClick={logout}><LogOut size={19} /> Log out</button>
      </aside>
      <section className="dashboard-main">
        <header className="dashboard-topbar">
          <button className="icon-button mobile-only" onClick={() => setOpen(true)}><Menu /></button>
          <div><strong>Owner workspace</strong><span>Manage bookings, customers and AI insights</span></div>
          <a className="button ghost small" href="/" target="_blank">Open booking site</a>
        </header>
        <div className="dashboard-content"><Outlet /></div>
      </section>
    </div>
  );
}
