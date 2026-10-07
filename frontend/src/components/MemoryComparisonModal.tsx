import React from 'react';
import {
  GitCompare,
  BrainCircuit,
  Zap,
  X,
  Database,
  RotateCw,
} from 'lucide-react';
import { Analysis } from '../types';
import EvidenceProvenanceBadge from './EvidenceProvenanceBadge';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  incidentId: string;
  withMemoryAnalysis: Analysis | null;
  withoutMemoryAnalysis: Analysis | null;
  isLoadingIsolated: boolean;
  isLoadingWithMemory?: boolean;
  onRunIsolatedAnalysis: () => void;
  onRunWithMemoryAnalysis?: () => void;
}

export const MemoryComparisonModal: React.FC<Props> = ({
  isOpen,
  onClose,
  incidentId,
  withMemoryAnalysis,
  withoutMemoryAnalysis,
  isLoadingIsolated,
  isLoadingWithMemory = false,
  onRunIsolatedAnalysis,
  onRunWithMemoryAnalysis,
}) => {
  if (!isOpen) return null;

  // Compute dynamic comparison metrics from real responses
  const withoutPrecedentsCount = withoutMemoryAnalysis?.recalled_memories?.length ?? 0;
  const withPrecedentsCount = withMemoryAnalysis?.recalled_memories?.length ?? 0;

  const withoutTopHyp = withoutMemoryAnalysis?.hypotheses?.[0];
  const withTopHyp = withMemoryAnalysis?.hypotheses?.[0];

  const withoutHistoricalHypCount =
    withoutMemoryAnalysis?.hypotheses?.filter((h) => h.evidence_type === 'HISTORICAL PRECEDENT')
      .length ?? 0;
  const withHistoricalHypCount =
    withMemoryAnalysis?.hypotheses?.filter((h) => h.evidence_type === 'HISTORICAL PRECEDENT')
      .length ?? 0;

  const precedentIdCited = withMemoryAnalysis?.hypotheses?.find(
    (h) => h.historical_incident_id
  )?.historical_incident_id;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-6xl max-h-[92vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950/70 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-purple-600/20 text-purple-400 border border-purple-500/30">
              <GitCompare className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                Comparative Reasoning Analysis: With vs Without Hindsight
                <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  {incidentId}
                </span>
              </h3>
              <p className="text-xs text-slate-400">
                Live side-by-side comparison of actual backend responses from isolated LLM reasoning vs Hindsight-augmented recall.
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

        {/* Dynamic Comparative Metrics Bar */}
        {(withoutMemoryAnalysis || withMemoryAnalysis) && (
          <div className="px-6 py-3 bg-slate-950/90 border-b border-slate-800 grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
            <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80">
              <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-0.5">
                Precedents Recalled
              </span>
              <div className="flex items-center gap-2 font-mono text-xs">
                <span className="text-slate-400">Isolated: {withoutPrecedentsCount}</span>
                <span className="text-slate-600">|</span>
                <span className="text-emerald-400 font-bold">Memory: {withPrecedentsCount}</span>
              </div>
            </div>

            <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80">
              <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-0.5">
                Top Confidence
              </span>
              <div className="flex items-center gap-2 font-mono text-xs">
                <span className="text-slate-400">
                  Isolated: {withoutTopHyp ? `${Math.round(withoutTopHyp.confidence * 100)}%` : 'N/A'}
                </span>
                <span className="text-slate-600">|</span>
                <span className="text-emerald-400 font-bold">
                  Memory: {withTopHyp ? `${Math.round(withTopHyp.confidence * 100)}%` : 'N/A'}
                </span>
              </div>
            </div>

            <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80">
              <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-0.5">
                Precedent-Backed Hypotheses
              </span>
              <div className="flex items-center gap-2 font-mono text-xs">
                <span className="text-slate-400">Isolated: {withoutHistoricalHypCount}</span>
                <span className="text-slate-600">|</span>
                <span className="text-purple-300 font-bold">
                  Memory: {withHistoricalHypCount}
                  {precedentIdCited && ` (${precedentIdCited})`}
                </span>
              </div>
            </div>

            <div className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800/80">
              <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-0.5">
                Remediation Steps
              </span>
              <div className="flex items-center gap-2 font-mono text-xs">
                <span className="text-slate-400">
                  Isolated: {withoutMemoryAnalysis?.remediation_plan?.length ?? 0}
                </span>
                <span className="text-slate-600">|</span>
                <span className="text-indigo-300 font-bold">
                  Memory: {withMemoryAnalysis?.remediation_plan?.length ?? 0}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Content Area: Side-by-Side Columns */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left Column: Without Memory (Isolated Backend Response) */}
            <div className="p-5 rounded-xl border border-slate-800 bg-slate-950/60 flex flex-col space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                    <Zap className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-slate-200">Without Memory (Isolated LLM)</h4>
                    <span className="text-[10px] text-slate-500 uppercase font-mono tracking-wider">
                      Endpoint: /api/agent/analyze-isolated/{incidentId}
                    </span>
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400 border border-slate-700">
                  Isolated Mode
                </span>
              </div>

              {isLoadingIsolated ? (
                <div className="p-12 text-center text-slate-400 text-xs flex flex-col items-center gap-2 my-auto">
                  <RotateCw className="w-5 h-5 animate-spin text-slate-400" />
                  <span>Executing isolated analysis without memory...</span>
                </div>
              ) : withoutMemoryAnalysis ? (
                <div className="space-y-4 text-xs">
                  {/* Summary */}
                  <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 space-y-1">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                      Diagnostic Summary
                    </span>
                    <p className="text-slate-300 leading-relaxed font-mono">
                      {withoutMemoryAnalysis.summary}
                    </p>
                  </div>

                  {/* Recalled Precedents */}
                  <div className="p-3 bg-slate-900 rounded-lg border border-slate-800 space-y-1.5">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400 font-medium">Hindsight Recalled Precedents:</span>
                      <span className="font-mono font-bold text-slate-500">
                        {withoutMemoryAnalysis.recalled_memories.length} (None)
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-500 font-mono">
                      Memory recall bypassed. Diagnostic reasoning constructed solely from current incident telemetry and static SOP runbooks.
                    </p>
                  </div>

                  {/* Hypotheses */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                        Root-Cause Hypotheses ({withoutMemoryAnalysis.hypotheses.length})
                      </span>
                      <span className="text-[10px] text-slate-500 font-mono">Ranked</span>
                    </div>

                    {withoutMemoryAnalysis.hypotheses.map((h, i) => (
                      <div
                        key={i}
                        className="p-3 bg-slate-900 rounded-lg border border-slate-800 space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-slate-200">{h.cause}</span>
                          <span className="font-mono text-slate-400 font-bold">
                            {Math.round(h.confidence * 100)}%
                          </span>
                        </div>
                        <EvidenceProvenanceBadge type={h.evidence_type} />
                        <p className="text-[11px] text-slate-400 leading-relaxed font-mono">
                          {h.rationale}
                        </p>
                      </div>
                    ))}
                  </div>

                  {/* Remediation Plan */}
                  <div className="space-y-2">
                    <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">
                      Recommended Remediation ({withoutMemoryAnalysis.remediation_plan.length} step(s))
                    </span>
                    <div className="space-y-2">
                      {withoutMemoryAnalysis.remediation_plan.map((s) => (
                        <div
                          key={s.step}
                          className="p-3 bg-slate-900 rounded-lg border border-slate-800 space-y-1.5 font-mono text-[11px]"
                        >
                          <div className="flex items-center gap-2">
                            <span className="w-4 h-4 rounded bg-slate-800 text-slate-400 font-bold flex items-center justify-center text-[10px]">
                              {s.step}
                            </span>
                            <span className="text-slate-300">{s.action}</span>
                          </div>
                          <div className="text-[10px] text-slate-500 pl-6">
                            Verification: {s.verification}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center space-y-3 my-auto">
                  <p className="text-xs text-slate-400">
                    No isolated baseline computed for this incident yet.
                  </p>
                  <button
                    onClick={onRunIsolatedAnalysis}
                    disabled={isLoadingIsolated}
                    className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-all disabled:opacity-50"
                  >
                    Run /api/agent/analyze-isolated
                  </button>
                </div>
              )}
            </div>

            {/* Right Column: With Hindsight Memory (Actual Backend Response) */}
            <div className="p-5 rounded-xl border border-indigo-700/60 bg-indigo-950/30 flex flex-col space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-indigo-900/60">
                <div className="flex items-center gap-2">
                  <div className="p-1.5 rounded bg-indigo-600/30 text-indigo-300 border border-indigo-500/40">
                    <BrainCircuit className="w-4 h-4 text-indigo-400" />
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white">With Hindsight Memory</h4>
                    <span className="text-[10px] text-indigo-300 uppercase font-mono tracking-wider">
                      Endpoint: /api/agent/analyze/{incidentId}
                    </span>
                  </div>
                </div>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-900/80 text-indigo-200 border border-indigo-700">
                  Real Hindsight arecall()
                </span>
              </div>

              {isLoadingWithMemory ? (
                <div className="p-12 text-center text-indigo-300 text-xs flex flex-col items-center gap-2 my-auto">
                  <RotateCw className="w-5 h-5 animate-spin text-indigo-400" />
                  <span>Querying Hindsight bank & synthesizing precedents...</span>
                </div>
              ) : withMemoryAnalysis ? (
                <div className="space-y-4 text-xs">
                  {/* Summary */}
                  <div className="p-3 bg-slate-950 rounded-lg border border-indigo-900/50 space-y-1">
                    <span className="text-[10px] font-semibold text-indigo-400 uppercase tracking-wider block">
                      Diagnostic Summary
                    </span>
                    <p className="text-slate-200 leading-relaxed font-mono">
                      {withMemoryAnalysis.summary}
                    </p>
                  </div>

                  {/* Recalled Memories from Hindsight with genuine scores */}
                  <div className="p-3 bg-slate-950 rounded-lg border border-indigo-900/50 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-300 font-medium flex items-center gap-1.5">
                        <Database className="w-3.5 h-3.5 text-indigo-400" />
                        Hindsight Recalled Precedents:
                      </span>
                      <span className="font-mono font-bold text-emerald-400">
                        {withMemoryAnalysis.recalled_memories.length} item(s)
                      </span>
                    </div>

                    {withMemoryAnalysis.recalled_memories.length > 0 ? (
                      <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                        {withMemoryAnalysis.recalled_memories.slice(0, 3).map((mem, idx) => (
                          <div
                            key={idx}
                            className="p-2.5 rounded bg-slate-900 border border-purple-900/40 text-[11px] space-y-1"
                          >
                            <div className="flex items-center justify-between">
                              <span className="font-mono font-bold text-purple-300">
                                {mem.incident_id || `MEMORY-${idx + 1}`}
                              </span>
                              <span className="text-[10px] text-slate-400 font-mono">
                                {mem.relevance_label}
                              </span>
                            </div>
                            <p className="text-slate-300 font-mono text-[10px] line-clamp-2">
                              {mem.raw_text}
                            </p>
                            {mem.scores && (
                              <div className="flex items-center gap-3 text-[10px] font-mono text-slate-400 pt-0.5">
                                {mem.scores.final !== undefined && (
                                  <span>
                                    Final: <span className="text-purple-300 font-bold">{(mem.scores.final * 100).toFixed(1)}%</span>
                                  </span>
                                )}
                                {mem.scores.reranker !== undefined && (
                                  <span>
                                    Reranker: <span className="text-indigo-300 font-bold">{(mem.scores.reranker * 100).toFixed(1)}%</span>
                                  </span>
                                )}
                                {mem.scores.semantic !== undefined && (
                                  <span>
                                    Semantic: <span className="text-cyan-300 font-bold">{(mem.scores.semantic * 100).toFixed(1)}%</span>
                                  </span>
                                )}
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-[11px] text-slate-500 font-mono">
                        No historical memories returned for this query.
                      </p>
                    )}
                  </div>

                  {/* Hypotheses */}
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] font-semibold text-indigo-400 uppercase tracking-wider block">
                        Root-Cause Hypotheses ({withMemoryAnalysis.hypotheses.length})
                      </span>
                      <span className="text-[10px] text-emerald-400 font-mono">Precedent-Informed</span>
                    </div>

                    {withMemoryAnalysis.hypotheses.map((h, i) => (
                      <div
                        key={i}
                        className="p-3 bg-slate-950 rounded-lg border border-indigo-900/60 space-y-2"
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-white">{h.cause}</span>
                          <span className="font-mono text-emerald-400 font-bold">
                            {Math.round(h.confidence * 100)}%
                          </span>
                        </div>
                        <EvidenceProvenanceBadge
                          type={h.evidence_type}
                          precedentId={h.historical_incident_id}
                        />
                        <p className="text-[11px] text-slate-300 leading-relaxed font-mono">
                          {h.rationale}
                        </p>
                      </div>
                    ))}
                  </div>

                  {/* Remediation Plan */}
                  <div className="space-y-2">
                    <span className="text-[10px] font-semibold text-indigo-400 uppercase tracking-wider block">
                      Recommended Remediation ({withMemoryAnalysis.remediation_plan.length} step(s))
                    </span>
                    <div className="space-y-2">
                      {withMemoryAnalysis.remediation_plan.map((s) => (
                        <div
                          key={s.step}
                          className="p-3 bg-slate-950 rounded-lg border border-indigo-900/50 space-y-1.5 font-mono text-[11px]"
                        >
                          <div className="flex items-center gap-2">
                            <span className="w-4 h-4 rounded bg-indigo-900 text-indigo-200 font-bold flex items-center justify-center text-[10px]">
                              {s.step}
                            </span>
                            <span className="text-indigo-200">{s.action}</span>
                          </div>
                          <div className="text-[10px] text-slate-400 pl-6">
                            Verification: {s.verification}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center space-y-3 my-auto">
                  <p className="text-xs text-slate-400">
                    No Hindsight analysis loaded for this incident yet.
                  </p>
                  {onRunWithMemoryAnalysis && (
                    <button
                      onClick={onRunWithMemoryAnalysis}
                      disabled={isLoadingWithMemory}
                      className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold shadow-sm transition-all disabled:opacity-50"
                    >
                      Run /api/agent/analyze
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="px-6 py-3 border-t border-slate-800 bg-slate-950/70 flex items-center justify-between text-xs text-slate-500">
          <span className="font-mono text-[11px]">
            Backend Provenance: All displayed scores, rationales, and steps reflect actual API payloads.
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold transition-colors"
          >
            Close Comparison
          </button>
        </div>
      </div>
    </div>
  );
};

export default MemoryComparisonModal;
