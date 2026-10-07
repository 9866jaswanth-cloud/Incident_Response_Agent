import React, { useState } from 'react';
import {
  Search,
  Filter,
  AlertTriangle,
  ArrowRight,
  Database,
} from 'lucide-react';
import { Incident } from '../types';

interface Props {
  incidents: Incident[];
  onSelectIncident: (id: string) => void;
  loading: boolean;
}

export const IncidentsView: React.FC<Props> = ({ incidents, onSelectIncident, loading }) => {
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [severityFilter, setSeverityFilter] = useState<string>('ALL');
  const [statusFilter, setStatusFilter] = useState<string>('ALL');
  const [serviceFilter, setServiceFilter] = useState<string>('ALL');

  // Extract distinct services
  const services = Array.from(new Set(incidents.map((i) => i.service))).sort();

  // Filtered list
  const filtered = incidents.filter((inc) => {
    const matchesSearch =
      searchTerm === '' ||
      inc.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inc.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inc.error_message.toLowerCase().includes(searchTerm.toLowerCase()) ||
      inc.service.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesSeverity = severityFilter === 'ALL' || inc.severity === severityFilter;
    const matchesStatus = statusFilter === 'ALL' || inc.status === statusFilter;
    const matchesService = serviceFilter === 'ALL' || inc.service === serviceFilter;

    return matchesSearch && matchesSeverity && matchesStatus && matchesService;
  });

  return (
    <div className="space-y-6">
      {/* Header & Search */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-5 rounded-2xl bg-slate-900/60 border border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
            <span>Production Incidents ({filtered.length} of {incidents.length})</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Real and synthetic enterprise incidents ready for AI diagnosis and organizational memory retention.
          </p>
        </div>

        {/* Search Input */}
        <div className="relative w-full md:w-72">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by ID, service, error..."
            className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
          />
        </div>
      </div>

      {/* Filter Bar */}
      <div className="flex flex-wrap items-center gap-3 p-3 bg-slate-900/40 rounded-xl border border-slate-800 text-xs">
        <div className="flex items-center gap-1.5 text-slate-400 font-medium">
          <Filter className="w-3.5 h-3.5" />
          <span>Filters:</span>
        </div>

        {/* Severity */}
        <select
          value={severityFilter}
          onChange={(e) => setSeverityFilter(e.target.value)}
          className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-indigo-500 font-mono"
        >
          <option value="ALL">All Severities</option>
          <option value="P1-Critical">P1-Critical</option>
          <option value="P2-High">P2-High</option>
          <option value="P3-Medium">P3-Medium</option>
          <option value="P4-Low">P4-Low</option>
        </select>

        {/* Status */}
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-indigo-500 font-mono"
        >
          <option value="ALL">All Statuses</option>
          <option value="Investigating">Investigating</option>
          <option value="Mitigated">Mitigated</option>
          <option value="Resolved">Resolved</option>
          <option value="Closed">Closed</option>
        </select>

        {/* Service */}
        <select
          value={serviceFilter}
          onChange={(e) => setServiceFilter(e.target.value)}
          className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-indigo-500 font-mono"
        >
          <option value="ALL">All Services</option>
          {services.map((svc) => (
            <option key={svc} value={svc}>
              {svc}
            </option>
          ))}
        </select>

        {(searchTerm || severityFilter !== 'ALL' || statusFilter !== 'ALL' || serviceFilter !== 'ALL') && (
          <button
            onClick={() => {
              setSearchTerm('');
              setSeverityFilter('ALL');
              setStatusFilter('ALL');
              setServiceFilter('ALL');
            }}
            className="text-[11px] text-indigo-400 hover:text-indigo-300 ml-auto"
          >
            Clear Filters
          </button>
        )}
      </div>

      {/* Incidents Table */}
      <div className="border border-slate-800 rounded-2xl bg-slate-900/50 overflow-hidden shadow-sm">
        {loading ? (
          <div className="p-12 text-center text-slate-500 text-xs">Loading incidents...</div>
        ) : filtered.length === 0 ? (
          <div className="p-12 text-center text-slate-500 text-xs">
            No incidents matched your query. Try broadening your filter parameters.
          </div>
        ) : (
          <div className="divide-y divide-slate-800">
            {filtered.map((inc) => (
              <div
                key={inc.id}
                onClick={() => onSelectIncident(inc.id)}
                className="p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 hover:bg-slate-850/80 cursor-pointer transition-all group"
              >
                {/* Left details */}
                <div className="space-y-1.5 flex-1 min-w-0">
                  <div className="flex flex-wrap items-center gap-2">
                    <span className="font-mono text-xs font-bold text-white bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                      {inc.id}
                    </span>

                    <span
                      className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                        inc.severity === 'P1-Critical'
                          ? 'bg-rose-950 text-rose-300 border border-rose-800'
                          : inc.severity === 'P2-High'
                          ? 'bg-amber-950 text-amber-300 border border-amber-800'
                          : 'bg-slate-800 text-slate-300 border border-slate-700'
                      }`}
                    >
                      {inc.severity}
                    </span>

                    <span className="font-mono text-xs font-semibold text-indigo-300">
                      {inc.service}
                    </span>

                    <span className="text-slate-500 font-mono text-[11px] hidden sm:inline">
                      • {inc.environment}
                    </span>
                  </div>

                  <h3 className="text-sm font-semibold text-white group-hover:text-indigo-300 transition-colors truncate">
                    {inc.title}
                  </h3>

                  <p className="text-xs text-slate-400 font-mono line-clamp-1">
                    {inc.error_message}
                  </p>
                </div>

                {/* Right badges & button */}
                <div className="flex items-center gap-3 shrink-0">
                  {/* Retained Badge */}
                  {inc.retained_to_hindsight ? (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-medium bg-emerald-950 text-emerald-300 border border-emerald-800">
                      <Database className="w-3 h-3 text-emerald-400" />
                      Retained in Bank
                    </span>
                  ) : (
                    <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[10px] font-medium bg-slate-800 text-slate-400 border border-slate-700">
                      Unconfirmed
                    </span>
                  )}

                  <button className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-indigo-600 group-hover:bg-indigo-500 text-white shadow-sm transition-all">
                    <span>Investigate</span>
                    <ArrowRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default IncidentsView;
