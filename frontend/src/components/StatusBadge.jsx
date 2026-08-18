export default function StatusBadge({ status }) {
  return <span className={`status status-${status.toLowerCase().replace('_', '-')}`}>{status.replace('_', ' ')}</span>;
}
