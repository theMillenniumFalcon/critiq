import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface AnalyzeRequest {
  repo_url: string;
  pr_number: number;
  github_token?: string;
  analysis_types?: string[];
  priority?: 'low' | 'normal' | 'high';
}

export interface AnalyzeResponse {
  task_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  message: string;
  estimated_completion_time?: string;
}

export const analyzeAPI = {
  submitAnalysis: async (data: AnalyzeRequest) => {
    const response = await apiClient.post<AnalyzeResponse>('/api/v1/analyze', data);
    return response.data;
  },
  
  getTaskStatus: async (taskId: string) => {
    const response = await apiClient.get<AnalyzeResponse>(`/api/v1/tasks/${taskId}`);
    return response.data;
  },
};