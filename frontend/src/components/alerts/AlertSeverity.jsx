import React from 'react';
import Badge from '../common/Badge';
import { getSeverityConfig } from '../../utils/severityUtils';

export const AlertSeverity = ({ severity = 'INFO', showLabel = true, size = 'md' }) => {
  const config = getSeverityConfig(severity);

  return (
    <div className="inline-flex items-center gap-2">
      <Badge severity={severity} size={size} dot>
        {showLabel ? config.label : ''}
      </Badge>
    </div>
  );
};

export default AlertSeverity;
