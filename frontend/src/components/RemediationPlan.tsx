import React from 'react';
import { Terminal, ShieldAlert, CheckCircle, AlertTriangle } from 'lucide-react';
import { RemediationStep } from '../types';

interface Props {
  plan: RemediationStep[];
  onAdoptPlan?: (fullPlanText: string) => void;
}

export const RemediationPlan: React.FC<Props> = ({ plan, onAdoptPlan }) => {
  if (!plan || plan.length === 0) {
    return (
      <div className="p-6 text-center text-slate-500 text-xs bg-slate-950/40 rounded-xl border border-slate-800">
        No remediation plan generated yet. Run analysis to create an action plan.
      </div>
    );
  }

  const combinedPlan = plan
    .map((s) => `Step ${s.step}: ${s.action}\nVerification: ${s.verification}`)
    .join('\n\n');

  return (
    <div className="space-y-3">
      {plan.map((step) => (
        <div
          key={step.step}
          className="p-4 rounded-xl border border-slate-800 bg-slate-900/60 space-y-2.5"
        >
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="w-6 h-6 rounded-lg bg-indigo-950 text-indigo-300 font-mono font-bold text-xs flex items-center justify-center border border-indigo-700/60">
                {step.step}
              </span>
              <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
                Remediation Action
              </span>
            </div>

            <div className="flex items-center gap-2">
              {step.is_destructive && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-rose-950 text-rose-300 border border-rose-800/60">
                  <AlertTriangle className="w-3 h-3 text-rose-400" />
                  Destructive
                </span>
              )}
              {step.requires_human_approval && (
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-amber-950/80 text-amber-300 border border-amber-800/60">
                  <ShieldAlert className="w-3 h-3 text-amber-400" />
                  Requires Human Approval
                </span>
              )}
            </div>
          </div>

          {/* Action Command / Description */}
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 font-mono text-xs text-indigo-300 flex items-start gap-2">
            <Terminal className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
            <span className="break-words leading-relaxed">{step.action}</span>
          </div>

          {/* Verification */}
          <div className="p-2.5 bg-slate-950/60 rounded-lg border border-slate-800/80 text-xs text-slate-400 flex items-start gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
            <div className="leading-relaxed">
              <span className="text-slate-500 font-semibold uppercase tracking-wider text-[10px] block">
                Verification Criteria
              </span>
              <span className="font-mono text-[11px] text-slate-300">{step.verification}</span>
            </div>
          </div>
        </div>
      ))}

      {onAdoptPlan && (
        <div className="pt-2 flex justify-end">
          <button
            onClick={() => onAdoptPlan(combinedPlan)}
            className="px-3 py-1.5 rounded-md text-xs font-medium bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700 transition-all"
          >
            Copy Plan to Confirmation Draft
          </button>
        </div>
      )}
    </div>
  );
};

export default RemediationPlan;
