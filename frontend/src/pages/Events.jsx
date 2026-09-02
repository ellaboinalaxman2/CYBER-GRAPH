import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Activity, RefreshCw } from 'lucide-react';
import PageContainer from '../components/layout/PageContainer';
import EventTable from '../components/events/EventTable';
import EventFilters from '../components/events/EventFilters';
import EventDetails from '../components/events/EventDetails';
import { useEvents } from '../hooks/useEvents';
import Button from '../components/common/Button';
import Loader from '../components/common/Loader';
import EmptyState from '../components/common/EmptyState';

export const Events = () => {
  const [searchParams] = useSearchParams();
  const initialSearch = searchParams.get('search') || '';

  const { events, loading, filters, setFilters, refetch } = useEvents({
    search: initialSearch,
    status: 'ALL',
  });

  const [selectedEvent, setSelectedEvent] = useState(null);

  useEffect(() => {
    if (initialSearch) {
      setFilters((prev) => ({ ...prev, search: initialSearch }));
    }
  }, [initialSearch, setFilters]);

  const handleFilterChange = (newF) => {
    setFilters((prev) => ({ ...prev, ...newF }));
  };

  const handleReset = () => {
    setFilters({ search: '', status: 'ALL' });
  };

  return (
    <PageContainer
      title="Normalized Security Events"
      subtitle="Clean telemetry ingested from Member 2 & cryptographically verified on Member 6 blockchain"
      actions={
        <Button
          variant="secondary"
          size="sm"
          icon={RefreshCw}
          onClick={() => refetch()}
          disabled={loading}
        >
          {loading ? 'Refreshing...' : 'Refresh Events'}
        </Button>
      }
    >
      <div className="space-y-6">
        {/* Filters */}
        <EventFilters
          filters={filters}
          onFilterChange={handleFilterChange}
          onReset={handleReset}
        />

        {/* Master - Detail Split if Event Selected */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div className={selectedEvent ? 'lg:col-span-8' : 'lg:col-span-12'}>
            {loading ? (
              <Loader text="Fetching security event stream..." className="py-16" />
            ) : events.length === 0 ? (
              <EmptyState
                icon={Activity}
                title="No Events Found"
                description="No telemetry logs matching the current criteria."
              />
            ) : (
              <EventTable
                events={events}
                selectedEventId={selectedEvent?.id}
                onSelectEvent={setSelectedEvent}
              />
            )}
          </div>

          {selectedEvent && (
            <div className="lg:col-span-4 sticky top-20">
              <EventDetails
                event={selectedEvent}
                onClose={() => setSelectedEvent(null)}
              />
            </div>
          )}
        </div>
      </div>
    </PageContainer>
  );
};

export default Events;
