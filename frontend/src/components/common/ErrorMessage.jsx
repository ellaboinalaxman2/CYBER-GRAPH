import React from 'react';
import { AlertTriangle, RefreshCw } from 'lucide-react';
import Button from './Button';

export const ErrorMessage = ({
  message = 'An unexpected security telemetry error occurred',
  onRetry,
  className = '',
}) => {
  return (
    <div
      className={`p-6 rounded-xl border border-red-500/30 bg-red-950/20 flex flex-col items-center justify-center text-center gap-3 ${className}`}
    >
      <div className="p-3 rounded-full bg-red-500/10 text-red-400 border border-red-500/20">
        <AlertTriangle className="w-6 h-6" />
      </div>
      <p className="text-sm text-red-200 font-mono">{message}</p>
      {onRetry && (
        <Button variant="secondary" size="sm" onClick={onRetry} icon={RefreshCw}>
          Retry Connection
        </Button>
      )}
    </div>
  );
};

export default ErrorMessage;
