export const NODE_TYPES = {
  ENDPOINT: 'endpoint',
  PC: 'pc',
  SERVER: 'server',
  DATABASE: 'database',
  ROUTER: 'router',
  FIREWALL: 'firewall',
  USER: 'user',
};

export const EDGE_TYPES = {
  CONNECTS_TO: 'CONNECTS_TO',
  ACCESSES: 'ACCESSES',
  AUTHENTICATES: 'AUTHENTICATES',
  COMMUNICATES_WITH: 'COMMUNICATES_WITH',
};

export const NODE_TYPE_CONFIG = {
  endpoint: { label: 'Endpoint / PC', color: '#06b6d4', icon: 'Monitor' },
  pc: { label: 'Workstation / PC', color: '#06b6d4', icon: 'Laptop' },
  server: { label: 'Server', color: '#8b5cf6', icon: 'Server' },
  database: { label: 'Database', color: '#ec4899', icon: 'Database' },
  router: { label: 'Router', color: '#3b82f6', icon: 'Router' },
  firewall: { label: 'Firewall', color: '#f97316', icon: 'Shield' },
  user: { label: 'User Account', color: '#10b981', icon: 'User' },
};
