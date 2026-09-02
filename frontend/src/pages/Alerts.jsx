import React, { useState } from 'react';
import PageContainer from '../components/layout/PageContainer';
import AlertFilters from '../components/alerts/AlertFilters';
import AlertList from '../components/alerts/AlertList';
import AlertDetails from '../components/alerts/AlertDetails';
import { useAlerts } from '../hooks/useAlerts';
import Button from '../components/common/Button';
import { RefreshCw } from 'lucide-react';

export const Alerts = () => {
  const { alerts, loading, filters, setFilters, updateStatus, refetch } = useAlerts();
  const [selectedAlert, setSelectedAlert] = useState(null);

  const handleFilterChange = (newFilters) => {
    setFilters((prev) => ({ ...prev, ...newFilters }));
  };

  const handleResetFilters = () => {
    setFilters({ severity: 'ALL', status: 'ALL', search: '' });
  };

  const currentSelected = selectedAlert || alerts[0];

  return (
    <PageContainer
      title="Alerts & Threat Incidents"
      subtitle="Real-time SOC alert triage, anomaly correlation & cryptographic verification"
      actions={
        <Button
          variant="secondary"
          size="sm"
          icon={RefreshCw}
          onClick={() => refetch()}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh Alerts'}
        </Button>
      }
    >
      <div className="space-y-6">
        {/* Filters */}
        <AlertFilters
          filters={filters}
          onFilterChange={handleFilterChange}
          onReset={handleResetFilters}
        />

        {/* Master - Detail Split View */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Left Column: Alert Feed */}
          <div className="lg:col-span-6 space-y-3">
            <AlertList
              alerts={alerts}
              selectedAlert={currentSelected}
              onSelectAlert={setSelectedAlert}
              loading={loading}
              onStatusChange={updateStatus}
            />
          </div>

          {/* Right Column: Forensic Inspector */}
          <div className="lg:col-span-6 sticky top-20">
            <AlertDetails
              alert={currentSelected}
              onStatusChange={updateStatus}
              onClose={() => setSelectedAlert(null)}
            />
          </div>
        </div>
      </div>
    </PageContainer>
  );
};

export default Alerts;
