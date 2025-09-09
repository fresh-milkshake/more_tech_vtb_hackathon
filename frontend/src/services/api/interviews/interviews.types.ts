import type { IPaginationParams } from '@/types';

export type InterviewStatus =
  | 'scheduled'
  | 'in_progress'
  | 'completed'
  | 'cancelled';

export type InterviewState = 'START' | 'IN_PROGRESS' | 'PAUSED' | 'ENDED';

export type InterviewType = 'technical' | 'hr' | 'screening' | 'final';

export interface IInterview {
  id: string;
  position: string;
  interview_type: InterviewType;
  scheduled_at: string; // ISO datetime
  max_questions: number;
  estimated_duration: number; // в секундах
  interview_plan: Record<string, unknown>;
  candidate_id: string;
  interviewer_id: string;
  status: InterviewStatus;
  current_state: InterviewState;
  timeline: Array<Record<string, unknown>>; // вместо string[]
  context: Record<string, unknown>;
  started_at: string | null;
  ended_at: string | null;
  total_score: number;
  overall_feedback: string | null;
  recommendation: string | null;
  extra_data: Record<string, unknown>;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface IInterviewsResponse extends IPaginationParams {
  interviews: IInterview[];
}

export interface IInterviewsRequestParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: InterviewStatus;
  type?: InterviewType;
}

export interface IInterviewTimeline {
  events: Array<Record<string, unknown>>;
}

export interface IInterviewSummary {
  id: string;
  candidate_id: string;
  interviewer_id: string;
  total_score: number;
  overall_feedback: string | null;
  recommendation: string | null;
}

export interface IInterviewStatus {
  id: string;
  status: InterviewStatus;
  current_state: InterviewState;
  started_at: string | null;
  ended_at: string | null;
}

export interface IInterviewStats {
  total: number;
  scheduled: number;
  in_progress: number;
  completed: number;
  cancelled: number;
}

export interface ICreateInterviewRequestParams {
  position: string;
  interview_type: InterviewType;
  scheduled_at: string; // ISO datetime
  max_questions: number;
  estimated_duration: number; // в секундах
  interview_plan: Record<string, unknown>;
  candidate_id: string;
  interviewer_id: string;
}
