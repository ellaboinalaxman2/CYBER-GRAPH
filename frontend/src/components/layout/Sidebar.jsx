import React from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  Network,
  ShieldAlert,
  Flame,
  Activity,
  CheckCircle2,
  Settings,
  LogOut,
  ChevronLeft,
  ChevronRight,
  Shield,
} from 'lucide-react';
import { useAppContext } from '../../context/AppContext';
import { useAuth } from '../../hooks/useAuth';
import { useAlerts } from '../../hooks/useAlerts';

const ICON_MAP = {
  LayoutDashboard,
  Network,
  ShieldAlert,
  Flame,
  Activity,
  CheckCircle2,
  Settings,
};

export const Sidebar = () => {
  const { sidebarOpen, toggleSidebar } = useAppContext();
  const { user, logout } = useAuth();
  const { alerts } = useAlerts();
  const navigate = useNavigate();

  const activeAlertCount = alerts?.filter((a) => a.status === 'ACTIVE').length || 0;

  const links = [
    { name: 'Dashboard', path: '/dashboard', icon: LayoutDashboard },
    { name: 'Cyber Graph', path: '/graph', icon: Network },
    { name: 'Alerts', path: '/alerts', icon: ShieldAlert, badge: activeAlertCount },
    { name: 'Attacks', path: '/attacks', icon: Flame },
    { name: 'Events', path: '/events', icon: Activity },
    { name: 'Blockchain Audit', path: '/blockchain', icon: CheckCircle2 },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  return (
    <aside
      className={`fixed top-0 left-0 bottom-0 z-40 bg-slate-950/95 backdrop-blur-md border-r border-slate-800 transition-all duration-300 flex flex-col ${
        sidebarOpen ? 'w-64' : 'w-20'
      }`}
    >
      {/* Brand Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-slate-800/80">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500/20 to-blue-600/30 border border-cyan-500/40 flex items-center justify-center flex-shrink-0 shadow-lg shadow-cyan-500/10">
            <Shield className="w-5 h-5 text-cyan-400" />
          </div>
          {sidebarOpen && (
            <div className="flex flex-col">
              <span className="font-bold text-base tracking-wider bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400 bg-clip-text text-transparent">
                CYBER GRAPH
              </span>
              <span className="text-[10px] text-slate-400 font-mono tracking-widest uppercase">
                SecOps Intelligence
              </span>
            </div>
          )}
        </div>
        <button
          onClick={toggleSidebar}
          className="p-1.5 rounded-lg text-slate-400 hover:text-cyan-400 hover:bg-slate-800/80 transition-colors"
          title={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
        >
          {sidebarOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-1.5">
        {links.map((link) => {
          const Icon = link.icon;
          return (
            <NavLink
              key={link.path}
              to={link.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-3 rounded-xl font-medium transition-all duration-150 group relative ${
                  isActive
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-md shadow-cyan-950/50'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
                }`
              }
            >
              <Icon className="w-5 h-5 flex-shrink-0 transition-transform group-hover:scale-110" />
              {sidebarOpen && <span className="text-sm truncate">{link.name}</span>}
              {sidebarOpen && link.badge > 0 && (
                <span className="ml-auto px-2 py-0.5 text-xs font-mono font-bold bg-red-500/20 text-red-400 border border-red-500/30 rounded-full animate-pulse">
                  {link.badge}
                </span>
              )}
            </NavLink>
          );
        })}
      </nav>

      {/* User Info & Logout */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950">
        <div className="flex items-center gap-3 p-2 rounded-xl bg-slate-900/60 border border-slate-800/60">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-600 to-indigo-600 flex items-center justify-center font-bold text-xs text-white flex-shrink-0">
            {user?.name?.charAt(0) || 'A'}
          </div>
          {sidebarOpen && (
            <div className="flex-1 min-w-0">
              <p className="text-xs font-semibold text-slate-200 truncate">{user?.name || 'Security Analyst'}</p>
              <p className="text-[10px] text-cyan-400/80 font-mono truncate">{user?.role || 'SOC Level 2'}</p>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="p-1.5 rounded-lg text-slate-400 hover:text-red-400 hover:bg-red-950/30 transition-colors"
            title="Logout"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
