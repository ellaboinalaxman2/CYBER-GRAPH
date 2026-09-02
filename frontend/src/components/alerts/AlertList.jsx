import React from 'react';
import AlertCard from './AlertCard';
import EmptyState from '../common/EmptyState';
import Loader from '../common/Loader';
import { ShieldCheck } from 'lucide-react';

export const AlertList = ({
  alerts = [],
  selectedAlert,
  onSelectAlert,
  loading = false,
  onStatusChange,
}) => {
  if (loading) {
    return <Loader text="Loading live security alerts..." className="py-16" />;
  }

  if (alerts.length === 0) {
    return (
      <EmptyState
        icon={ShieldCheck}
        title="Zero Security Alerts"
        description="No alerts matching current filter parameters. Network perimeter is calm."
      />
    );
  }

  return (
    <div className="space-y-3">
      {alerts.map((alert) => (
        <AlertCard
          key={alert.id}
          alert={alert}
          isSelected={selectedAlert?.id === alert.id}
          onSelect={onSelectAlert}
          onStatusChange={onStatusChange}
        />
      ))}
    </div>
  );
};

export default AlertList;
