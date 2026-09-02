export function formatTimestamp(isoString) {
  if (!isoString) return 'Just now';
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  } catch (e) {
    return isoString;
  }
}

export function formatDateTime(isoString) {
  if (!isoString) return 'N/A';
  try {
    const d = new Date(isoString);
    if (isNaN(d.getTime())) return isoString;
    return `${d.toLocaleDateString()} ${d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`;
  } catch (e) {
    return isoString;
  }
}

export function timeAgo(isoString) {
  if (!isoString) return '';
  const now = new Date();
  const past = new Date(isoString);
  const diffInSecs = Math.floor((now - past) / 1000);

  if (diffInSecs < 60) return `${diffInSecs}s ago`;
  if (diffInSecs < 3600) return `${Math.floor(diffInSecs / 60)}m ago`;
  if (diffInSecs < 86400) return `${Math.floor(diffInSecs / 3600)}h ago`;
  return `${Math.floor(diffInSecs / 86400)}d ago`;
}
