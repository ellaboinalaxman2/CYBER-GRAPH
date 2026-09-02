import { SEVERITY_CONFIG } from '../constants/severity';

export function getSeverityConfig(severity = 'INFO') {
  const key = severity?.toUpperCase() || 'INFO';
  return SEVERITY_CONFIG[key] || SEVERITY_CONFIG.INFO;
}

export function getSeverityBadgeClass(severity = 'INFO') {
  const config = getSeverityConfig(severity);
  return config.badgeClass;
}

export function getSeverityColor(severity = 'INFO') {
  const config = getSeverityConfig(severity);
  return config.color;
}
