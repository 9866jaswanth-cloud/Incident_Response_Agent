import React from 'react';
import { Database, FileText, Cpu, Clock } from 'lucide-react';
import { EvidenceType } from '../types';

interface Props {
  type: EvidenceType;
  precedentId?: string | null;
  className?: string;
}

export const EvidenceProvenanceBadge: React.FC<Props> = ({ type, precedentId, className = '' }) => {
  switch (type) {
    case 'CURRENT EVIDENCE':
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-cyan-950/80 text-cyan-300 border border-cyan-700/50 shadow-sm ${className}`}
        >
          <Clock className="w-3 h-3 text-cyan-400" />
          <span>CURRENT EVIDENCE</span>
        </span>
      );

    case 'HISTORICAL PRECEDENT':
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-indigo-950/80 text-indigo-300 border border-indigo-600/60 shadow-sm ${className}`}
        >
          <Database className="w-3 h-3 text-indigo-400" />
          <span>HISTORICAL PRECEDENT</span>
          {precedentId && (
            <span className="ml-1 px-1.5 py-0.5 rounded bg-indigo-800/80 text-white font-mono text-[10px] tracking-wide">
              {precedentId}
            </span>
          )}
        </span>
      );

    case 'RUNBOOK':
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-emerald-950/80 text-emerald-300 border border-emerald-700/50 shadow-sm ${className}`}
        >
          <FileText className="w-3 h-3 text-emerald-400" />
          <span>RUNBOOK</span>
        </span>
      );

    case 'MODEL INFERENCE':
    default:
      return (
        <span
          className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800/80 text-slate-300 border border-slate-700 shadow-sm ${className}`}
        >
          <Cpu className="w-3 h-3 text-slate-400" />
          <span>MODEL INFERENCE</span>
        </span>
      );
  }
};

export default EvidenceProvenanceBadge;
