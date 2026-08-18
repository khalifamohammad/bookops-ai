import { useEffect, useState } from 'react';
import { Clock3, Scissors } from 'lucide-react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import Loading from '../components/Loading';

export default function ServicesPage() {
  const [services, setServices] = useState([]);
  const [error, setError] = useState('');
  useEffect(() => { api('/services').then(setServices).catch((e) => setError(e.message)); }, []);
  return (
    <section className="section page-section">
      <div className="section-heading centered"><span>Services</span><h1>Choose what you need</h1><p>Every duration and price is shown before you book.</p></div>
      {error && <div className="alert error">{error}</div>}
      {!services.length && !error ? <Loading /> : (
        <div className="service-grid">
          {services.map((service) => (
            <article className="service-card" key={service.id}>
              <div className="service-icon"><Scissors /></div>
              <h3>{service.name}</h3><p>{service.description || 'Professional service tailored to your needs.'}</p>
              <div className="service-meta"><span><Clock3 size={17} /> {service.duration_minutes} min</span><strong>₪{service.price.toFixed(0)}</strong></div>
              <Link className="button full" to={`/book?service=${service.id}`}>Book this service</Link>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
