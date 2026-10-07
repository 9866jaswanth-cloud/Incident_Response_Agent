import React from 'react';
import { CheckCircle2, ChevronRight } from 'lucide-react';
import { Hypothesis } from '../types';
import EvidenceProvenanceBadge from './EvidenceProvenanceBadge';

interface Props {
  hypotheses: Hypothesis[];
  onSelectForResolution?: (hypothesis: Hypothesis) => void;
  selectedCause?: string | null;
}

export const HypothesisList: React.FC<Props> = ({
  hypotheses,
  onSelectForResolution,
  selectedCause,
}) => {
  if (!hypotheses || hypotheses.length === 0) {
    return (
      <div className="p-6 text-center text-slate-500 text-xs bg-slate-950/40 rounded-xl border border-slate-800">
        No hypotheses generated yet. Run analysis to trigger reasoning.
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {hypotheses.map((hyp, idx) => {
        const isSelected = selectedCause === hyp.cause;
        const confidencePct = Math.round(hyp.confidence * 100);

        return (
          <div
            key={idx}
            className={`p-4 rounded-xl border transition-all ${
              isSelected
                ? 'bg-indigo-950/60 border-indigo-500 shadow-md ring-1 ring-indigo-500/40'
                : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
            }`}
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 font-mono text-[11px] font-bold flex items-center justify-center border border-slate-700">
                  {idx + 1}
                </span>
                <h4 className="text-sm font-semibold text-white tracking-tight">{hyp.cause}</h4>
              </div>

              <div className="flex items-center gap-2">
                <EvidenceProvenanceBadge
                  type={hyp.evidence_type}
                  precedentId={hyp.historical_incident_id}
                />
              </div>
            </div>

            {/* Confidence Bar */}
            <div className="mb-3 space-y-1">
              <div className="flex items-center justify-between text-[11px] font-mono">
                <span className="text-slate-400">Agent Confidence</span>
                <span
                  className={`font-bold ${
                    confidencePct >= 80
                      ? 'text-emerald-400'
                      : confidencePct >= 60
                      ? 'text-amber-400'
                      : 'text-slate-400'
                  }`}
                >
                  {confidencePct}%
                </span>
              </div>
              <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    confidencePct >= 80
                      ? 'bg-gradient-to-r from-emerald-600 to-emerald-400'
                      : confidencePct >= 60
                      ? 'bg-gradient-to-r from-amber-600 to-amber-400'
                      : 'bg-slate-600'
                  }`}
                  style={{ width: `${confidencePct}%` }}
                />
              </div>
            </div>

            {/* Technical Rationale */}
            <div className="p-3 bg-slate-950/70 rounded-lg border border-slate-800 text-xs text-slate-300 leading-relaxed font-mono">
              <span className="text-slate-500 font-semibold block uppercase tracking-wider text-[10px] mb-1">
                Technical Justification & Evidence
              </span>
              {hyp.rationale}
            </div>

            {/* Adoption action */}
            {onSelectForResolution && (
              <div className="mt-3 flex justify-end">
                <button
                  onClick={() => onSelectForResolution(hyp)}
                  className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
                    isSelected
                      ? 'bg-indigo-600 text-white'
                      : 'bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white'
                  }`}
                >
                  {isSelected ? (
                    <>
                      <CheckCircle2 className="w-3.5 h-3.5 text-indigo-200" />
                      <span>Selected for Human Confirmation</span>
                    </>
                  ) : (
                    <>
                      <span>Select Root Cause</span>
                      <ChevronRight className="w-3.5 h-3.5" />
                    </>
                  )}
                </button>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default HypothesisList;
