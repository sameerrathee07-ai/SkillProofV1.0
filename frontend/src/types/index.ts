export interface User {
  id: number;
  email: string;
  name: string;
  role: 'poster' | 'solver';
  created_at: string;
}

export interface Problem {
  id: number;
  poster_id: number;
  description: string;
  category: string;
  budget_range: string;
  timeline: string;
  status: 'open' | 'closed';
  created_at: string;
  poster_name?: string;
}

export interface PitchSession {
  id: number;
  user_id: number;
  problem_id: number;
  started_at: string;
  completed: boolean;
  pitch_text: string;
  scores_json: string | null;
  current_step: number;
  attempt_no: number;
}

export interface Message {
  id: number;
  session_id: number;
  role: 'assistant' | 'user';
  content: string;
  created_at: string;
}

export interface DimensionScore {
  dimension: string;
  score: number;
}

export interface Proposal {
  id: number;
  problem_id: number;
  solver_id: number;
  pitch_session_id: number;
  gate_score: number | null;
  dimension_scores: string | null;
  feedback: string | null;
  status: 'needs_work' | 'submitted';
  attempts: number;
  pdf_downloads: number;
  created_at: string;
  solver_name?: string;
  problem_title?: string;
  solver_credibility?: Credibility;
}

export interface Credibility {
  avg_gate_score: number;
  first_attempt_passes: number;
  total_attempts: number;
  total_passes: number;
}

export interface TokenBalance {
  balance: number;
}

export interface TokenPackage {
  id: string;
  name: string;
  price_rs: number;
  tokens: number;
}

export interface ValidationError {
  field: string;
  message: string;
}

export interface ProblemValidationResponse {
  valid: boolean;
  errors: ValidationError[];
}

export interface PitchChatResponse {
  reply: string;
  current_step: number;
  pitch_complete: boolean;
  remaining_tokens: number;
}

export interface ScoreResponse {
  gate_passed: boolean;
  gate_score: number;
  dimension_scores: DimensionScore[];
  feedback: string;
  proposal_id: number | null;
  status: 'needs_work' | 'submitted';
}