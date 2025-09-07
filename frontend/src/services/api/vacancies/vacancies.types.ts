import type { IPaginationParams } from '@/types';

export interface IVacancy {
  id: number;
  title: string;
  description: string;
  requirements: string;
  responsibilities: string;
  company_name: string;
  location: string;
  salary_range: string;
  employment_type: string;
  experience_level: string;

  // новые поля
  is_active: boolean;
  is_published: boolean;
  document_status: 'pending' | 'approved' | 'rejected' | 'draft';
  created_by_user_id: number;
  created_at: string;
  updated_at: string;
  interview_links_count: number;
}

export interface IVacanciesRequestParams extends IPaginationParams {
  search?: string;
  is_active?: boolean;
}

export interface IVacanciesResponse {
  vacancies: IVacancy[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}
