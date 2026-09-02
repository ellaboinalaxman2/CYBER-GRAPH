import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, RefreshCw, Network } from 'lucide-react';
import PageContainer from '../components/layout/PageContainer';
import AttackDetails from '../components/attacks/AttackDetails';
import { attackApi } from '../services/attackApi';
import Button from '../components/common/Button';
import Loader from '../components/common/Loader';
import ErrorMessage from '../components/common/ErrorMessage';

export const AttackDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [attack, setAttack] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAttack = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await attackApi.getAttackById(id);
      setAttack(data);
    } catch (err) {
      setError(err.message || 'Failed to load attack details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAttack();
  }, [id]);

  return (
    <PageContainer
      title={attack ? `${attack.id}: ${attack.title}` : 'Attack Campaign Details'}
      subtitle="Deep forensic dissection of attack stages, MITRE mapping & lateral traversal"
      actions={
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            icon={ArrowLeft}
            onClick={() => navigate('/attacks')}
          >
            Back to Attacks
          </Button>
          <Button
            variant="outline"
            size="sm"
            icon={RefreshCw}
            onClick={fetchAttack}
            disabled={loading}
          >
            Refresh
          </Button>
        </div>
      }
    >
      <div className="space-y-6">
        {loading ? (
          <Loader text="Loading campaign telemetry & forensic artifacts..." className="py-24" />
        ) : error ? (
          <ErrorMessage message={error} onRetry={fetchAttack} />
        ) : (
          <AttackDetails attack={attack} />
        )}
      </div>
    </PageContainer>
  );
};

export default AttackDetailsPage;
