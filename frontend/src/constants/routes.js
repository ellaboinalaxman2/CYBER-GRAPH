export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  GRAPH: '/graph',
  ALERTS: '/alerts',
  ATTACKS: '/attacks',
  ATTACK_DETAILS: '/attacks/:id',
  EVENTS: '/events',
  NODE_DETAILS: '/nodes/:id',
  BLOCKCHAIN: '/blockchain',
  SETTINGS: '/settings',
  NOT_FOUND: '*',
};

export const NAV_LINKS = [
  { name: 'Dashboard', path: '/dashboard', icon: 'LayoutDashboard' },
  { name: 'Cyber Graph', path: '/graph', icon: 'Network' },
  { name: 'Alerts', path: '/alerts', icon: 'ShieldAlert', badge: 'activeAlerts' },
  { name: 'Attacks', path: '/attacks', icon: 'Flame' },
  { name: 'Events', path: '/events', icon: 'Activity' },
  { name: 'Blockchain Audit', path: '/blockchain', icon: 'CheckCircle2' },
  { name: 'Settings', path: '/settings', icon: 'Settings' },
];
