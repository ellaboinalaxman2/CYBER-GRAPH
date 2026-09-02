import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Shield, Lock, Mail, User, ShieldCheck, ArrowRight } from 'lucide-react';
import { useAuth } from '../hooks/useAuth';
import Button from '../components/common/Button';

export const Register = () => {
  const navigate = useNavigate();
  const { register, loading } = useAuth();

  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('viewer');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
      await register({ username, email, role, password });
      navigate('/dashboard');
    } catch (err) {
      setError(err.message || 'Registration failed.');
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0d14] flex flex-col justify-center py-12 sm:px-6 lg:px-8 relative overflow-hidden">
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-cyan-900/20 via-slate-950 to-[#0a0d14] pointer-events-none" />

      <div className="sm:mx-auto sm:w-full sm:max-w-md relative z-10">
        <div className="flex justify-center">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-cyan-500/20 via-blue-500/20 to-indigo-500/30 border border-cyan-500/40 flex items-center justify-center shadow-2xl shadow-cyan-500/20">
            <ShieldCheck className="w-8 h-8 text-cyan-400" />
          </div>
        </div>

        <h2 className="mt-6 text-center text-3xl font-extrabold tracking-tight text-slate-100 font-sans">
          Analyst Enrollment
        </h2>
        <p className="mt-2 text-center text-xs font-mono text-cyan-400/90 tracking-wider uppercase">
          Create Cyber Graph SOC Operational Account
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md relative z-10 px-4 sm:px-0">
        <div className="bg-slate-900/80 backdrop-blur-xl py-8 px-6 sm:px-10 rounded-2xl border border-slate-800 shadow-2xl shadow-cyan-950/40">
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="p-3 rounded-lg bg-red-950/40 border border-red-500/40 text-red-300 text-xs font-mono">
                {error}
              </div>
            )}

            <div>
              <label className="block text-xs font-mono text-slate-300 uppercase tracking-wider mb-2">
                Analyst Full Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs sm:text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 font-mono"
                  placeholder="analyst01"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-300 uppercase tracking-wider mb-2">
                Official Email
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs sm:text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 font-mono"
                  placeholder="analyst@cybergraph.security"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-300 uppercase tracking-wider mb-2">
                Operational Role
              </label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3 py-2 text-xs sm:text-sm text-slate-200 focus:outline-none focus:border-cyan-500 font-mono"
              >
                <option value="viewer">Viewer</option>
                <option value="analyst">Security Analyst</option>
                <option value="admin">Administrator</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-mono text-slate-300 uppercase tracking-wider mb-2">
                Access Token / Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 text-slate-500 absolute left-3 top-1/2 -translate-y-1/2" />
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-2 text-xs sm:text-sm text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 font-mono"
                  placeholder="••••••••••••"
                />
              </div>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="lg"
              disabled={loading}
              className="w-full mt-3"
              icon={ArrowRight}
            >
              {loading ? 'Creating Credentials...' : 'Register Operator Profile'}
            </Button>
          </form>

          <div className="mt-6 pt-6 border-t border-slate-800/80 flex items-center justify-between text-xs font-mono">
            <span className="text-slate-500">Already registered?</span>
            <Link to="/login" className="text-cyan-400 hover:text-cyan-300 font-bold">
              Sign In to Console &rarr;
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
