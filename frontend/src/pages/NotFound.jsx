import React from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldAlert, Home, ArrowLeft } from 'lucide-react';
import Button from '../components/common/Button';

export const NotFound = () => {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#0a0d14] flex flex-col items-center justify-center p-6 text-center font-mono relative overflow-hidden">
      <div className="w-20 h-20 rounded-2xl bg-red-500/10 border border-red-500/30 flex items-center justify-center mb-6 text-red-400 shadow-2xl shadow-red-500/20">
        <ShieldAlert className="w-10 h-10 animate-bounce" />
      </div>

      <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-100 tracking-tight">
        404 — UNRESOLVED ROUTE
      </h1>
      <p className="mt-3 text-sm text-slate-400 max-w-md font-sans">
        The requested cybersecurity endpoint does not exist or has been quarantined by perimeter policy.
      </p>

      <div className="mt-8 flex items-center gap-3">
        <Button variant="secondary" icon={ArrowLeft} onClick={() => navigate(-1)}>
          Return Previous
        </Button>
        <Button variant="primary" icon={Home} onClick={() => navigate('/dashboard')}>
          SOC Dashboard
        </Button>
      </div>
    </div>
  );
};

export default NotFound;
