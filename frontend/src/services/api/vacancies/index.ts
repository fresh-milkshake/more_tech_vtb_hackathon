import api, { handleApiError } from '..';
import { toast } from 'sonner';
import type {
  IVacancy,
  IVacanciesRequestParams,
  IVacanciesResponse,
} from './vacancies.types';

export const getVacancies = async (
  params: IVacanciesRequestParams = {}
): Promise<IVacanciesResponse | null> => {
  try {
    const searchParams = new URLSearchParams();

    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        if (typeof value === 'boolean') {
          searchParams.append(key, value.toString());
        } else {
          searchParams.append(key, String(value));
        }
      }
    });

    const queryString = searchParams.toString();
    const url = `/vacancies${queryString ? `?${queryString}` : ''}`;

    const { data } = await api.get<IVacanciesResponse>(url);
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при получении вакансий');
    toast.error('Ошибка', {
      description: 'Не удалось получить список вакансий',
    });
    return null;
  }
};

export const getVacancyById = async (id: number): Promise<IVacancy | null> => {
  try {
    const { data } = await api.get<IVacancy>(`/vacancies/${id}`);
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при получении вакансии');
    toast.error('Ошибка', {
      description: 'Не удалось получить информацию о вакансии',
    });
    return null;
  }
};

export const createVacancy = async (
  vacancyData: Omit<IVacancy, 'id'>
): Promise<IVacancy | null> => {
  try {
    const { data } = await api.post<IVacancy>('/vacancies', vacancyData, {
      headers: { 'Content-Type': 'application/json' },
    });
    toast.success('Успех', { description: 'Вакансия успешно создана' });
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при создании вакансии');
    toast.error('Ошибка', { description: 'Не удалось создать вакансию' });
    return null;
  }
};

export const updateVacancy = async (
  id: number,
  vacancyData: Partial<IVacancy>
): Promise<IVacancy | null> => {
  try {
    const { data } = await api.put<IVacancy>(`/vacancies/${id}`, vacancyData, {
      headers: { 'Content-Type': 'application/json' },
    });
    toast.success('Успех', { description: 'Вакансия успешно обновлена' });
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при обновлении вакансии');
    toast.error('Ошибка', { description: 'Не удалось обновить вакансию' });
    return null;
  }
};

export const deleteVacancy = async (id: number): Promise<boolean> => {
  try {
    await api.delete(`/vacancies/${id}`);
    toast.success('Успех', { description: 'Вакансия успешно удалена' });
    return true;
  } catch (error) {
    handleApiError(error, 'Ошибка при удалении вакансии');
    toast.error('Ошибка', { description: 'Не удалось удалить вакансию' });
    return false;
  }
};
