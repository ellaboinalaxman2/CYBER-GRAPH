import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Server,
  ShieldAlert,
  Flame,
  AlertOctagon,
  Activity,
  Network,
  CheckCircle2,
  Cpu,
  RefreshCw,
} from 'lucide-react';
import PageContainer from '../components/layout/PageContainer';
import StatsCard from '../components/dashboard/StatsCard';
import ThreatChart from '../components/dashboard/ThreatChart';
import RecentAlerts from '../components/dashboard/RecentAlerts';
import ThreatOverview from '../components/dashboard/ThreatOverview';
import AttackSummary from '../components/dashboard/AttackSummary';
import { useGraph } from '../hooks/useGraph';
import { useAlerts } from '../hooks/useAlerts';
import { useAttacks } from '../hooks/useAttacks';
import { MOCK_DASHBOARD_STATS, MOCK_THREAT_CHART_DATA } from '../services/mockData';
import Button from '../components/common/Button';
import UploadDataset from '../components/dashboard/UploadDataset';

export const Dashboard = () => {
  const navigate = useNavigate();
  const { nodes, edges, loading: graphLoading, fetchGraph } = useGraph();
  const { alerts, loading: alertsLoading, refetch: refetchAlerts } = useAlerts();
  const { attacks, loading: attacksLoading, refetch: refetchAttacks } = useAttacks();

  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = async () => {
    setRefreshing(true);
    await Promise.all([fetchGraph(), refetchAlerts(), refetchAttacks()]);
    setRefreshing(false);
  };

  const totalAssets = nodes.length > 0 ? nodes.length : MOCK_DASHBOARD_STATS.totalAssets;
  const activeAlerts = alerts.filter((a) => a.status === 'ACTIVE').length;
  const criticalThreats = alerts.filter((a) => a.severity === 'CRITICAL' && a.status === 'ACTIVE').length;
  const detectedAttacks = attacks.length;

  return (
    <PageContainer
      title="Security Operations Overview"
      subtitle="Real-time graph intelligence, threat correlation & autonomous attack detection"
      actions={
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            icon={RefreshCw}
            onClick={handleRefresh}
            disabled={refreshing}
          >
            {refreshing ? 'Syncing...' : 'Sync Telemetry'}
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={Network}
            onClick={() => navigate('/graph')}
          >
            Open Cyber Graph
          </Button>
        </div>
      }
    >
      <div className="space-y-6">
        {/* KPI Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatsCard
            title="Total Assets"
            value={totalAssets}
            change="+4 newly discovered"
            isPositive={true}
            icon={Server}
            variant="cyan"
            subtitle="Mapped in Neo4j Topology"
            onClick={() => navigate('/graph')}
          />

          <StatsCard
            title="Active Alerts"
            value={activeAlerts}
            change="+2 in last 10m"
            isPositive={false}
            icon={ShieldAlert}
            variant="warning"
            subtitle="Requires SOC triage"
            onClick={() => navigate('/alerts')}
          />

          <StatsCard
            title="Detected Attacks"
            value={detectedAttacks}
            change="1 active traversal"
            isPositive={false}
            icon={Flame}
            variant="critical"
            subtitle="Correlated by Attack Engine"
            onClick={() => navigate('/attacks')}
          />

          <StatsCard
            title="Critical Threats"
            value={criticalThreats}
            change="Immediate focus"
            isPositive={false}
            icon={AlertOctagon}
            variant="critical"
            subtitle="Lateral & data exfil paths"
            onClick={() => navigate('/alerts?severity=CRITICAL')}
          />
        </div>

        {/* Upload Dataset Section */}
        <UploadDataset onUploadComplete={handleRefresh} />

        {/* Threat Overview Banner */}
        <ThreatOverview stats={{ totalAssets, activeAlerts, criticalThreats, detectedAttacks }} />

        {/* Charts & Real-time Feeds */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Activity Chart */}
          <div className="lg:col-span-2 p-6 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm">
            <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
              <div>
                <h3 className="text-base font-bold text-slate-100">Threat Activity Telemetry</h3>
                <p className="text-xs font-mono text-slate-400">24-hour event timeline vs AI anomaly spikes</p>
              </div>
              <span className="text-xs font-mono text-cyan-400 bg-cyan-950/60 px-2.5 py-1 rounded-full border border-cyan-500/30">
                Live Feed
              </span>
            </div>

            <ThreatChart data={MOCK_THREAT_CHART_DATA} />
          </div>

          {/* Recent Alerts Feed */}
          <div className="p-6 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-sm flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
                <h3 className="text-base font-bold text-slate-100">Recent Security Alerts</h3>
                <button
                  onClick={() => navigate('/alerts')}
                  className="text-xs font-mono text-cyan-400 hover:underline"
                >
                  All Alerts &rarr;
                </button>
              </div>

              <RecentAlerts alerts={alerts.slice(0, 4)} />
            </div>

            <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] font-mono text-slate-500">
              <span>Member 1 UI View</span>
              <span>Updated 5s ago</span>
            </div>
          </div>
        </div>

        {/* Attack Campaigns Section */}
        <AttackSummary attacks={attacks} />
      </div>
    </PageContainer>
  );
};

export default Dashboard;
