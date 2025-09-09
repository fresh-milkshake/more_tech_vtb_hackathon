import type { IPaginationParams } from '@/types';

export interface ICandidate {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  resume_text: string;
  linkedin_url: string;
  github_url: string;
  portfolio_url: string;
  skills: string[];
  experience_years: string;
  current_position: string;
  current_company: string;
  applied_position: string;
  notes: string;
  created_at: string;
  updated_at: string;
}

export interface IInterviewPlan {
  [key: string]: unknown;
}

export interface IInterview {
  position: string;
  interview_type: 'technical' | 'hr' | 'manager' | 'final';
  scheduled_at: string;
  max_questions: number;
  estimated_duration: number;
  interview_plan: IInterviewPlan;
  candidate_id: string;
  interviewer_id: string;
}

export interface ICandidatesRequestParams extends IPaginationParams {
  search?: string;
  applied_position?: string;
  experience_years?: string;
  status?: string;
  skills?: string;
  created_at_from?: string; // ISO date
  created_at_to?: string; // ISO date
}

export interface ICandidatesResponse {
  candidates: ICandidate[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}
