import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Flame, RefreshCw, Network, ShieldAlert } from 'lucide-react';
import PageContainer from '../components/layout/PageContainer';
import AttackCard from '../components/attacks/AttackCard';
import { useAttacks } from '../hooks/useAttacks';
import Button from '../components/common/Button';
import Loader from '../components/common/Loader';
import EmptyState from '../components/common/EmptyState';

export const Attacks = () => {
  const navigate = useNavigate();
  const { attacks, loading, refetch } = useAttacks();

  return (
    <PageContainer
      title="Correlated Attack Campaigns"
      subtitle="Reconstructed multi-stage attack intrusions mapped against MITRE ATT&CK framework"
      actions={
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            icon={RefreshCw}
            onClick={() => refetch()}
            disabled={loading}
          >
            {loading ? 'Analyzing...' : 'Refresh Attacks'}
          </Button>
          <Button
            variant="primary"
            size="sm"
            icon={Network}
            onClick={() => navigate('/graph')}
          >
            Visual Graph
          </Button>
        </div>
      }
    >
      <div className="space-y-6">
        {loading ? (
          <Loader text="Reconstructing attack paths from Attack Engine..." className="py-20" />
        ) : attacks.length === 0 ? (
          <EmptyState
            icon={Flame}
            title="Zero Attack Campaigns"
            description="No lateral movement or exfiltration campaigns detected by Member 5 correlation engine."
          />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {attacks.map((attack) => (
              <AttackCard key={attack.id} attack={attack} />
            ))}
          </div>
        )}
      </div>
    </PageContainer>
  );
};

export default Attacks;
