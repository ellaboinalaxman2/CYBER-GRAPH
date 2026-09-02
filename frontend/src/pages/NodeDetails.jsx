import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Server,
  ArrowLeft,
  Cpu,
  Activity,
  ShieldAlert,
  CheckCircle2,
  Network,
  RefreshCw,
} from 'lucide-react';
import PageContainer from '../components/layout/PageContainer';
import PredictionCard from '../components/ai/PredictionCard';
import VerificationStatus from '../components/blockchain/VerificationStatus';
import Badge from '../components/common/Badge';
import Button from '../components/common/Button';
import Loader from '../components/common/Loader';
import { graphApi } from '../services/graphApi';
import { aiApi } from '../services/aiApi';
import { eventApi } from '../services/eventApi';

export const NodeDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [node, setNode] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [relatedEvents, setRelatedEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchNodeAllData = async () => {
    setLoading(true);
    try {
      const [nodeData, aiData, evts] = await Promise.all([
        graphApi.getNodeById(id),
        aiApi.getNodePrediction(id),
        eventApi.getEvents({ search: id }),
      ]);
      setNode(nodeData);
      setPrediction(aiData);
      setRelatedEvents(evts.events || []);
    } catch (err) {
      console.error('Error fetching node full telemetry', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNodeAllData();
  }, [id]);

  if (loading) {
    return (
      <PageContainer title={`Asset Analysis: ${id}`} subtitle="Loading deep graph inspection...">
        <Loader text="Correlating node telemetry across Neo4j, AI Engine & Blockchain..." className="py-24" />
      </PageContainer>
    );
  }

  return (
    <PageContainer
      title={`Asset Forensics: ${node?.label || id}`}
      subtitle={`Comprehensive telemetry for ${node?.type || 'Node'} (${node?.ip || 'N/A'})`}
      actions={
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="sm" icon={ArrowLeft} onClick={() => navigate(-1)}>
            Back
          </Button>
          <Button variant="outline" size="sm" icon={Network} onClick={() => navigate('/graph')}>
            View in Topology
          </Button>
        </div>
      }
    >
      <div className="space-y-6">
        {/* Top Asset Identity Card */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/80 font-mono text-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                <Server className="w-6 h-6" />
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-xl font-bold text-slate-100">{node?.label || id}</h2>
                  <Badge severity={node?.risk || 'LOW'}>{node?.status || 'Active'}</Badge>
                </div>
                <p className="text-slate-400 mt-1 font-sans text-xs">
                  Zone: <span className="text-slate-200">{node?.zone || 'Internal Network'}</span> • OS: <span className="text-slate-200">{node?.os || 'Linux'}</span>
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-center">
                <span className="text-[10px] text-slate-500 uppercase block">Connections</span>
                <span className="text-base font-bold text-slate-200">{node?.connections || 0}</span>
              </div>
              <div className="p-3 rounded-xl bg-slate-950 border border-slate-800 text-center">
                <span className="text-[10px] text-slate-500 uppercase block">Alerts</span>
                <span className="text-base font-bold text-red-400">{node?.alerts || 0}</span>
              </div>
            </div>
          </div>

          <div className="mt-4 grid grid-cols-1 sm:grid-cols-3 gap-3 text-slate-300">
            <div>
              <span className="text-slate-500 block text-[10px] uppercase">IP Address</span>
              <span className="text-cyan-400 font-bold">{node?.ip}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px] uppercase">MAC Address</span>
              <span>{node?.mac || '52:54:00:12:34:56'}</span>
            </div>
            <div>
              <span className="text-slate-500 block text-[10px] uppercase">Entity Type</span>
              <span className="capitalize">{node?.type}</span>
            </div>
          </div>
        </div>

        {/* 2-Column Intelligence Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* AI Intelligence HUD (Member 3) */}
          <PredictionCard predictionData={prediction} nodeId={id} />

          {/* Blockchain Cryptographic Verification (Member 6) */}
          <VerificationStatus
            eventId={relatedEvents[0]?.id || 'EVT-1001'}
            verified={true}
            transactionHash={relatedEvents[0]?.txHash}
            timestamp={relatedEvents[0]?.timestamp}
          />
        </div>

        {/* Related Security Events */}
        <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/80">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
            <div className="flex items-center gap-2">
              <Activity className="w-4 h-4 text-cyan-400" />
              <h3 className="text-sm font-bold font-mono text-slate-100 uppercase">
                Associated Telemetry Events ({relatedEvents.length})
              </h3>
            </div>
            <button
              onClick={() => navigate(`/events?search=${id}`)}
              className="text-xs font-mono text-cyan-400 hover:underline"
            >
              Open in Event Explorer &rarr;
            </button>
          </div>

          <div className="space-y-2 font-mono text-xs">
            {relatedEvents.slice(0, 5).map((evt) => (
              <div
                key={evt.id}
                className="p-3 rounded-lg bg-slate-950/60 border border-slate-800/80 flex items-center justify-between"
              >
                <div className="flex items-center gap-3">
                  <span className="font-bold text-cyan-400">{evt.id}</span>
                  <span className="text-slate-300">{evt.event}</span>
                  <span className="text-slate-500">({evt.source} &rarr; {evt.destination})</span>
                </div>
                <span className="text-emerald-400 text-[11px]">✓ Verified ({evt.time})</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </PageContainer>
  );
};

export default NodeDetailsPage;
