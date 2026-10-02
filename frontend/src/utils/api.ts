import axios from 'axios';
import type {
  User, Problem, PitchSession, Message, Proposal,
  TokenBalance, TokenPackage, ProblemValidationResponse,
  PitchChatResponse, ScoreResponse, Credibility
} from '../types';

const api = axios.create({
  baseURL: '/api',
  withCredentials: true,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  signup: (data: { email: string; password: string; name: string; role: 'poster' | 'solver' }) =>
    api.post('/auth/signup', data),
  login: (data: { email: string; password: string }) =>
    api.post('/auth/login', data),
  logout: () => api.post('/auth/logout'),
  me: () => api.get<User>('/auth/me'),
};

export const problemsApi = {
  validate: (data: { description: string; category: string; budget_range: string; timeline: string }) =>
    api.post<ProblemValidationResponse>('/problems/validate', data),
  create: (data: { description: string; category: string; budget_range: string; timeline: string }) =>
    api.post<Problem>('/problems', data),
  list: () => api.get<Problem[]>('/problems'),
  get: (id: number) => api.get<Problem>(`/problems/${id}`),
  close: (id: number) => api.patch(`/problems/${id}/close`),
};

export const pitchApi = {
  start: (problemId: number) => api.post<{ session_id: number; current_step: number; message: string; remaining_tokens: number }>(`/problems/${problemId}/pitch/start`),
  get: (sessionId: number) => api.get<PitchSession>(`/pitch/${sessionId}`),
  messages: (sessionId: number) => api.get<Message[]>(`/pitch/${sessionId}/messages`),
  chat: (sessionId: number, answer: string) =>
    api.post<PitchChatResponse>(`/pitch/${sessionId}/chat`, { answer }),
  score: (sessionId: number) => api.post<ScoreResponse>(`/pitch/${sessionId}/score`),
  revise: (proposalId: number) => api.post<{ session_id: number; current_step: number; message: string; remaining_tokens: number }>(`/pitch/proposals/${proposalId}/revise`),
  myProposals: () => api.get<Proposal[]>('/pitch/proposals/mine'),
  problemProposals: (problemId: number) => api.get<Proposal[]>(`/pitch/problems/${problemId}/proposals`),
};

export const tokensApi = {
  balance: () => api.get<TokenBalance>('/tokens/balance'),
  packages: () => api.get<TokenPackage[]>('/tokens/packages'),
  purchase: (packageId: string, idempotencyKey: string) =>
    api.post<{ success: boolean; new_balance: number; tokens_added: number }>('/tokens/purchase', { package_id: packageId, idempotency_key: idempotencyKey }),
};

export const pdfApi = {
  download: (proposalId: number) => api.get(`/pdf/proposals/${proposalId}`, { responseType: 'blob' }),
};

export const solversApi = {
  credibility: (solverId: number) => api.get<Credibility>(`/solvers/${solverId}/credibility`),
};

export default api;