import React from 'react';
import { Sparkles, ArrowRight, CheckCircle2, AlertCircle, BrainCircuit } from 'lucide-react';
import { Incident } from '../types';

interface GuidedDemoBarProps {
  incidents: Incident[];
  onSelectIncident: (id: string) => void;
  selectedIncidentId: string | null;
  onOpenLearningLoop?: () => void;
}

export const GuidedDemoBar: React.FC<GuidedDemoBarProps> = ({
  incidents,
  onSelectIncident,
  selectedIncidentId,
  onOpenLearningLoop,
}) => {
  const inc1 = incidents.find((i) => i.id === 'INC-001');
  const inc2 = incidents.find((i) => i.id === 'INC-002');
  const inc3 = incidents.find((i) => i.id === 'INC-003');

  const steps = [
    {
      id: 'INC-001',
      title: 'Step 1: Initial Discovery',
      service: 'Payment API',
      incident: inc1,
      story: 'Zero memory precedent. Cold-start analysis. SRE confirms and retains to Hindsight.',
      benefit: 'Forms initial organizational memory.',
    },
    {
      id: 'INC-002',
      title: 'Step 2: Memory Recall',
      service: 'Payment API',
      incident: inc2,
      story: 'Recalls INC-001 memory. Cites precedent in hypothesis & speeds up pool remediation.',
      benefit: 'Prevents rediscovering known pool exhaustion causes.',
    },
    {
      id: 'INC-003',
      title: 'Step 3: Cross-Service Transfer',
      service: 'Order Service',
      incident: inc3,
      story: 'Different service! Cross-service recall transfers pool configuration lessons.',
      benefit: 'Knowledge propagates across entire engineering org.',
    },
  ];

  return (
    <div className="bg-gradient-to-r from-indigo-950/80 via-slate-900 to-purple-950/80 border-b border-indigo-900/40 px-6 py-3">
      <div className="max-w-7xl mx-auto">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 mb-2">
          <div className="flex items-center gap-2">
            <span className="p-1 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30">
              <Sparkles className="w-4 h-4" />
            </span>
            <span className="text-xs font-bold uppercase tracking-wider text-purple-300">
              Guided 3-Step Demo Story
            </span>
            <span className="text-xs text-slate-400">
              (How Hindsight powers organizational memory across recurring & cross-service incidents)
            </span>
          </div>

          {onOpenLearningLoop && (
            <button
              onClick={onOpenLearningLoop}
              className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-indigo-950/90 hover:bg-indigo-900/90 border border-indigo-700/60 text-indigo-200 text-xs font-semibold shadow-sm transition-colors"
            >
              <BrainCircuit className="w-3.5 h-3.5 text-indigo-400" />
              <span>Learning Loop Architecture</span>
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {steps.map((step) => {
            const isSelected = selectedIncidentId === step.id;
            const isRetained = step.incident?.retained_to_hindsight;

            return (
              <div
                key={step.id}
                onClick={() => onSelectIncident(step.id)}
                className={`p-3 rounded-lg border cursor-pointer transition-all ${
                  isSelected
                    ? 'bg-indigo-950/90 border-indigo-500 shadow-md ring-1 ring-indigo-500/50'
                    : 'bg-slate-900/80 border-slate-800 hover:border-indigo-700/60 hover:bg-slate-850'
                }`}
              >
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs font-bold text-white bg-slate-800 px-1.5 py-0.5 rounded border border-slate-700">
                      {step.id}
                    </span>
                    <span className="text-xs font-semibold text-slate-200">{step.title}</span>
                  </div>
                  {isRetained ? (
                    <span className="flex items-center gap-1 text-[11px] font-medium text-emerald-400 bg-emerald-950/80 px-2 py-0.5 rounded-full border border-emerald-800/60">
                      <CheckCircle2 className="w-3 h-3" />
                      Retained
                    </span>
                  ) : (
                    <span className="flex items-center gap-1 text-[11px] text-amber-400 bg-amber-950/60 px-2 py-0.5 rounded-full border border-amber-800/50">
                      <AlertCircle className="w-3 h-3" />
                      Unconfirmed
                    </span>
                  )}
                </div>

                <div className="text-[11px] font-medium text-indigo-300 mb-1">
                  Service: <span className="text-slate-300">{step.service}</span>
                </div>

                <p className="text-xs text-slate-400 leading-snug mb-2">
                  {step.story}
                </p>

                <div className="flex items-center justify-between text-[11px] pt-1.5 border-t border-slate-800">
                  <span className="text-purple-300 font-medium">{step.benefit}</span>
                  <div className="flex items-center gap-1 text-slate-400 group-hover:text-indigo-300">
                    <span>Investigate</span>
                    <ArrowRight className="w-3 h-3" />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default GuidedDemoBar;
