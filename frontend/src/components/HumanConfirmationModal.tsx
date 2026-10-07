import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  CheckCircle2,
  XCircle,
  Edit3,
  Database,
  AlertTriangle,
  Send,
  X,
  FileCheck,
} from 'lucide-react';
import { IncidentConfirmRequest, IncidentConfirmResponse } from '../types';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  incidentId: string;
  defaultRootCause?: string;
  defaultResolution?: string;
  defaultLesson?: string;
  onConfirmSubmit: (data: IncidentConfirmRequest) => Promise<IncidentConfirmResponse>;
}

export const HumanConfirmationModal: React.FC<Props> = ({
  isOpen,
  onClose,
  incidentId,
  defaultRootCause = '',
  defaultResolution = '',
  defaultLesson = '',
  onConfirmSubmit,
}) => {
  const [actionType, setActionType] = useState<'confirm' | 'correct' | 'reject'>('confirm');
  const [rootCause, setRootCause] = useState<string>(defaultRootCause);
  const [resolution, setResolution] = useState<string>(defaultResolution);
  const [lesson, setLesson] = useState<string>(defaultLesson);
  const [notes, setNotes] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [result, setResult] = useState<IncidentConfirmResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setRootCause(defaultRootCause);
    setResolution(defaultResolution);
    setLesson(
      defaultLesson ||
        'Document pool connection configurations and keep worker pools isolated from external webhook spikes.'
    );
    setResult(null);
    setError(null);
  }, [defaultRootCause, defaultResolution, defaultLesson, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);

    try {
      const payload: IncidentConfirmRequest = {
        status: actionType === 'reject' ? 'rejected' : 'confirmed',
        notes: notes || undefined,
      };

      if (actionType === 'confirm') {
        payload.confirmed_root_cause = rootCause;
        payload.approved_resolution = resolution;
        payload.post_mortem_lesson = lesson;
      } else if (actionType === 'correct') {
        payload.corrected_root_cause = rootCause;
        payload.corrected_resolution = resolution;
        payload.post_mortem_lesson = lesson;
      }

      const res = await onConfirmSubmit(payload);
      setResult(res);
    } catch (err: any) {
      console.error('Confirmation error:', err);
      setError(err?.response?.data?.detail || err.message || 'Failed to submit confirmation.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-slate-900 border border-slate-700/80 rounded-2xl w-full max-w-2xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-slate-800 bg-slate-950/70 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-lg bg-indigo-600/20 text-indigo-400 border border-indigo-500/30">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white flex items-center gap-2">
                Human SRE Sign-Off Gate
                <span className="font-mono text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                  {incidentId}
                </span>
              </h3>
              <p className="text-xs text-slate-400">
                AI hypothesis requires human verification before retention into organizational memory.
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

        {/* Success View */}
        {result ? (
          <div className="p-6 space-y-4 overflow-y-auto">
            <div
              className={`p-4 rounded-xl border flex items-start gap-3 ${
                result.retained_to_hindsight
                  ? 'bg-emerald-950/50 border-emerald-600/60 text-emerald-200'
                  : 'bg-amber-950/50 border-amber-600/60 text-amber-200'
              }`}
            >
              {result.retained_to_hindsight ? (
                <CheckCircle2 className="w-6 h-6 text-emerald-400 shrink-0 mt-0.5" />
              ) : (
                <XCircle className="w-6 h-6 text-amber-400 shrink-0 mt-0.5" />
              )}
              <div className="space-y-1">
                <h4 className="text-sm font-bold">{result.message}</h4>
                <p className="text-xs opacity-90">
                  {result.retained_to_hindsight
                    ? `Successfully retained into Hindsight bank "${result.bank_id}" with Memory ID: ${result.hindsight_memory_id || 'hindsight-entry'}.`
                    : 'The investigation was closed without retaining to organizational memory.'}
                </p>
              </div>
            </div>

            {result.retained_post_mortem_preview && (
              <div className="space-y-1.5">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
                  Retained Post-Mortem Memory Entry:
                </span>
                <pre className="p-4 bg-slate-950 rounded-xl border border-slate-800 text-xs font-mono text-slate-300 whitespace-pre-wrap leading-relaxed max-h-60 overflow-y-auto">
                  {result.retained_post_mortem_preview}
                </pre>
              </div>
            )}

            <div className="flex justify-end pt-2">
              <button
                onClick={onClose}
                className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 text-white font-medium text-xs transition-colors"
              >
                Close & Return to Console
              </button>
            </div>
          </div>
        ) : (
          /* Form View */
          <form onSubmit={handleSubmit} className="flex-1 overflow-y-auto p-6 space-y-5">
            {/* Action Type Selector */}
            <div className="grid grid-cols-3 gap-2 p-1 bg-slate-950 rounded-xl border border-slate-800">
              <button
                type="button"
                onClick={() => setActionType('confirm')}
                className={`py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                  actionType === 'confirm'
                    ? 'bg-emerald-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <CheckCircle2 className="w-3.5 h-3.5" />
                <span>Confirm & Retain</span>
              </button>

              <button
                type="button"
                onClick={() => setActionType('correct')}
                className={`py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                  actionType === 'correct'
                    ? 'bg-indigo-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <Edit3 className="w-3.5 h-3.5" />
                <span>Overrule / Correct</span>
              </button>

              <button
                type="button"
                onClick={() => setActionType('reject')}
                className={`py-2 px-3 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5 transition-all ${
                  actionType === 'reject'
                    ? 'bg-rose-600 text-white shadow-sm'
                    : 'text-slate-400 hover:text-slate-200'
                }`}
              >
                <XCircle className="w-3.5 h-3.5" />
                <span>Reject Analysis</span>
              </button>
            </div>

            {actionType === 'reject' ? (
              <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-xs space-y-2">
                <div className="flex items-center gap-2 text-rose-300 font-bold">
                  <AlertTriangle className="w-4 h-4" />
                  <span>Rejection Policy Enforced</span>
                </div>
                <p className="text-slate-300 leading-relaxed">
                  Rejecting this analysis marks the hypothesis as invalid. In accordance with safety rules,
                  this event will <span className="font-semibold text-rose-300">NEVER be retained to Hindsight</span>.
                  An audit trail entry will record the SRE rejection.
                </p>
                <div className="pt-2">
                  <label className="block text-slate-400 text-xs font-medium mb-1">
                    Rejection Reason / Notes
                  </label>
                  <textarea
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Describe why this diagnosis was incorrect or discarded..."
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:border-rose-500 font-mono"
                    rows={3}
                  />
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {actionType === 'correct' && (
                  <div className="p-3 bg-indigo-950/40 border border-indigo-800/50 rounded-lg text-xs text-indigo-300 flex items-center gap-2">
                    <FileCheck className="w-4 h-4 shrink-0" />
                    <span>
                      Human-in-the-loop overrule: Your corrected root cause and resolution will replace the
                      AI hypothesis and be permanently indexed by Hindsight.
                    </span>
                  </div>
                )}

                {/* Root Cause */}
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                    {actionType === 'correct' ? 'Corrected Root Cause' : 'Confirmed Root Cause'}
                  </label>
                  <input
                    type="text"
                    required
                    value={rootCause}
                    onChange={(e) => setRootCause(e.target.value)}
                    placeholder="e.g., PostgreSQL connection pool exhaustion due to slow queries"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2.5 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
                  />
                </div>

                {/* Approved Resolution */}
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                    {actionType === 'correct' ? 'Corrected Resolution Steps' : 'Approved Resolution Plan'}
                  </label>
                  <textarea
                    required
                    value={resolution}
                    onChange={(e) => setResolution(e.target.value)}
                    placeholder="e.g., Scaled connection pool max_size from 20 to 50 and added 15s timeout"
                    rows={3}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
                  />
                </div>

                {/* Post-Mortem Lesson */}
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                    Post-Mortem Lesson (Retained for future recall)
                  </label>
                  <textarea
                    value={lesson}
                    onChange={(e) => setLesson(e.target.value)}
                    placeholder="Key architectural takeaway or runbook update to assist future responders..."
                    rows={2}
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg p-3 text-xs text-slate-200 focus:outline-none focus:border-indigo-500 font-mono"
                  />
                </div>

                {/* SRE Notes */}
                <div>
                  <label className="block text-xs font-bold uppercase tracking-wider text-slate-400 mb-1.5">
                    Engineer Notes (Optional)
                  </label>
                  <input
                    type="text"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Verified alongside team on Slack #incident-response"
                    className="w-full bg-slate-950 border border-slate-800 rounded-lg px-3.5 py-2 text-xs text-slate-200 focus:outline-none focus:border-indigo-500"
                  />
                </div>

                <div className="p-3 bg-slate-950 rounded-lg border border-slate-800 text-[11px] text-slate-400 flex items-center gap-2">
                  <Database className="w-4 h-4 text-purple-400 shrink-0" />
                  <span>
                    Submitting will trigger a real Hindsight <code className="text-purple-300 font-mono">aretain()</code>{' '}
                    call to write this verified knowledge into bank <code className="text-slate-200 font-mono">incident-response-bank</code>.
                  </span>
                </div>
              </div>
            )}

            {error && (
              <div className="p-3 rounded-lg bg-rose-950/60 border border-rose-800 text-xs text-rose-300">
                {error}
              </div>
            )}

            {/* Footer Buttons */}
            <div className="pt-3 border-t border-slate-800 flex items-center justify-end gap-3">
              <button
                type="button"
                onClick={onClose}
                disabled={isSubmitting}
                className="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={isSubmitting}
                className={`px-4 py-2 rounded-lg text-xs font-semibold flex items-center gap-2 transition-all ${
                  actionType === 'reject'
                    ? 'bg-rose-600 hover:bg-rose-500 text-white'
                    : 'bg-indigo-600 hover:bg-indigo-500 text-white'
                } disabled:opacity-50`}
              >
                {isSubmitting ? (
                  <span>Processing with Hindsight...</span>
                ) : actionType === 'reject' ? (
                  <>
                    <XCircle className="w-4 h-4" />
                    <span>Confirm Rejection</span>
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    <span>Approve & Retain Memory</span>
                  </>
                )}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};

export default HumanConfirmationModal;
