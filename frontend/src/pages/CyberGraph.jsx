import React, { useState } from 'react';
import { Network, Layers, Sparkles, RefreshCw, Flame } from 'lucide-react';
import PageContainer from '../components/layout/PageContainer';
import CyberGraph from '../components/graph/CyberGraph';
import { useGraph } from '../hooks/useGraph';
import { useAttacks } from '../hooks/useAttacks';
import Button from '../components/common/Button';
import Loader from '../components/common/Loader';
import ErrorMessage from '../components/common/ErrorMessage';

export const CyberGraphPage = () => {
  const { nodes, edges, loading, error, fetchGraph, activeAttackPath, setAttackPath } = useGraph();
  const { attacks } = useAttacks();
  const [selectedAttackId, setSelectedAttackId] = useState('');

  const handleAttackSelect = (atkId) => {
    setSelectedAttackId(atkId);
    if (!atkId) {
      setAttackPath(null);
      return;
    }
    const found = attacks.find((a) => a.id === atkId);
    if (found) {
      setAttackPath(found);
    }
  };

  return (
    <PageContainer
      title="Cyber Graph Topology"
      subtitle="Interactive cybersecurity relationship graph with automated attack path highlighting"
      actions={
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Attack Path Simulator Dropdown */}
          <div className="flex items-center gap-1.5 bg-slate-900 border border-slate-800 rounded-lg px-3 py-1 text-xs font-mono">
            <Flame className="w-3.5 h-3.5 text-red-400" />
            <span className="text-slate-400">Attack Path Overlay:</span>
            <select
              value={selectedAttackId}
              onChange={(e) => handleAttackSelect(e.target.value)}
              className="bg-transparent text-slate-100 font-bold focus:outline-none cursor-pointer"
            >
              <option value="" className="bg-slate-900 text-slate-300">None (Full Topology)</option>
              {attacks.map((atk) => (
                <option key={atk.id} value={atk.id} className="bg-slate-900 text-red-400">
                  {atk.id} - {atk.title}
                </option>
              ))}
            </select>
          </div>

          <Button
            variant="secondary"
            size="sm"
            icon={RefreshCw}
            onClick={() => fetchGraph()}
            disabled={loading}
          >
            {loading ? 'Refreshing...' : 'Refresh Graph'}
          </Button>
        </div>
      }
    >
      <div className="space-y-4">
        {loading && nodes.length === 0 ? (
          <Loader text="Generating Cytoscape interactive graph topology..." className="py-32" />
        ) : error ? (
          <ErrorMessage message={error} onRetry={fetchGraph} />
        ) : (
          <CyberGraph
            nodes={nodes}
            edges={edges}
            activeAttackPath={activeAttackPath}
          />
        )}
      </div>
    </PageContainer>
  );
};

export default CyberGraphPage;
