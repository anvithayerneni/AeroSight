import React, { useState, useEffect } from 'react';
import { Layout } from './components/Layout';
import { PageId } from './components/Sidebar';
import { DashboardPage } from './pages/DashboardPage';
import { FlightsPage } from './pages/FlightsPage';
import { AirportsPage } from './pages/AirportsPage';
import { RoutesPage } from './pages/RoutesPage';
import { DelayAnalyticsPage } from './pages/DelayAnalyticsPage';
import { RealTimeOpsPage } from './pages/RealTimeOpsPage';
import { MLPredictionsPage } from './pages/MLPredictionsPage';
import { ReportsPage } from './pages/ReportsPage';
import { LiveTelemetryEvent } from './services/types';

export const App: React.FC = () => {
  const [activePage, setActivePage] = useState<PageId>('dashboard');
  const [liveEvents, setLiveEvents] = useState<LiveTelemetryEvent[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Connect to SSE stream
  useEffect(() => {
    const eventSource = new EventSource('/api/streaming/live-events');

    eventSource.onmessage = (event) => {
      try {
        const parsed: LiveTelemetryEvent = JSON.parse(event.data);
        setLiveEvents((prev) => [parsed, ...prev.slice(0, 49)]); // Keep last 50 events
      } catch (err) {
        console.error('Error parsing SSE telemetry event:', err);
      }
    };

    eventSource.onerror = () => {
      // EventSource auto-retries automatically
    };

    return () => {
      eventSource.close();
    };
  }, []);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setTimeout(() => {
      setIsRefreshing(false);
      window.location.reload();
    }, 600);
  };

  const renderContent = () => {
    switch (activePage) {
      case 'dashboard':
        return <DashboardPage liveEvents={liveEvents} />;
      case 'flights':
        return <FlightsPage />;
      case 'airports':
        return <AirportsPage />;
      case 'routes':
        return <RoutesPage />;
      case 'delays':
        return <DelayAnalyticsPage />;
      case 'realtime':
        return <RealTimeOpsPage liveEvents={liveEvents} />;
      case 'ml':
        return <MLPredictionsPage />;
      case 'reports':
        return <ReportsPage />;
      default:
        return <DashboardPage liveEvents={liveEvents} />;
    }
  };

  return (
    <Layout
      activePage={activePage}
      onSelectPage={setActivePage}
      onRefresh={handleRefresh}
      isRefreshing={isRefreshing}
    >
      {renderContent()}
    </Layout>
  );
};

export default App;
