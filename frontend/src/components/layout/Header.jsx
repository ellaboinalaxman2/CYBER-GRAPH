import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Bell,
  Search,
  ShieldAlert,
  Activity,
  Cpu,
  CheckCircle,
  Menu,
} from 'lucide-react';
import { useAppContext } from '../../context/AppContext';
import { useAlerts } from '../../hooks/useAlerts';
import Badge from '../common/Badge';

export const Header = () => {
  const { toggleSidebar, systemHealth } = useAppContext();
  const { alerts } = useAlerts();
  const [searchTerm, setSearchTerm] = useState('');
  const [showNotifications, setShowNotifications] = useState(false);
  const navigate = useNavigate();

  const criticalAlerts = alerts?.filter((a) => a.severity === 'CRITICAL' && a.status === 'ACTIVE') || [];

  const handleGlobalSearch = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      navigate(`/events?search=${encodeURIComponent(searchTerm.trim())}`);
    }
  };

  return (
    <header className="h-16 bg-slate-950/80 backdrop-blur-md border-b border-slate-800 px-4 lg:px-6 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center gap-3">
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-lg text-slate-400 hover:text-cyan-400 hover:bg-slate-800/80 lg:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>

        {/* Global Search Input */}
        <form onSubmit={handleGlobalSearch} className="relative hidden md:block w-72 lg:w-96">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search IP, node, hash, or event ID..."
            className="w-full bg-slate-900/90 border border-slate-800 rounded-lg pl-9 pr-4 py-1.5 text-xs text-slate-200 placeholder:text-slate-500 focus:outline-none focus:border-cyan-500 focus:ring-1 focus:ring-cyan-500 transition-all font-mono"
          />
        </form>
      </div>

      <div className="flex items-center gap-3 lg:gap-4">
        {/* System Health Status */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span className="text-slate-400 font-mono">SOC Health:</span>
          <span className="text-emerald-400 font-semibold font-mono">100% ONLINE</span>
        </div>

        {/* AI & Blockchain Status Badges */}
        <div className="hidden xl:flex items-center gap-2">
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-950/40 border border-indigo-500/30 text-indigo-300 text-xs font-mono">
            <Cpu className="w-3.5 h-3.5 text-indigo-400" />
            <span>AI: GraphSAGE</span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-cyan-950/40 border border-cyan-500/30 text-cyan-300 text-xs font-mono">
            <CheckCircle className="w-3.5 h-3.5 text-cyan-400" />
            <span>PoA Ledger</span>
          </div>
        </div>

        {/* Notification Bell Dropdown */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 rounded-lg text-slate-400 hover:text-cyan-400 hover:bg-slate-800/80 transition-colors"
          >
            <Bell className="w-5 h-5" />
            {criticalAlerts.length > 0 && (
              <span className="absolute top-1 right-1 w-2.5 h-2.5 rounded-full bg-red-500 ring-2 ring-slate-950 animate-pulse" />
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-4 z-50 animate-in fade-in slide-in-from-top-2">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <span className="font-semibold text-sm text-slate-200">Active Threat Alerts</span>
                <Badge severity="CRITICAL">{criticalAlerts.length} Critical</Badge>
              </div>
              <div className="mt-3 space-y-2 max-h-64 overflow-y-auto">
                {alerts.slice(0, 4).map((alt) => (
                  <div
                    key={alt.id}
                    onClick={() => {
                      setShowNotifications(false);
                      navigate('/alerts');
                    }}
                    className="p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80 hover:border-cyan-500/40 cursor-pointer transition-all"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-slate-200 truncate">{alt.title}</span>
                      <Badge severity={alt.severity} size="sm">{alt.severity}</Badge>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-1 font-mono">{alt.source} &rarr; {alt.destination}</p>
                  </div>
                ))}
              </div>
              <button
                onClick={() => {
                  setShowNotifications(false);
                  navigate('/alerts');
                }}
                className="w-full mt-3 py-1.5 text-xs text-center text-cyan-400 hover:text-cyan-300 font-mono block bg-cyan-950/30 rounded-lg border border-cyan-500/20"
              >
                View all security alerts &rarr;
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;
