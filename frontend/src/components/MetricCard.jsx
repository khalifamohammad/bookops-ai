export default function MetricCard({ label, value, helper, icon: Icon }) {
  return (
    <article className="metric-card">
      <div><span>{label}</span><strong>{value}</strong>{helper && <small>{helper}</small>}</div>
      {Icon && <div className="metric-icon"><Icon size={22} /></div>}
    </article>
  );
}
