import React, { useState } from 'react';
import { CheckCircle2, Shield, Search, RefreshCw, Layers } from 'lucide-react';
import PageContainer from '../components/layout/PageContainer';
import AuditTrail from '../components/blockchain/AuditTrail';
import TransactionDetails from '../components/blockchain/TransactionDetails';
import VerificationStatus from '../components/blockchain/VerificationStatus';
import { useBlockchain } from '../hooks/useBlockchain';
import Button from '../components/common/Button';
import Loader from '../components/common/Loader';
import Badge from '../components/common/Badge';

export const BlockchainAudit = () => {
  const { auditTrail, blockchainStatus, loading, refetch } = useBlockchain();
  const [selectedRecord, setSelectedRecord] = useState(null);
  const [searchFilter, setSearchFilter] = useState('');

  const filteredRecords = auditTrail.filter((r) => {
    if (!searchFilter) return true;
    const s = searchFilter.toLowerCase();
    return (
      r.eventId.toLowerCase().includes(s) ||
      r.txHash.toLowerCase().includes(s) ||
      r.hash.toLowerCase().includes(s)
    );
  });

  const activeRecord = selectedRecord || auditTrail[0];

  return (
    <PageContainer
      title="Blockchain Immutability & Audit Trail"
      subtitle="Cryptographic verification of security events powered by Member 6 distributed ledger"
      actions={
        <Button
          variant="secondary"
          size="sm"
          icon={RefreshCw}
          onClick={() => refetch()}
          disabled={loading}
        >
          {loading ? 'Validating...' : 'Sync Ledger State'}
        </Button>
      }
    >
      <div className="space-y-6">
        {/* Blockchain Status Overview Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 font-mono text-xs">
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-slate-500 uppercase block mb-1">Ledger Network</span>
            <span className="text-base font-bold text-cyan-400">CyberGraph-PoA</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-slate-500 uppercase block mb-1">Current Block Height</span>
            <span className="text-base font-bold text-slate-100">#1,849,220</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-slate-500 uppercase block mb-1">Verified Telemetry Records</span>
            <span className="text-base font-bold text-emerald-400">14,248 (100%)</span>
          </div>

          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
            <span className="text-slate-500 uppercase block mb-1">Consensus Confirmation</span>
            <span className="text-base font-bold text-slate-100">&lt; 0.8s</span>
          </div>
        </div>

        {/* Search Bar for Hashes / Events */}
        <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex items-center justify-between gap-4">
          <div className="relative flex-1 max-w-md">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by event ID, Tx hash, or SHA-256 digest..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder:text-slate-600 focus:outline-none focus:border-cyan-500 font-mono"
            />
          </div>
          <Badge variant="success" dot>PoA Network Online</Badge>
        </div>

        {/* 2-Column Split: Audit Trail Table & Forensic Proof */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div className="lg:col-span-7">
            {loading ? (
              <Loader text="Querying blockchain ledger nodes..." className="py-16" />
            ) : (
              <AuditTrail
                auditRecords={filteredRecords}
                onSelectRecord={setSelectedRecord}
                selectedRecordId={activeRecord?.eventId}
              />
            )}
          </div>

          <div className="lg:col-span-5 sticky top-20 space-y-4">
            {activeRecord && (
              <>
                <VerificationStatus
                  eventId={activeRecord.eventId}
                  verified={activeRecord.status === 'VERIFIED'}
                  transactionHash={activeRecord.txHash}
                  timestamp={activeRecord.timestamp}
                  blockNumber={activeRecord.blockNumber}
                />
                <TransactionDetails tx={activeRecord} />
              </>
            )}
          </div>
        </div>
      </div>
    </PageContainer>
  );
};

export default BlockchainAudit;
