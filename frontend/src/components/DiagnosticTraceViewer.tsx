import React, { useState } from 'react';
import {
  Search,
  Database,
  GitCompare,
  Lightbulb,
  CheckSquare,
  Activity,
  ChevronRight,
  ShieldCheck,
  Award,
} from 'lucide-react';
import { DiagnosticTrace, RecalledMemoryItem } from '../types';

interface Props {
  trace: DiagnosticTrace | null;
  recalledMemories: RecalledMemoryItem[];
}

export const DiagnosticTraceViewer: React.FC<Props> = ({ trace, recalledMemories }) => {
  const [activeStep, setActiveStep] = useState<number>(0);

  if (!trace) {
    return (
      <div className="p-6 rounded-xl border border-slate-800 bg-slate-900/40 text-center text-slate-400 text-sm">
        Diagnostic trace will appear once incident analysis is executed.
      </div>
    );
  }

  const steps = [
    {
      id: 0,
      title: '1. Incident Evidence',
      icon: Activity,
      color: 'text-cyan-400',
      bgColor: 'bg-cyan-950/60',
      borderColor: 'border-cyan-800/60',
      content: (
        <div className="space-y-3">
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <span className="text-slate-500 font-semibold block uppercase tracking-wider text-[10px] mb-1">
                Target Service
              </span>
              <span className="text-slate-200 font-mono font-medium">
                {trace.current_incident?.service || 'N/A'}
              </span>
            </div>
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <span className="text-slate-500 font-semibold block uppercase tracking-wider text-[10px] mb-1">
                Environment
              </span>
              <span className="text-slate-200 font-mono font-medium">
                {trace.current_incident?.environment || 'production'}
              </span>
            </div>
          </div>

          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs">
            <span className="text-slate-500 font-semibold block uppercase tracking-wider text-[10px] mb-1">
              Error Message
            </span>
            <code className="text-rose-400 font-mono break-all">
              {trace.current_incident?.error_message || 'N/A'}
            </code>
          </div>

          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-xs">
            <span className="text-slate-500 font-semibold block uppercase tracking-wider text-[10px] mb-1">
              Observed Symptoms
            </span>
            <div className="flex flex-wrap gap-1.5 mt-1">
              {Array.isArray(trace.current_incident?.symptoms) ? (
                trace.current_incident.symptoms.map((sym: string, i: number) => (
                  <span
                    key={i}
                    className="px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-mono text-[11px]"
                  >
                    • {sym}
                  </span>
                ))
              ) : (
                <span className="text-slate-400">None specified</span>
              )}
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 1,
      title: '2. Hindsight Recall',
      icon: Search,
      color: 'text-indigo-400',
      bgColor: 'bg-indigo-950/60',
      borderColor: 'border-indigo-800/60',
      content: (
        <div className="space-y-3 text-xs">
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-slate-500 font-semibold uppercase tracking-wider text-[10px]">
                Recall Query Dispatched to Hindsight arecall()
              </span>
              <span className="text-[10px] font-mono px-2 py-0.5 bg-indigo-950 text-indigo-300 rounded border border-indigo-700/50">
                Budget: {trace.hindsight_recall?.budget || 'mid'}
              </span>
            </div>
            <code className="text-indigo-200 font-mono bg-indigo-950/40 p-2.5 rounded block border border-indigo-900/40 break-words leading-relaxed">
              {trace.hindsight_recall?.query || 'N/A'}
            </code>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <span className="text-slate-500 font-semibold block uppercase tracking-wider text-[10px] mb-1">
                Target Bank
              </span>
              <span className="text-slate-200 font-mono font-medium">
                {trace.hindsight_recall?.bank_id || 'incident-response-bank'}
              </span>
            </div>
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <span className="text-slate-500 font-semibold block uppercase tracking-wider text-[10px] mb-1">
                Memories Discovered
              </span>
              <span className="text-emerald-400 font-mono font-bold text-sm">
                {recalledMemories.length} historical item(s)
              </span>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 2,
      title: '3. Historical Precedents',
      icon: Database,
      color: 'text-purple-400',
      bgColor: 'bg-purple-950/60',
      borderColor: 'border-purple-800/60',
      content: (
        <div className="space-y-3">
          {recalledMemories.length === 0 ? (
            <div className="p-4 bg-slate-950 rounded-lg border border-slate-800 text-center text-slate-400 text-xs">
              <Award className="w-8 h-8 text-slate-600 mx-auto mb-2" />
              <p className="font-semibold text-slate-300">Cold-Start Incident</p>
              <p className="text-[11px] text-slate-500 mt-1">
                No matching historical precedents found in Hindsight bank. The agent will rely on current telemetry,
                runbooks, and first-principles inference. Once resolved, this incident will form the first memory!
              </p>
            </div>
          ) : (
            recalledMemories.map((mem, i) => (
              <div
                key={i}
                className="p-3.5 bg-slate-950 rounded-lg border border-purple-900/40 text-xs space-y-2 hover:border-purple-700/60 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="px-2 py-0.5 rounded bg-purple-900/60 text-purple-200 font-mono font-bold text-[11px] border border-purple-700/50">
                      {mem.incident_id || `PRECEDENT-${i + 1}`}
                    </span>
                    <span className="text-slate-300 font-medium">Service: {mem.service || 'Shared'}</span>
                  </div>
                  <span className="text-[10px] font-mono px-2 py-0.5 bg-slate-800 text-purple-300 rounded border border-slate-700">
                    {mem.relevance_label}
                  </span>
                </div>

                <div className="p-2.5 bg-slate-900 rounded border border-slate-800 font-mono text-[11px] text-slate-300 whitespace-pre-wrap leading-relaxed">
                  {mem.raw_text}
                </div>

                {mem.scores && (
                  <div className="flex items-center gap-4 text-[10px] text-slate-400 font-mono pt-1">
                    {mem.scores.final !== undefined && (
                      <span>
                        Final Score:{' '}
                        <span className="text-purple-300 font-semibold">
                          {(mem.scores.final * 100).toFixed(1)}%
                        </span>
                      </span>
                    )}
                    {mem.scores.reranker !== undefined && (
                      <span>
                        Reranker:{' '}
                        <span className="text-indigo-300 font-semibold">
                          {(mem.scores.reranker * 100).toFixed(1)}%
                        </span>
                      </span>
                    )}
                    {mem.scores.semantic !== undefined && (
                      <span>
                        Semantic:{' '}
                        <span className="text-cyan-300 font-semibold">
                          {(mem.scores.semantic * 100).toFixed(1)}%
                        </span>
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      ),
    },
    {
      id: 3,
      title: '4. Evidence Synthesis',
      icon: GitCompare,
      color: 'text-amber-400',
      bgColor: 'bg-amber-950/60',
      borderColor: 'border-amber-800/60',
      content: (
        <div className="space-y-3 text-xs">
          <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
            <span className="text-slate-500 font-semibold block uppercase tracking-wider text-[10px] mb-1">
              Synthesis Summary
            </span>
            <p className="text-slate-300 leading-relaxed">
              {trace.evidence_synthesis?.provenance_summary ||
                'Correlating real-time symptoms against historical precedent runbooks and recent deployment events.'}
            </p>
          </div>

          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <span className="text-slate-500 font-semibold block uppercase tracking-wider text-[10px] mb-1">
                Telemetry Correlated
              </span>
              <span className="text-slate-300 font-mono text-[11px]">
                {trace.evidence_synthesis?.correlated_symptoms_count ?? trace.current_incident?.symptoms?.length ?? 0}{' '}
                signal(s)
              </span>
            </div>
            <div className="p-3 bg-slate-950 rounded-lg border border-slate-800">
              <span className="text-slate-500 font-semibold block uppercase tracking-wider text-[10px] mb-1">
                Precedents Leveraged
              </span>
              <span className="text-purple-300 font-mono font-medium text-[11px]">
                {trace.evidence_synthesis?.precedents_used?.length ?? recalledMemories.length} item(s)
              </span>
            </div>
          </div>
        </div>
      ),
    },
    {
      id: 4,
      title: '5. Root-Cause Hypotheses',
      icon: Lightbulb,
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-950/60',
      borderColor: 'border-emerald-800/60',
      content: (
        <div className="space-y-2 text-xs">
          {trace.root_cause_hypotheses?.length > 0 ? (
            trace.root_cause_hypotheses.map((hyp: any, i: number) => (
              <div key={i} className="p-3 bg-slate-950 rounded-lg border border-slate-800 space-y-1.5">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-white">{hyp.cause}</span>
                  <span className="font-mono text-emerald-400 font-bold">
                    {Math.round((hyp.confidence || 0) * 100)}% Confidence
                  </span>
                </div>
                <p className="text-slate-400 leading-relaxed text-[11px]">{hyp.rationale}</p>
              </div>
            ))
          ) : (
            <p className="text-slate-500">Hypotheses pending...</p>
          )}
        </div>
      ),
    },
    {
      id: 5,
      title: '6. Recommended Remediation',
      icon: CheckSquare,
      color: 'text-blue-400',
      bgColor: 'bg-blue-950/60',
      borderColor: 'border-blue-800/60',
      content: (
        <div className="space-y-2 text-xs">
          {trace.recommended_remediation?.length > 0 ? (
            trace.recommended_remediation.map((step: any, i: number) => (
              <div key={i} className="p-3 bg-slate-950 rounded-lg border border-slate-800 flex items-start gap-3">
                <div className="w-5 h-5 rounded-full bg-blue-900/60 text-blue-300 font-mono font-bold text-[10px] flex items-center justify-center border border-blue-700/50 shrink-0 mt-0.5">
                  {step.step || i + 1}
                </div>
                <div className="space-y-1 flex-1">
                  <div className="font-mono text-slate-200 text-[11px]">{step.action}</div>
                  <div className="text-[10px] text-slate-400 flex items-center gap-2">
                    <span className="text-slate-500">Verify:</span> {step.verification}
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded text-[9px] font-semibold uppercase tracking-wider bg-amber-950/80 text-amber-300 border border-amber-800/50 shrink-0">
                  Human Gate
                </span>
              </div>
            ))
          ) : (
            <p className="text-slate-500">Remediation plan pending...</p>
          )}
        </div>
      ),
    },
  ];

  return (
    <div className="border border-slate-800 rounded-xl bg-slate-900/50 overflow-hidden shadow-sm">
      <div className="px-5 py-3 border-b border-slate-800 bg-slate-950/60 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-indigo-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-200">
            6-Step Diagnostic Reasoning Trace
          </h3>
        </div>
        <span className="text-[11px] text-slate-400 font-mono">
          Provenanced AI Reasoning Pipeline
        </span>
      </div>

      {/* Stepper Header */}
      <div className="grid grid-cols-2 md:grid-cols-6 border-b border-slate-800 bg-slate-950/40">
        {steps.map((s) => {
          const Icon = s.icon;
          const isActive = activeStep === s.id;
          return (
            <button
              key={s.id}
              onClick={() => setActiveStep(s.id)}
              className={`p-2.5 text-left border-r last:border-r-0 border-slate-800 flex items-center gap-2 transition-all ${
                isActive
                  ? 'bg-slate-800/90 border-b-2 border-b-indigo-500'
                  : 'hover:bg-slate-850 opacity-70 hover:opacity-100'
              }`}
            >
              <div className={`p-1.5 rounded ${s.bgColor} border ${s.borderColor}`}>
                <Icon className={`w-3.5 h-3.5 ${s.color}`} />
              </div>
              <span className={`text-xs font-semibold truncate ${isActive ? 'text-white' : 'text-slate-400'}`}>
                {s.title}
              </span>
            </button>
          );
        })}
      </div>

      {/* Active Step Content */}
      <div className="p-5 bg-slate-900/30">
        <div className="flex items-center justify-between mb-3 pb-2 border-b border-slate-800/60">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold text-white">{steps[activeStep].title}</span>
          </div>
          <div className="flex items-center gap-2 text-xs">
            <button
              disabled={activeStep === 0}
              onClick={() => setActiveStep((prev) => Math.max(0, prev - 1))}
              className="px-2 py-1 rounded bg-slate-800 text-slate-300 hover:bg-slate-700 disabled:opacity-40 text-[11px]"
            >
              Previous
            </button>
            <button
              disabled={activeStep === steps.length - 1}
              onClick={() => setActiveStep((prev) => Math.min(steps.length - 1, prev + 1))}
              className="px-2 py-1 rounded bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-40 text-[11px] flex items-center gap-1"
            >
              <span>Next Step</span>
              <ChevronRight className="w-3 h-3" />
            </button>
          </div>
        </div>

        {steps[activeStep].content}
      </div>
    </div>
  );
};

export default DiagnosticTraceViewer;
