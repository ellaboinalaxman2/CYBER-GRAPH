import React from 'react';
import { Cpu, ShieldAlert, CheckCircle } from 'lucide-react';
import Badge from '../common/Badge';
import AnomalyScore from './AnomalyScore';
import ConfidenceScore from './ConfidenceScore';
import AIExplanation from './AIExplanation';

export const PredictionCard = ({
  predictionData,
  nodeId,
}) => {
  const isAttack = (predictionData?.prediction || 'ATTACK').toUpperCase() === 'ATTACK';

  return (
    <div className="p-5 rounded-2xl border border-slate-800 bg-slate-900/80 backdrop-blur-md space-y-4 font-mono shadow-xl">
      <div className="flex items-center justify-between pb-3 border-b border-slate-800">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-indigo-400" />
          <h4 className="text-sm font-bold text-slate-100">AI Intelligence Analysis</h4>
        </div>
        <Badge variant={isAttack ? 'danger' : 'success'}>
          {predictionData?.prediction || 'ATTACK'}
        </Badge>
      </div>

      {nodeId && (
        <p className="text-xs text-slate-400">
          Target Entity: <span className="text-cyan-400 font-bold">{nodeId}</span>
        </p>
      )}

      <AnomalyScore score={predictionData?.anomaly_score || 0.94} />
      <ConfidenceScore confidence={predictionData?.confidence || 0.93} />

      <AIExplanation
        explanations={predictionData?.explanations || [
          'Unusual login activity',
          'Abnormal connection pattern',
          'Suspicious neighboring node',
        ]}
        prediction={predictionData?.prediction || 'ATTACK'}
      />
    </div>
  );
};

export default PredictionCard;
