import React, { useState } from 'react';
import {
  ArrowLeft,
  BrainCircuit,
  Terminal,
  GitBranch,
  ShieldCheck,
  CheckCircle2,
  RotateCw,
  GitCompare,
  ChevronDown,
  ChevronUp,
} from 'lucide-react';
import { Incident, Analysis, Hypothesis, IncidentConfirmRequest, IncidentConfirmResponse } from '../types';
import DiagnosticTraceViewer from './DiagnosticTraceViewer';
import HypothesisList from './HypothesisList';
import RemediationPlan from './RemediationPlan';
import HumanConfirmationModal from './HumanConfirmationModal';
import MemoryComparisonModal from './MemoryComparisonModal';
import api from '../services/api';

interface Props {
  incident: Incident;
  onBack: () => void;
  onIncidentUpdated: (updated: Incident) => void;
}

export const IncidentConsoleView: React.FC<Props> = ({
  incident,
  onBack,
  onIncidentUpdated,
}) => {
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [isolatedAnalysis, setIsolatedAnalysis] = useState<Analysis | null>(null);
  const [isAnalyzingIsolated, setIsAnalyzingIsolated] = useState<boolean>(false);

  // Modals
  const [isConfirmModalOpen, setIsConfirmModalOpen] = useState<boolean>(false);
  const [isCompareModalOpen, setIsCompareModalOpen] = useState<boolean>(false);

  // Selected hypothesis for resolution
  const [selectedHypothesis, setSelectedHypothesis] = useState<Hypothesis | null>(null);
  const [adoptedPlanText, setAdoptedPlanText] = useState<string>('');

  // Collapsible panels
  const [showLogs, setShowLogs] = useState<boolean>(true);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Trigger Hindsight-empowered analysis
  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);
    setErrorMsg(null);
    try {
      const data = await api.analyzeIncident(incident.id);
      setAnalysis(data);
      if (data.hypotheses && data.hypotheses.length > 0) {
        setSelectedHypothesis(data.hypotheses[0]);
      }
      if (data.remediation_plan && data.remediation_plan.length > 0) {
        setAdoptedPlanText(
          data.remediation_plan.map((s) => `Step ${s.step}: ${s.action}`).join('\n')
        );
      }
    } catch (err: any) {
      console.error('Failed to run AI analysis:', err);
      setErrorMsg(
        err?.response?.data?.detail || err.message || 'Failed to complete Hindsight analysis.'
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Trigger isolated analysis (for side-by-side comparison)
  const handleRunIsolated = async () => {
    setIsAnalyzingIsolated(true);
    try {
      const data = await api.analyzeIncidentIsolated(incident.id);
      setIsolatedAnalysis(data);
    } catch (err: any) {
      console.error('Failed to run isolated analysis:', err);
    } finally {
      setIsAnalyzingIsolated(false);
    }
  };

  // Submit confirmation to backend
  const handleConfirmSubmit = async (data: IncidentConfirmRequest): Promise<IncidentConfirmResponse> => {
    const res = await api.confirmIncident(incident.id, data);
    // Refresh incident details
    const updatedInc = await api.getIncident(incident.id);
    onIncidentUpdated(updatedInc);
    return res;
  };

  return (
    <div className="space-y-6">
      {/* Top Breadcrumb & Actions Bar */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-4 rounded-xl bg-slate-900/60 border border-slate-800">
        <div className="flex items-center gap-3">
          <button
            onClick={onBack}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-mono text-sm font-bold text-white bg-slate-950 px-2.5 py-0.5 rounded border border-slate-800">
                {incident.id}
              </span>
              <span
                className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider ${
                  incident.severity === 'P1-Critical'
                    ? 'bg-rose-950 text-rose-300 border border-rose-800'
                    : 'bg-amber-950 text-amber-300 border border-amber-800'
                }`}
              >
                {incident.severity}
              </span>
              <span className="font-mono text-xs font-semibold text-indigo-400">
                {incident.service}
              </span>
              <span className="text-slate-500 font-mono text-xs">• {incident.environment}</span>
            </div>
            <h1 className="text-base font-bold text-white mt-1">{incident.title}</h1>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Compare Button */}
          <button
            onClick={() => {
              setIsCompareModalOpen(true);
              if (!analysis) handleRunAnalysis();
              if (!isolatedAnalysis) handleRunIsolated();
            }}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-purple-950/80 hover:bg-purple-900 text-purple-200 border border-purple-700/60 transition-all shadow-sm"
          >
            <GitCompare className="w-3.5 h-3.5 text-purple-400" />
            <span>Compare With/Without Memory</span>
          </button>

          {/* Retained Indicator */}
          {incident.retained_to_hindsight ? (
            <span className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-950 text-emerald-300 border border-emerald-700">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              <span>Retained in Hindsight</span>
            </span>
          ) : (
            <button
              onClick={() => setIsConfirmModalOpen(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold bg-emerald-600 hover:bg-emerald-500 text-white transition-all shadow-sm"
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>SRE Sign-Off</span>
            </button>
          )}
        </div>
      </div>

      {/* Incident Vitals & Telemetry */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {/* Metric 1: p99 Latency */}
        <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block">
            p99 Latency
          </span>
          <span className="text-xl font-bold font-mono text-rose-400">
            {incident.metrics?.latency_p99 || 'N/A'}
          </span>
          <span className="text-[11px] text-slate-500">Service SLA threshold: 250ms</span>
        </div>

        {/* Metric 2: Error Rate */}
        <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block">
            Error Rate
          </span>
          <span className="text-xl font-bold font-mono text-rose-400">
            {incident.metrics?.error_rate || 'N/A'}
          </span>
          <span className="text-[11px] text-slate-500">Elevated 5xx HTTP responses</span>
        </div>

        {/* Metric 3: Active Connections */}
        <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block">
            DB Connection Pool
          </span>
          <span className="text-xl font-bold font-mono text-amber-400">
            {incident.metrics?.active_connections
              ? `${incident.metrics.active_connections} / ${incident.metrics?.pool_max || '20'}`
              : 'N/A'}
          </span>
          <span className="text-[11px] text-slate-500">Pool capacity reached</span>
        </div>

        {/* Metric 4: Status */}
        <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-1">
          <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block">
            Incident Status
          </span>
          <span
            className={`text-xl font-bold font-mono ${
              incident.status === 'Resolved' ? 'text-emerald-400' : 'text-amber-400'
            }`}
          >
            {incident.status}
          </span>
          <span className="text-[11px] text-slate-500">
            {incident.retained_to_hindsight ? 'Memory indexed' : 'Awaiting SRE resolution'}
          </span>
        </div>
      </div>

      {/* Retained Memory Banner (if already confirmed & retained) */}
      {incident.retained_to_hindsight && (
        <div className="p-4 rounded-xl bg-emerald-950/40 border border-emerald-800/60 flex items-start gap-3">
          <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
          <div className="space-y-1 flex-1 text-xs">
            <div className="flex items-center justify-between">
              <span className="font-bold text-emerald-300">
                Verified Incident Post-Mortem Retained in Hindsight
              </span>
              <span className="font-mono text-[10px] text-emerald-400 bg-emerald-950 px-2 py-0.5 rounded border border-emerald-800">
                Memory ID: {incident.hindsight_memory_id || 'hindsight-entry'}
              </span>
            </div>
            <p className="text-slate-300">
              <span className="font-semibold text-emerald-400">Confirmed Root Cause:</span>{' '}
              {incident.confirmed_root_cause}
            </p>
            <p className="text-slate-300">
              <span className="font-semibold text-emerald-400">Approved Resolution:</span>{' '}
              {incident.confirmed_resolution}
            </p>
            {incident.post_mortem_lesson && (
              <p className="text-slate-400 text-[11px] italic">
                Lesson: "{incident.post_mortem_lesson}"
              </p>
            )}
          </div>
        </div>
      )}

      {/* Collapsible Logs & Changes Section */}
      <div className="border border-slate-800 rounded-xl bg-slate-900/50 overflow-hidden">
        <button
          onClick={() => setShowLogs(!showLogs)}
          className="w-full px-4 py-3 bg-slate-950/60 border-b border-slate-800 flex items-center justify-between text-xs font-semibold text-slate-300 hover:text-white"
        >
          <div className="flex items-center gap-2">
            <Terminal className="w-4 h-4 text-slate-400" />
            <span>Telemetry Evidence, Raw Logs & Recent Deployments</span>
          </div>
          {showLogs ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>

        {showLogs && (
          <div className="p-4 space-y-4">
            {/* Symptoms */}
            <div>
              <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
                Observed Symptoms
              </span>
              <div className="flex flex-wrap gap-2">
                {incident.symptoms.map((s, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded bg-slate-950 text-slate-300 border border-slate-800 font-mono text-xs"
                  >
                    • {s}
                  </span>
                ))}
              </div>
            </div>

            {/* Error Message & Raw Logs */}
            <div>
              <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
                Application Error Logs
              </span>
              <pre className="p-3 bg-slate-950 rounded-lg border border-slate-800 font-mono text-xs text-rose-300 overflow-x-auto leading-relaxed max-h-48">
                {incident.logs}
              </pre>
            </div>

            {/* Recent Changes */}
            <div>
              <span className="text-[10px] font-semibold text-slate-500 uppercase tracking-wider block mb-1.5">
                Recent Changes / Git History
              </span>
              <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 font-mono text-xs text-slate-300 flex items-center gap-2">
                <GitBranch className="w-4 h-4 text-indigo-400 shrink-0" />
                <span>{incident.recent_changes}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* AI Diagnostic Trigger Section */}
      <div className="p-5 rounded-2xl bg-gradient-to-r from-indigo-950/40 via-slate-900 to-indigo-950/40 border border-indigo-900/60 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <BrainCircuit className="w-5 h-5 text-indigo-400 animate-pulse" />
            <h3 className="text-sm font-bold text-white">AI Incident Analysis Agent</h3>
          </div>
          <p className="text-xs text-slate-300">
            Queries Hindsight <code className="text-purple-300 font-mono">incident-response-bank</code>,
            retrieves past resolutions with reranker scores, and synthesizes grounded hypotheses.
          </p>
        </div>

        <button
          onClick={handleRunAnalysis}
          disabled={isAnalyzing}
          className="flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs shadow-lg shadow-indigo-600/30 transition-all disabled:opacity-50 shrink-0"
        >
          <RotateCw className={`w-4 h-4 ${isAnalyzing ? 'animate-spin' : ''}`} />
          <span>{isAnalyzing ? 'Querying Hindsight & Analyzing...' : 'Run Hindsight Analysis'}</span>
        </button>
      </div>

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-950/70 border border-rose-800 text-xs text-rose-300">
          {errorMsg}
        </div>
      )}

      {/* Diagnostic Analysis Results */}
      {analysis && (
        <div className="space-y-6 animate-in fade-in duration-300">
          {/* Diagnostic Summary */}
          <div className="p-5 rounded-xl bg-slate-900/70 border border-slate-800 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider">
                Diagnostic Assessment Summary
              </span>
              <span className="text-[11px] font-mono text-slate-400">
                Mode: <span className="text-purple-300 font-bold">{analysis.mode}</span>
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-mono">
              {analysis.summary}
            </p>
          </div>

          {/* 6-Step Diagnostic Trace */}
          <DiagnosticTraceViewer
            trace={analysis.diagnostic_trace || null}
            recalledMemories={analysis.recalled_memories}
          />

          {/* Hypotheses & Remediation in 2 Columns */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Left: Hypotheses */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                  Root-Cause Hypotheses ({analysis.hypotheses.length})
                </h3>
                <span className="text-[10px] text-slate-500">Ranked by Model Confidence</span>
              </div>
              <HypothesisList
                hypotheses={analysis.hypotheses}
                selectedCause={selectedHypothesis?.cause}
                onSelectForResolution={(hyp) => {
                  setSelectedHypothesis(hyp);
                }}
              />
            </div>

            {/* Right: Remediation Plan */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300">
                  Recommended Remediation Steps ({analysis.remediation_plan.length})
                </h3>
                <span className="text-[10px] text-amber-400">Safety Gated</span>
              </div>
              <RemediationPlan
                plan={analysis.remediation_plan}
                onAdoptPlan={(txt) => setAdoptedPlanText(txt)}
              />
            </div>
          </div>

          {/* Human Decision Bar */}
          <div className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xl">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                <h4 className="text-sm font-bold text-white">Human SRE Sign-Off Checkpoint</h4>
              </div>
              <p className="text-xs text-slate-400">
                Confirm diagnosis to index this verified post-mortem into Hindsight, or correct/reject to prevent flawed memory retention.
              </p>
            </div>

            <div className="flex items-center gap-2 shrink-0">
              <button
                onClick={() => setIsConfirmModalOpen(true)}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-xs shadow-lg shadow-emerald-600/30 transition-all"
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>Confirm & Retain</span>
              </button>

              <button
                onClick={() => setIsConfirmModalOpen(true)}
                className="flex items-center gap-1.5 px-4 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold border border-slate-700 transition-all"
              >
                <span>Overrule / Reject</span>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Modal */}
      <HumanConfirmationModal
        isOpen={isConfirmModalOpen}
        onClose={() => setIsConfirmModalOpen(false)}
        incidentId={incident.id}
        defaultRootCause={selectedHypothesis?.cause || incident.confirmed_root_cause || ''}
        defaultResolution={adoptedPlanText || incident.confirmed_resolution || ''}
        defaultLesson={incident.post_mortem_lesson || ''}
        onConfirmSubmit={handleConfirmSubmit}
      />

      {/* Memory Comparison Modal */}
      <MemoryComparisonModal
        isOpen={isCompareModalOpen}
        onClose={() => setIsCompareModalOpen(false)}
        incidentId={incident.id}
        withMemoryAnalysis={analysis}
        withoutMemoryAnalysis={isolatedAnalysis}
        isLoadingIsolated={isAnalyzingIsolated}
        isLoadingWithMemory={isAnalyzing}
        onRunIsolatedAnalysis={handleRunIsolated}
        onRunWithMemoryAnalysis={handleRunAnalysis}
      />
    </div>
  );
};

export default IncidentConsoleView;
