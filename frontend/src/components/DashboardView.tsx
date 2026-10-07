import React from 'react';
import {
  AlertTriangle,
  BrainCircuit,
  Database,
  ArrowRight,
  Sparkles,
  CheckCircle2,
  Activity,
  Flame,
} from 'lucide-react';
import { Incident, MemoryStatus, MemoryTimelineEvent } from '../types';

interface Props {
  incidents: Incident[];
  memoryStatus: MemoryStatus | null;
  recentEvents: MemoryTimelineEvent[];
  onSelectIncident: (id: string) => void;
  onNavigateTab: (tab: 'dashboard' | 'incidents' | 'investigate' | 'timeline') => void;
  onStartDemo: () => void;
}

export const DashboardView: React.FC<Props> = ({
  incidents,
  memoryStatus,
  recentEvents,
  onSelectIncident,
  onNavigateTab,
  onStartDemo,
}) => {
  const p1Count = incidents.filter((i) => i.severity === 'P1-Critical').length;
  const activeCount = incidents.filter((i) => i.status === 'Investigating').length;
  const retainedCount = incidents.filter((i) => i.retained_to_hindsight).length;

  const demoIncidents = [
    incidents.find((i) => i.id === 'INC-001'),
    incidents.find((i) => i.id === 'INC-002'),
    incidents.find((i) => i.id === 'INC-003'),
  ].filter(Boolean) as Incident[];

  return (
    <div className="space-y-6">
      {/* Hero / Quick Pitch Banner */}
      <div className="relative overflow-hidden rounded-2xl border border-indigo-900/50 bg-gradient-to-r from-slate-900 via-indigo-950/40 to-slate-900 p-6 shadow-xl">
        <div className="max-w-3xl space-y-2 relative z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-950/80 border border-indigo-700/60 text-indigo-300 text-xs font-semibold">
            <BrainCircuit className="w-3.5 h-3.5 text-indigo-400" />
            <span>Persistent Organizational Memory Engine</span>
          </div>
          <h2 className="text-2xl font-black text-white tracking-tight">
            An AI Agent that remembers how your organization solved problems before.
          </h2>
          <p className="text-sm text-slate-300 leading-relaxed">
            Eliminate repetitive diagnosis during production fire drills. The agent retrieves verified
            historical post-mortems from the real <span className="font-mono text-purple-300 font-semibold">Hindsight</span> service,
            proposes proven remediations, and requires human SRE sign-off before committing new lessons to memory.
          </p>

          <div className="pt-3 flex flex-wrap gap-3">
            <button
              onClick={onStartDemo}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold shadow-lg shadow-indigo-600/30 transition-all"
            >
              <Sparkles className="w-4 h-4" />
              <span>Launch 3-Incident Guided Story</span>
            </button>

            <button
              onClick={() => onNavigateTab('incidents')}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all"
            >
              <span>Explore All Incidents ({incidents.length})</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Top Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* P1 Incidents */}
        <div className="p-4 rounded-xl bg-slate-900/70 border border-rose-900/40 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>P1 Critical</span>
            <Flame className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-rose-400">{p1Count}</div>
          <span className="text-[11px] text-slate-500">Service disruptions</span>
        </div>

        {/* Investigating Incidents */}
        <div className="p-4 rounded-xl bg-slate-900/70 border border-amber-900/40 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Active Fire Drills</span>
            <AlertTriangle className="w-4 h-4 text-amber-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-amber-400">{activeCount}</div>
          <span className="text-[11px] text-slate-500">Currently investigating</span>
        </div>

        {/* Retained in Hindsight */}
        <div className="p-4 rounded-xl bg-slate-900/70 border border-purple-900/40 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Retained in Memory</span>
            <Database className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-purple-400">{retainedCount}</div>
          <span className="text-[11px] text-slate-500">Verified post-mortems</span>
        </div>

        {/* Real Hindsight Health */}
        <div className="p-4 rounded-xl bg-slate-900/70 border border-emerald-900/40 space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Hindsight Server</span>
            <Activity className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-400">
            {memoryStatus?.connected ? 'ONLINE' : 'OFFLINE'}
          </div>
          <span className="text-[11px] text-slate-500 font-mono truncate block">
            {memoryStatus?.bank_id || 'incident-response-bank'}
          </span>
        </div>
      </div>

      {/* Main Grid: Guided Flow Highlight & Active Incidents */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left 2 Cols: Demo Walkthrough Incidents */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-purple-400" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Organizational Learning Triad
              </h3>
            </div>
            <span className="text-xs text-slate-400">Replayable Learning Loop</span>
          </div>

          <div className="space-y-3">
            {demoIncidents.map((inc) => (
              <div
                key={inc.id}
                onClick={() => onSelectIncident(inc.id)}
                className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-indigo-600/70 hover:bg-slate-850 cursor-pointer transition-all group"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-white bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                      {inc.id}
                    </span>
                    <h4 className="text-sm font-bold text-slate-200 group-hover:text-indigo-300 transition-colors">
                      {inc.title}
                    </h4>
                  </div>

                  <div className="flex items-center gap-2">
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                        inc.severity === 'P1-Critical'
                          ? 'bg-rose-950 text-rose-300 border border-rose-800'
                          : 'bg-amber-950 text-amber-300 border border-amber-800'
                      }`}
                    >
                      {inc.severity}
                    </span>
                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        inc.retained_to_hindsight
                          ? 'bg-emerald-950 text-emerald-300 border border-emerald-800'
                          : 'bg-slate-800 text-slate-400 border border-slate-700'
                      }`}
                    >
                      {inc.retained_to_hindsight ? 'Retained in Bank' : 'Unconfirmed'}
                    </span>
                  </div>
                </div>

                <p className="text-xs text-slate-400 line-clamp-2 leading-relaxed mb-3">
                  {inc.error_message}
                </p>

                <div className="flex items-center justify-between text-xs pt-2 border-t border-slate-800 text-slate-400">
                  <span className="font-mono text-[11px] text-indigo-300">Service: {inc.service}</span>
                  <div className="flex items-center gap-1 text-slate-400 group-hover:text-indigo-300 font-medium">
                    <span>Open in Investigation Console</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right Col: Hindsight System Details & Recent Operations */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-purple-400" />
              <h3 className="text-sm font-bold text-white uppercase tracking-wider">
                Memory Health & Telemetry
              </h3>
            </div>
            <button
              onClick={() => onNavigateTab('timeline')}
              className="text-xs text-indigo-400 hover:text-indigo-300"
            >
              View Full Audit
            </button>
          </div>

          {/* Engine Card */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3 text-xs">
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <span className="text-slate-400">Memory Provider</span>
              <span className="font-mono font-bold text-purple-300">Official Hindsight</span>
            </div>
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <span className="text-slate-400">Memory Bank ID</span>
              <span className="font-mono text-slate-200">
                {memoryStatus?.bank_id || 'incident-response-bank'}
              </span>
            </div>
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <span className="text-slate-400">Server Endpoint</span>
              <span className="font-mono text-slate-200">
                {memoryStatus?.hindsight_base_url || '127.0.0.1:8888'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400">Status</span>
              <span className="inline-flex items-center gap-1 font-semibold text-emerald-400">
                <CheckCircle2 className="w-3.5 h-3.5" />
                Live & Grounded
              </span>
            </div>
          </div>

          {/* Recent Operations */}
          <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 space-y-3">
            <span className="text-xs font-bold text-slate-300 uppercase tracking-wider block">
              Recent Memory Activity
            </span>

            {recentEvents.length === 0 ? (
              <p className="text-xs text-slate-500 py-4 text-center">
                No recent operations recorded. Analyze an incident to trigger recall.
              </p>
            ) : (
              <div className="space-y-2">
                {recentEvents.slice(0, 4).map((evt) => (
                  <div
                    key={evt.id}
                    className="p-2.5 rounded-lg bg-slate-950 border border-slate-800/80 text-[11px] space-y-1"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-mono font-bold text-purple-300">{evt.operation}</span>
                      <span className="font-mono text-slate-500 text-[10px]">{evt.duration_ms}ms</span>
                    </div>
                    <p className="text-slate-400 line-clamp-1 font-mono text-[10px]">
                      {evt.query_or_content}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardView;
