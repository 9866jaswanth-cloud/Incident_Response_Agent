/**
 * TypeScript Data Models mirroring backend Pydantic schemas.
 */

export type Severity = 'P1-Critical' | 'P2-High' | 'P3-Medium' | 'P4-Low';
export type IncidentStatus = 'Investigating' | 'Mitigated' | 'Resolved' | 'Closed';
export type EvidenceType = 'CURRENT EVIDENCE' | 'HISTORICAL PRECEDENT' | 'RUNBOOK' | 'MODEL INFERENCE';

export interface Incident {
  id: string;
  title: string;
  service: string;
  severity: Severity;
  status: IncidentStatus;
  error_message: string;
  symptoms: string[];
  logs: string;
  metrics: Record<string, any>;
  recent_changes: string;
  stack_trace?: string | null;
  environment: string;
  confirmed_root_cause?: string | null;
  confirmed_resolution?: string | null;
  investigation_steps?: string[] | null;
  post_mortem_lesson?: string | null;
  retained_to_hindsight: boolean;
  retained_at?: string | null;
  hindsight_memory_id?: string | null;
  created_at: string;
  resolved_at?: string | null;
}

export interface Hypothesis {
  cause: string;
  confidence: number;
  evidence_type: EvidenceType;
  rationale: string;
  historical_incident_id?: string | null;
}

export interface RecalledMemoryItem {
  id?: string | null;
  incident_id?: string | null;
  service?: string | null;
  symptoms?: string | null;
  root_cause?: string | null;
  resolution?: string | null;
  outcome?: string | null;
  relevance_label: string;
  raw_text: string;
  scores?: {
    final?: number;
    reranker?: number;
    semantic?: number;
    keyword?: number;
  } | null;
  document_id?: string | null;
  context?: string | null;
  source: string;
}

export interface RemediationStep {
  step: number;
  action: string;
  verification: string;
  is_destructive: boolean;
  requires_human_approval: boolean;
}

export interface DiagnosticTrace {
  current_incident: Record<string, any>;
  hindsight_recall: Record<string, any>;
  historical_precedents: Array<Record<string, any>>;
  evidence_synthesis: Record<string, any>;
  root_cause_hypotheses: Array<Record<string, any>>;
  recommended_remediation: Array<Record<string, any>>;
}

export interface Analysis {
  id: string;
  incident_id: string;
  summary: string;
  hypotheses: Hypothesis[];
  recalled_memories: RecalledMemoryItem[];
  recommended_investigation: string[];
  remediation_plan: RemediationStep[];
  diagnostic_trace?: DiagnosticTrace | null;
  mode: 'with_memory' | 'without_memory';
  created_at: string;
}


export interface Runbook {
  id: string;
  service: string;
  title: string;
  trigger_symptoms: string[];
  standard_operating_procedure: string;
}

export interface MemoryStatus {
  connected: boolean;
  hindsight_base_url: string;
  bank_id: string;
  version?: string | null;
  mode: 'REAL_HINDSIGHT' | 'OFFLINE_DEVELOPMENT_MODE';
  message: string;
}

export interface MemoryTimelineEvent {
  id: number;
  operation: 'RETAIN' | 'RECALL' | 'REFLECT' | 'CONFIRMATION' | 'REJECTION';
  incident_id?: string | null;
  bank_id: string;
  query_or_content: string;
  results_summary: string;
  status: string;
  duration_ms: number;
  timestamp: string;
}

export interface IncidentConfirmRequest {
  status: 'confirmed' | 'rejected';
  confirmed_root_cause?: string | null;
  approved_resolution?: string | null;
  post_mortem_lesson?: string | null;
  notes?: string | null;
  investigation_steps?: string[];
  corrected_root_cause?: string | null;
  corrected_resolution?: string | null;
}

export interface IncidentConfirmResponse {
  incident_id: string;
  status: string;
  retained_to_hindsight: boolean;
  bank_id?: string | null;
  hindsight_memory_id?: string | null;
  confirmed_root_cause?: string | null;
  confirmed_resolution?: string | null;
  message: string;
  retained_post_mortem_preview?: string | null;
  audit_log_id?: number | null;
}

