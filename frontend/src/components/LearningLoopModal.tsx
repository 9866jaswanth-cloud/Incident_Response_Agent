import React from 'react';
import {
  BrainCircuit,
  ArrowDown,
  X,
  ShieldCheck,
  CheckCircle2,
  Database,
  Search,
  Activity,
  FileCheck,
  Cpu,
  RefreshCw,
} from 'lucide-react';

interface Props {
  isOpen: boolean;
  onClose: () => void;
}

export const LearningLoopModal: React.FC<Props> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const loopSteps = [
    {
      label: 'INCIDENT',
      detail: 'Production service disruption or latency degradation alert triggered (e.g. HikariPool exhaustion).',
      actor: 'System Monitoring',
      icon: Activity,
      color: 'text-rose-400',
      bgColor: 'bg-rose-950/60',
      borderColor: 'border-rose-800/60',
    },
    {
      label: 'CURRENT EVIDENCE',
      detail: 'Ingestion of live p99 latency, active connection meters, error logs, and recent commit diffs.',
      actor: 'Telemetry Pipeline',
      icon: Cpu,
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-950/60',
      borderColor: 'border-cyan-800/60',
    },
    {
      label: 'HINDSIGHT RECALL',
      detail: 'Real arecall() dispatched to incident-response-bank with hybrid semantic and cross-encoder reranking.',
      actor: 'Official Hindsight Engine',
      icon: Search,
      color: 'text-indigo-400',
      bgColor: 'bg-indigo-950/60',
      borderColor: 'border-indigo-800/60',
    },
    {
      label: 'HISTORICAL EXPERIENCE',
      detail: 'Extraction of verified past incident post-mortems with genuine similarity scores.',
      actor: 'Hindsight Memory Bank',
      icon: Database,
      color: 'text-purple-400',
      bgColor: 'bg-purple-950/60',
      borderColor: 'border-purple-800/60',
    },
    {
      label: 'ROOT-CAUSE ANALYSIS',
      detail: 'Evidence synthesis explicitly tagging CURRENT EVIDENCE vs HISTORICAL PRECEDENT vs MODEL INFERENCE.',
      actor: 'Incident Agent',
      icon: BrainCircuit,
      color: 'text-amber-400',
      bgColor: 'bg-amber-950/60',
      borderColor: 'border-amber-800/60',
    },
    {
      label: 'RECOMMENDATION',
      detail: 'Confidence-ranked root causes and actionable remediation steps with verification commands.',
      actor: 'Incident Agent',
      icon: FileCheck,
      color: 'text-blue-400',
      bgColor: 'bg-blue-950/60',
      borderColor: 'border-blue-800/60',
    },
    {
      label: 'HUMAN CONFIRMATION',
      detail: 'Mandatory SRE review: approve, correct/overrule, or reject. Rejections are strictly halted from retention.',
      actor: 'Human SRE Engineer',
      icon: ShieldCheck,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-950/60',
      borderColor: 'border-emerald-800/60',
    },
    {
      label: 'HINDSIGHT RETAIN',
      detail: 'Async aretain() writes human-verified post-mortem into Hindsight with audit trail entry.',
      actor: 'Official Hindsight Engine',
      icon: CheckCircle2,
      color: 'text-purple-400',
      bgColor: 'bg-purple-950/60',
      borderColor: 'border-purple-800/60',
    },
    {
      label: 'NEW ORGANIZATIONAL MEMORY',
      detail: 'Persistent memory unit indexed and ready for immediate recall by any engineer or service in the org.',
      actor: 'Incident Response Bank',
      icon: Database,
      color: 'text-indigo-400',
      bgColor: 'bg-indigo-950/60',
      borderColor: 'border-indigo-800/60',
    },
    {
      label: 'BETTER CONTEXT FOR FUTURE INCIDENTS',
      detail: 'Prevents rediscovering known root causes and accelerates cross-service knowledge transfer.',
      actor: 'Continuous Learning Loop',
      icon: RefreshCw,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-950/60',
      borderColor: 'border-emerald-800/60',
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-4xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950/70 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
              <BrainCircuit className="w-5 h-5 text-indigo-400" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                The Continuous Organizational Learning Loop
              </h3>
              <p className="text-xs text-slate-400">
                How Hindsight and Human SRE collaboration create compound institutional knowledge over time.
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          <div className="max-w-2xl mx-auto space-y-2">
            {loopSteps.map((step, idx) => {
              const Icon = step.icon;
              return (
                <React.Fragment key={idx}>
                  <div
                    className={`p-3.5 rounded-xl border ${step.borderColor} ${step.bgColor} flex items-start gap-3.5 shadow-sm transition-all hover:scale-[1.01]`}
                  >
                    <div className={`p-2 rounded-lg bg-slate-950 border ${step.borderColor} shrink-0`}>
                      <Icon className={`w-4 h-4 ${step.color}`} />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between gap-2 mb-1">
                        <span className={`text-xs font-black uppercase tracking-wider ${step.color}`}>
                          {step.label}
                        </span>
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-slate-950 text-slate-400 border border-slate-800">
                          {step.actor}
                        </span>
                      </div>
                      <p className="text-xs text-slate-300 leading-relaxed font-mono">
                        {step.detail}
                      </p>
                    </div>
                  </div>

                  {idx < loopSteps.length - 1 && (
                    <div className="flex justify-center py-0.5">
                      <ArrowDown className="w-4 h-4 text-slate-600 animate-pulse" />
                    </div>
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950/70 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-colors"
          >
            Close Learning Architecture
          </button>
        </div>
      </div>
    </div>
  );
};

export default LearningLoopModal;
