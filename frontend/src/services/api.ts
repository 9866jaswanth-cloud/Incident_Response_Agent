import axios from 'axios';
import {
  Incident,
  Analysis,
  MemoryStatus,
  MemoryTimelineEvent,
  IncidentConfirmRequest,
  IncidentConfirmResponse,
} from '../types';

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 45000, // Hindsight reranker and embeddings can take a few seconds
});

export interface IncidentListResponse {
  total: number;
  items: Incident[];
}

export interface MemoryTimelineResponse {
  total: number;
  events: MemoryTimelineEvent[];
}

export const api = {
  // Incidents
  async getIncidents(params?: {
    status?: string;
    severity?: string;
    service?: string;
    limit?: number;
    offset?: number;
  }): Promise<IncidentListResponse> {
    const response = await apiClient.get<IncidentListResponse>('/incidents', { params });
    return response.data;
  },

  async getIncident(id: string): Promise<Incident> {
    const response = await apiClient.get<Incident>(`/incidents/${id}`);
    return response.data;
  },

  // AI Agent Analysis
  async analyzeIncident(id: string): Promise<Analysis> {
    const response = await apiClient.post<Analysis>(`/agent/analyze/${id}`);
    return response.data;
  },

  async analyzeIncidentIsolated(id: string): Promise<Analysis> {
    const response = await apiClient.post<Analysis>(`/agent/analyze-isolated/${id}`);
    return response.data;
  },

  // Human Confirmation
  async confirmIncident(id: string, data: IncidentConfirmRequest): Promise<IncidentConfirmResponse> {
    const response = await apiClient.post<IncidentConfirmResponse>(`/agent/confirm/${id}`, data);
    return response.data;
  },

  // Hindsight Memory
  async getMemoryStatus(): Promise<MemoryStatus> {
    const response = await apiClient.get<MemoryStatus>('/memory/status');
    return response.data;
  },

  async getMemoryTimeline(limit: number = 30): Promise<MemoryTimelineResponse> {
    const response = await apiClient.get<MemoryTimelineEvent[] | MemoryTimelineResponse>('/memory/timeline', {
      params: { limit },
    });
    if (Array.isArray(response.data)) {
      return {
        total: response.data.length,
        events: response.data,
      };
    }
    return response.data;
  },

  // Demo Controls
  async resetDemo(): Promise<{ status: string; reset_incidents: string[]; message: string }> {
    const response = await apiClient.post('/incidents/reset-demo');
    return response.data;
  },

  async seedFresh(): Promise<{ status: string; reloaded_count: number }> {
    const response = await apiClient.post('/incidents/seed-fresh');
    return response.data;
  },
};

export default api;
