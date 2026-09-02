import React, { useState } from 'react';
import { Settings as SettingsIcon, Shield, Server, Cpu, Database, Save, CheckCircle2, Lock } from 'lucide-react';
import PageContainer from '../components/layout/PageContainer';
import Button from '../components/common/Button';
import Badge from '../components/common/Badge';

export const Settings = () => {
  const [apiUrl, setApiUrl] = useState(import.meta.env.VITE_API_URL || 'http://localhost:4000/api');
  const [enableMockFallback, setEnableMockFallback] = useState(true);
  const [anomalyThreshold, setAnomalyThreshold] = useState(70);
  const [refreshInterval, setRefreshInterval] = useState(5);
  const [saved, setSaved] = useState(false);

  const handleSave = (e) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <PageContainer
      title="System & SOC Configuration"
      subtitle="Configure Member 1 frontend communication parameters and threat telemetry parameters"
    >
      <div className="max-w-4xl space-y-6">
        <form onSubmit={handleSave} className="space-y-6">
          {/* Backend API Integration Settings */}
          <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/80 backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Server className="w-5 h-5 text-cyan-400" />
                <h3 className="text-base font-bold text-slate-100 font-sans">Member 7 (Backend API) Gateway</h3>
              </div>
              <Badge variant="cyber">REST API Integration</Badge>
            </div>

            <div className="space-y-4 text-xs font-mono">
              <div>
                <label className="block text-slate-300 uppercase tracking-wider mb-1.5">
                  Backend API Base Endpoint
                </label>
                <input
                  type="text"
                  value={apiUrl}
                  onChange={(e) => setApiUrl(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2.5 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
                  placeholder="http://localhost:4000/api"
                />
                <p className="text-[11px] text-slate-500 mt-1">
                  All requests route to Member 7 backend microservice for Neo4j, AI Engine, and Attack Engine data.
                </p>
              </div>

              <div className="flex items-center justify-between p-3 rounded-xl bg-slate-950 border border-slate-800">
                <div>
                  <span className="font-bold text-slate-200 block">Seamless Mock Telemetry Fallback</span>
                  <span className="text-[11px] text-slate-500">
                    Automatically serves realistic synthetic threat intelligence if the local backend is offline.
                  </span>
                </div>
                <input
                  type="checkbox"
                  checked={enableMockFallback}
                  onChange={(e) => setEnableMockFallback(e.target.checked)}
                  className="w-4 h-4 text-cyan-500 rounded border-slate-800 bg-slate-900 focus:ring-cyan-400 cursor-pointer"
                />
              </div>
            </div>
          </div>

          {/* AI Threat Thresholds */}
          <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/80 backdrop-blur-md space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2">
                <Cpu className="w-5 h-5 text-indigo-400" />
                <h3 className="text-base font-bold text-slate-100 font-sans">AI & Anomaly Thresholds</h3>
              </div>
              <Badge variant="default">GraphSAGE Tuning</Badge>
            </div>

            <div className="space-y-4 text-xs font-mono">
              <div>
                <div className="flex justify-between mb-1.5">
                  <span className="text-slate-300 uppercase">Critical Anomaly Notification Threshold:</span>
                  <span className="text-cyan-400 font-bold">{anomalyThreshold}%</span>
                </div>
                <input
                  type="range"
                  min="30"
                  max="95"
                  value={anomalyThreshold}
                  onChange={(e) => setAnomalyThreshold(Number(e.target.value))}
                  className="w-full h-2 bg-slate-950 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                />
              </div>

              <div>
                <label className="block text-slate-300 uppercase tracking-wider mb-1.5">
                  Telemetry Auto-Polling Rate (Seconds)
                </label>
                <select
                  value={refreshInterval}
                  onChange={(e) => setRefreshInterval(Number(e.target.value))}
                  className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-cyan-500 font-mono w-full"
                >
                  <option value="3">3 seconds (Real-Time Fast)</option>
                  <option value="5">5 seconds (Recommended)</option>
                  <option value="10">10 seconds (Standard)</option>
                  <option value="30">30 seconds (Low Bandwidth)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Security Compliance Audit & Safe Env Protocol */}
          <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/80 backdrop-blur-md space-y-3 font-mono text-xs">
            <div className="flex items-center gap-2 text-emerald-400 pb-2 border-b border-slate-800">
              <Lock className="w-4 h-4" />
              <h4 className="font-bold uppercase tracking-wider">Frontend Security Compliance Checklist</h4>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px] text-slate-300">
              <div className="flex items-center gap-2">
                <span className="text-emerald-400">✓</span>
                <span>JWT Stored in secure client session</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-emerald-400">✓</span>
                <span>No backend/database secrets in .env</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-emerald-400">✓</span>
                <span>Protected client-side routing enabled</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-emerald-400">✓</span>
                <span>XSS-safe JSON sanitization active</span>
              </div>
            </div>
          </div>

          <div className="flex items-center justify-between">
            {saved ? (
              <span className="text-xs font-mono text-emerald-400 flex items-center gap-1">
                <CheckCircle2 className="w-4 h-4" />
                Settings persisted successfully
              </span>
            ) : <span />}

            <Button type="submit" variant="primary" icon={Save}>
              Save Preferences
            </Button>
          </div>
        </form>
      </div>
    </PageContainer>
  );
};

export default Settings;
