export interface User {
  id: number
  email: string
  name: string
  role: 'poster' | 'solver'
  created_at: string
}

export interface Problem {
  id: number
  poster_id: number
  description: string
  category: string
  budget_range: string
  timeline: string
  status: string
  created_at: string
}

export interface PitchSession {
  id: number
  problem_id: number
  current_step: number
  completed: boolean
  pitch_text: string
  messages: { role: 'assistant' | 'user'; content: string }[]
}

export interface ChatResponse {
  reply: string
  current_step: number
  pitch_complete: boolean
  remaining_tokens: number
}

export interface DimensionScore {
  name: string
  score: number
  feedback: string
}

export interface ScoreResponse {
  passed: boolean
  gate_score: number
  dimension_scores: DimensionScore[]
  feedback: string
  proposal_id?: number
}

export interface Proposal {
  id: number
  problem_id: number
  solver_id: number
  gate_score: number
  dimension_scores: DimensionScore[]
  feedback: string
  status: string
  attempts: number
  created_at: string
  solver_name: string
  solver_credibility?: {
    avg_gate_score: number
    first_attempt_passes: number
    total_passes: number
    total_attempts: number
  }
}

export interface Credibility {
  user_id: number
  avg_gate_score: number
  first_attempt_passes: number
  total_passes: number
  total_attempts: number
}

export interface TokenBalance {
  balance: number
}

export interface Package {
  id: string
  name: string
  price_rs: number
  tokens: number
}