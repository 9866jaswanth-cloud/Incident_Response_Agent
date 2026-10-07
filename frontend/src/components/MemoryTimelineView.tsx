import React, { useState, useEffect } from 'react';
import {
  History,
  RotateCw,
  Database,
  Search,
  CheckCircle2,
  XCircle,
  Clock,
  Layers,
} from 'lucide-react';
import { MemoryTimelineEvent, MemoryStatus } from '../types';
import api from '../services/api';

interface Props {
  memoryStatus: MemoryStatus | null;
}

export const MemoryTimelineView: React.FC<Props> = ({ memoryStatus }) => {
  const [events, setEvents] = useState<MemoryTimelineEvent[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [filterOp, setFilterOp] = useState<string>('ALL');

  const fetchTimeline = async () => {
    setLoading(true);
    try {
      const data = await api.getMemoryTimeline(50);
      setEvents(data.events || []);
    } catch (err) {
      console.error('Failed to fetch memory timeline:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTimeline();
  }, []);

  const filteredEvents =
    filterOp === 'ALL' ? events : events.filter((e) => e.operation === filterOp);

  const getOpBadge = (op: string) => {
    switch (op) {
      case 'RETAIN':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-purple-950 text-purple-300 border border-purple-800">
            <Database className="w-3 h-3 text-purple-400" />
            RETAIN
          </span>
        );
      case 'RECALL':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-indigo-950 text-indigo-300 border border-indigo-800">
            <Search className="w-3 h-3 text-indigo-400" />
            RECALL
          </span>
        );
      case 'CONFIRMATION':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-emerald-950 text-emerald-300 border border-emerald-800">
            <CheckCircle2 className="w-3 h-3 text-emerald-400" />
            CONFIRM
          </span>
        );
      case 'REJECTION':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-rose-950 text-rose-300 border border-rose-800">
            <XCircle className="w-3 h-3 text-rose-400" />
            REJECT
          </span>
        );
      case 'REFLECT':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider bg-cyan-950 text-cyan-300 border border-cyan-800">
            <Layers className="w-3 h-3 text-cyan-400" />
            REFLECT
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 rounded-full text-[10px] font-mono bg-slate-800 text-slate-300 border border-slate-700">
            {op}
          </span>
        );
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Status & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <History className="w-5 h-5 text-indigo-400" />
            <span>Hindsight Memory Audit Log & Timeline</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Immutable chronological record of all retain, recall, confirmation, and rejection operations.
          </p>
        </div>

        <div className="flex items-center gap-3">
          {/* Filter */}
          <div className="flex items-center space-x-1 bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs">
            {['ALL', 'RETAIN', 'RECALL', 'CONFIRMATION', 'REJECTION'].map((f) => (
              <button
                key={f}
                onClick={() => setFilterOp(f)}
                className={`px-2.5 py-1 rounded-md text-[11px] font-semibold transition-all ${
                  filterOp === f
                    ? 'bg-indigo-600 text-white'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-850'
                }`}
              >
                {f}
              </button>
            ))}
          </div>

          <button
            onClick={fetchTimeline}
            disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 transition-colors disabled:opacity-50"
          >
            <RotateCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-indigo-400' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Memory Bank Info Card */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
            Active Memory Bank
          </span>
          <span className="font-mono text-xs font-bold text-indigo-300">
            {memoryStatus?.bank_id || 'incident-response-bank'}
          </span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
            Hindsight Base URL
          </span>
          <span className="font-mono text-xs text-slate-300">
            {memoryStatus?.hindsight_base_url || 'http://127.0.0.1:8888'}
          </span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
            Execution Mode
          </span>
          <span className="font-mono text-xs font-bold text-emerald-400">
            {memoryStatus?.mode || 'REAL_HINDSIGHT'}
          </span>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-1">
            Total Logged Events
          </span>
          <span className="font-mono text-xs font-bold text-white">
            {events.length} event(s)
          </span>
        </div>
      </div>

      {/* Timeline List */}
      <div className="space-y-3">
        {loading && events.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-xs bg-slate-900/30 rounded-2xl border border-slate-800">
            Loading Hindsight memory audit records...
          </div>
        ) : filteredEvents.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-xs bg-slate-900/30 rounded-2xl border border-slate-800">
            No events match the current filter. Perform an incident analysis or confirmation to create events.
          </div>
        ) : (
          filteredEvents.map((evt) => (
            <div
              key={evt.id}
              className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 hover:border-slate-700 transition-all space-y-2.5 text-xs"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="flex items-center gap-3">
                  {getOpBadge(evt.operation)}
                  {evt.incident_id && (
                    <span className="font-mono font-bold text-slate-200 bg-slate-800 px-2 py-0.5 rounded text-[11px] border border-slate-700">
                      {evt.incident_id}
                    </span>
                  )}
                  <span className="text-[11px] font-mono text-slate-400">
                    Bank: <span className="text-slate-300">{evt.bank_id}</span>
                  </span>
                </div>

                <div className="flex items-center gap-3 text-[11px] font-mono text-slate-400">
                  <span className="flex items-center gap-1 text-slate-500">
                    <Clock className="w-3 h-3" />
                    {new Date(evt.timestamp).toLocaleTimeString()}
                  </span>
                  <span className="px-2 py-0.5 rounded bg-slate-950 text-indigo-300 border border-slate-800 font-bold">
                    {evt.duration_ms}ms
                  </span>
                </div>
              </div>

              {/* Query or Retained Snippet */}
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800/80 font-mono text-[11px] text-slate-300 whitespace-pre-wrap leading-relaxed">
                {evt.query_or_content}
              </div>

              {/* Results Summary */}
              {evt.results_summary && (
                <div className="flex items-center gap-2 text-[11px] text-slate-400">
                  <span className="text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
                    Outcome:
                  </span>
                  <span className="text-slate-300 font-mono">{evt.results_summary}</span>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default MemoryTimelineView;
