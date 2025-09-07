export interface IUser {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

export interface IPaginationParams {
  page?: number;
  per_page?: number;
}
