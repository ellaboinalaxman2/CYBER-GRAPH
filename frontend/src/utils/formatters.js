export function formatPercentage(value) {
  if (value === undefined || value === null) return '0%';
  const num = typeof value === 'number' ? value : parseFloat(value);
  // If it's a decimal <= 1, convert to 100-scale
  const scaled = num <= 1 && num > 0 ? num * 100 : num;
  return `${Math.round(scaled)}%`;
}

export function formatRiskScore(score) {
  if (score === undefined || score === null) return '0 / 100';
  const num = typeof score === 'number' ? score : parseFloat(score);
  const scaled = num <= 1 && num > 0 ? Math.round(num * 100) : Math.round(num);
  return `${scaled} / 100`;
}

export function truncateHash(hash, front = 8, back = 6) {
  if (!hash) return '';
  if (hash.length <= front + back) return hash;
  return `${hash.slice(0, front)}...${hash.slice(-back)}`;
}

export function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}
