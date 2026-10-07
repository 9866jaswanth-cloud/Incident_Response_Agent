import { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import GuidedDemoBar from './components/GuidedDemoBar';
import DashboardView from './components/DashboardView';
import IncidentsView from './components/IncidentsView';
import IncidentConsoleView from './components/IncidentConsoleView';
import MemoryTimelineView from './components/MemoryTimelineView';
import LearningLoopModal from './components/LearningLoopModal';
import { Incident, MemoryStatus, MemoryTimelineEvent } from './types';
import api from './services/api';

export default function App() {
  const [currentTab, setCurrentTab] = useState<'dashboard' | 'incidents' | 'investigate' | 'timeline'>('dashboard');
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [memoryStatus, setMemoryStatus] = useState<MemoryStatus | null>(null);
  const [recentEvents, setRecentEvents] = useState<MemoryTimelineEvent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [demoMode, setDemoMode] = useState<boolean>(true);
  const [isResetting, setIsResetting] = useState<boolean>(false);
  const [isLearningLoopOpen, setIsLearningLoopOpen] = useState<boolean>(false);
  const [notification, setNotification] = useState<{ message: string; type: 'success' | 'info' | 'error' } | null>(null);

  // Load initial data
  const loadData = async () => {
    try {
      const [incidentsRes, memStatus, timelineRes] = await Promise.allSettled([
        api.getIncidents({ limit: 50 }),
        api.getMemoryStatus(),
        api.getMemoryTimeline(10),
      ]);

      if (incidentsRes.status === 'fulfilled') {
        setIncidents(incidentsRes.value.items);
      }
      if (memStatus.status === 'fulfilled') {
        setMemoryStatus(memStatus.value);
      }
      if (timelineRes.status === 'fulfilled') {
        setRecentEvents(timelineRes.value.events);
      }
    } catch (err) {
      console.error('Error loading initial app data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // Poll memory status periodically
    const interval = setInterval(() => {
      api.getMemoryStatus().then(setMemoryStatus).catch(console.error);
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  // Handle select incident
  const handleSelectIncident = (id: string) => {
    setSelectedIncidentId(id);
    setCurrentTab('investigate');
  };

  // Handle demo reset
  const handleResetDemo = async () => {
    if (!window.confirm('Reset demo incidents (INC-001, INC-002, INC-003) to fresh unconfirmed/un-retained state?')) {
      return;
    }
    setIsResetting(true);
    try {
      await api.resetDemo();
      await loadData();
      setNotification({
        message: 'Demo state successfully reset to initial unconfirmed baseline.',
        type: 'success',
      });
      setTimeout(() => setNotification(null), 5000);
    } catch (err: any) {
      console.error('Failed to reset demo:', err);
      setNotification({
        message: 'Failed to reset demo state: ' + (err.message || 'unknown error'),
        type: 'error',
      });
      setTimeout(() => setNotification(null), 5000);
    } finally {
      setIsResetting(false);
    }
  };

  // Handle incident update from console
  const handleIncidentUpdated = (updated: Incident) => {
    setIncidents((prev) => prev.map((inc) => (inc.id === updated.id ? updated : inc)));
    // Refresh memory timeline
    api.getMemoryTimeline(10).then((res) => setRecentEvents(res.events)).catch(console.error);
  };

  const selectedIncident = incidents.find((i) => i.id === selectedIncidentId);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-indigo-500 selection:text-white">
      {/* Top Navigation */}
      <Navbar
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        memoryStatus={memoryStatus}
        onResetDemo={handleResetDemo}
        isResetting={isResetting}
        demoMode={demoMode}
        setDemoMode={setDemoMode}
      />

      {/* Guided 3-Step Demo Story Bar */}
      {demoMode && (
        <GuidedDemoBar
          incidents={incidents}
          onSelectIncident={handleSelectIncident}
          selectedIncidentId={selectedIncidentId}
          onOpenLearningLoop={() => setIsLearningLoopOpen(true)}
        />
      )}

      {/* Notification Toast */}
      {notification && (
        <div
          className={`px-6 py-2.5 text-xs font-semibold text-center transition-all ${
            notification.type === 'success'
              ? 'bg-emerald-950/90 text-emerald-300 border-b border-emerald-800'
              : 'bg-rose-950/90 text-rose-300 border-b border-rose-800'
          }`}
        >
          {notification.message}
        </div>
      )}

      {/* Main Content Viewport */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-6">
        {currentTab === 'dashboard' && (
          <DashboardView
            incidents={incidents}
            memoryStatus={memoryStatus}
            recentEvents={recentEvents}
            onSelectIncident={handleSelectIncident}
            onNavigateTab={setCurrentTab}
            onStartDemo={() => {
              setDemoMode(true);
              handleSelectIncident('INC-001');
            }}
          />
        )}

        {currentTab === 'incidents' && (
          <IncidentsView
            incidents={incidents}
            onSelectIncident={handleSelectIncident}
            loading={loading}
          />
        )}

        {currentTab === 'investigate' && (
          selectedIncident ? (
            <IncidentConsoleView
              incident={selectedIncident}
              onBack={() => setCurrentTab('incidents')}
              onIncidentUpdated={handleIncidentUpdated}
            />
          ) : (
            <div className="p-12 text-center text-slate-400 bg-slate-900/40 rounded-2xl border border-slate-800">
              <p className="text-sm font-semibold mb-3">No incident selected for investigation.</p>
              <button
                onClick={() => setCurrentTab('incidents')}
                className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold"
              >
                Browse Incidents
              </button>
            </div>
          )
        )}

        {currentTab === 'timeline' && (
          <MemoryTimelineView memoryStatus={memoryStatus} />
        )}
      </main>

      {/* Learning Loop Modal */}
      <LearningLoopModal
        isOpen={isLearningLoopOpen}
        onClose={() => setIsLearningLoopOpen(false)}
      />

      {/* SRE Footer */}
      <footer className="border-t border-slate-800/80 bg-slate-950/80 px-6 py-4 mt-auto">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-3 text-xs text-slate-500">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-400">Incident Response Agent</span>
            <span>•</span>
            <span>Real Hindsight Memory Engine ({memoryStatus?.bank_id || 'incident-response-bank'})</span>
          </div>
          <div className="flex items-center gap-4 text-[11px] font-mono">
            <span>Server: 127.0.0.1:8888</span>
            <span>•</span>
            <span className="text-emerald-400">Human-in-the-Loop Enforced</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
