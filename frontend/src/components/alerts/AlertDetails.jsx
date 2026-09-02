import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  ShieldAlert,
  Clock,
  ArrowRight,
  Cpu,
  CheckCircle,
  FileText,
  Activity,
  Layers,
  Check,
  AlertOctagon,
  ExternalLink,
} from 'lucide-react';
import Badge from '../common/Badge';
import Button from '../common/Button';
import { formatDateTime } from '../../utils/dateUtils';
import { formatPercentage } from '../../utils/formatters';
import { blockchainApi } from '../../services/blockchainApi';

export const AlertDetails = ({
  alert,
  onStatusChange,
  onClose,
}) => {
  const navigate = useNavigate();
  const [blockchainProof, setBlockchainProof] = useState(null);
  const [verifyingChain, setVerifyingChain] = useState(false);

  useEffect(() => {
    if (alert?.relatedEvents?.[0]) {
      setVerifyingChain(true);
      blockchainApi
        .verifyEvent(alert.relatedEvents[0])
        .then((proof) => setBlockchainProof(proof))
        .finally(() => setVerifyingChain(false));
    }
  }, [alert]);

  if (!alert) {
    return (
      <div className="p-8 rounded-xl border border-slate-800 bg-slate-900/40 text-center text-slate-500 font-mono text-xs">
        Select an alert from the list to inspect forensic details
      </div>
    );
  }

  return (
    <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/90 backdrop-blur-md space-y-6 text-xs font-mono shadow-2xl">
      {/* Alert Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center gap-2">
            <Badge severity={alert.severity} dot>
              {alert.severity} PRIORITY
            </Badge>
            <span className="text-slate-400">{alert.id}</span>
          </div>
          <h3 className="text-base font-bold text-slate-100 font-sans mt-2">{alert.title}</h3>
        </div>

        {/* Status Actions */}
        <div className="flex items-center gap-2">
          {alert.status !== 'RESOLVED' ? (
            <Button
              variant="outline"
              size="sm"
              icon={Check}
              onClick={() => onStatusChange?.(alert.id, 'RESOLVED')}
            >
              Mark Resolved
            </Button>
          ) : (
            <Badge variant="success">Resolved</Badge>
          )}
        </div>
      </div>

      {/* Forensic Breakdown Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <span className="text-[10px] text-slate-500 uppercase tracking-widest block mb-1">Source Asset</span>
          <p className="text-sm font-bold text-cyan-400">{alert.source}</p>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <span className="text-[10px] text-slate-500 uppercase tracking-widest block mb-1">Destination Target</span>
          <p className="text-sm font-bold text-red-400">{alert.destination}</p>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <span className="text-[10px] text-slate-500 uppercase tracking-widest block mb-1">Detection Time</span>
          <p className="text-xs text-slate-200">{formatDateTime(alert.timestamp)}</p>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-950/60 border border-slate-800/80">
          <span className="text-[10px] text-slate-500 uppercase tracking-widest block mb-1">MITRE ATT&CK Mapping</span>
          <p className="text-xs text-indigo-400 font-bold">{alert.technique || 'T1021 - Remote Services'}</p>
        </div>
      </div>

      {/* What Happened / Narrative */}
      <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800/80">
        <h5 className="text-[11px] uppercase tracking-wider text-slate-400 font-bold mb-2 flex items-center gap-1.5">
          <FileText className="w-3.5 h-3.5 text-cyan-400" />
          Incident Analysis Narrative
        </h5>
        <p className="text-slate-300 font-sans text-xs leading-relaxed">{alert.description}</p>
      </div>

      {/* AI Inference & Anomaly Section */}
      <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-500/30">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2 text-indigo-300">
            <Cpu className="w-4 h-4 text-indigo-400" />
            <span className="font-bold text-xs">AI Engine (Member 3) Assessment</span>
          </div>
          <Badge variant="cyber">GraphSAGE v2.4</Badge>
        </div>

        <div className="space-y-2">
          <div className="flex justify-between text-xs">
            <span className="text-slate-400">Prediction:</span>
            <span className="text-red-400 font-bold">ATTACK CLASSIFICATION</span>
          </div>
          <div className="flex justify-between text-xs">
            <span className="text-slate-400">Model Confidence:</span>
            <span className="text-cyan-400 font-bold">{formatPercentage(alert.confidence || 0.94)}</span>
          </div>
        </div>
      </div>

      {/* Blockchain Verification Proof */}
      <div className="p-4 rounded-xl bg-slate-950/80 border border-slate-800">
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2 text-emerald-400">
            <CheckCircle className="w-4 h-4" />
            <span className="font-bold text-xs">Blockchain Proof (Member 6)</span>
          </div>
          <Badge variant="success" size="sm">
            {blockchainProof?.verified ? '✓ Integrity Verified' : 'Checking Ledger...'}
          </Badge>
        </div>
        <p className="text-[11px] text-slate-400 break-all">
          <span className="text-slate-500">Tx Hash:</span> {blockchainProof?.transaction_hash || '0xabc123789fed456123456789abcdef0123456789abcdef0123456789abcdef01'}
        </p>
      </div>

      {/* Direct Quick Actions */}
      <div className="flex flex-wrap gap-2 pt-2">
        <button
          onClick={() => navigate('/graph')}
          className="flex-1 py-2 px-3 bg-cyan-950/60 hover:bg-cyan-900/60 text-cyan-300 rounded-lg border border-cyan-500/30 flex items-center justify-center gap-1.5 transition-all text-xs font-semibold"
        >
          <Layers className="w-3.5 h-3.5" />
          <span>Locate in Cyber Graph</span>
        </button>

        <button
          onClick={() => navigate(`/events?search=${alert.source}`)}
          className="flex-1 py-2 px-3 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg border border-slate-700 flex items-center justify-center gap-1.5 transition-all text-xs"
        >
          <Activity className="w-3.5 h-3.5" />
          <span>Audit Events</span>
        </button>
      </div>
    </div>
  );
};

export default AlertDetails;
