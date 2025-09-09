import api, { handleApiError } from '..';
import { toast } from 'sonner';
import type {
  IInterview,
  IInterviewsRequestParams,
  IInterviewsResponse,
  IInterviewSummary,
  IInterviewTimeline,
  IInterviewStatus,
  IInterviewStats,
  ICreateInterviewRequestParams,
} from './interviews.types';

// Список интервью
export const getInterviews = async (
  params: IInterviewsRequestParams = {}
): Promise<IInterviewsResponse | null> => {
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
    const url = `/interviews${queryString ? `?${queryString}` : ''}`;

    const { data } = await api.get<IInterviewsResponse>(url);
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при получении интервью');
    toast.error('Ошибка', {
      description: 'Не удалось получить список интервью',
    });
    return null;
  }
};

export const getInterviewById = async (
  id: string
): Promise<IInterview | null> => {
  try {
    const { data } = await api.get<IInterview>(`/interviews/${id}`);
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при получении интервью');
    toast.error('Ошибка', {
      description: 'Не удалось получить информацию об интервью',
    });
    return null;
  }
};

export const createInterview = async (
  interviewData: ICreateInterviewRequestParams
): Promise<IInterview | null> => {
  try {
    const { data } = await api.post<IInterview>('/interviews', interviewData, {
      headers: { 'Content-Type': 'application/json' },
    });
    toast.success('Успех', { description: 'Интервью успешно создано' });
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при создании интервью');
    toast.error('Ошибка', { description: 'Не удалось создать интервью' });
    return null;
  }
};

export const updateInterview = async (
  id: string,
  interviewData: Partial<IInterview>
): Promise<IInterview | null> => {
  try {
    const { data } = await api.put<IInterview>(
      `/interviews/${id}`,
      interviewData,
      {
        headers: { 'Content-Type': 'application/json' },
      }
    );
    toast.success('Успех', { description: 'Интервью успешно обновлено' });
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при обновлении интервью');
    toast.error('Ошибка', { description: 'Не удалось обновить интервью' });
    return null;
  }
};

export const deleteInterview = async (id: string): Promise<boolean> => {
  try {
    await api.delete(`/interviews/${id}`);
    toast.success('Успех', { description: 'Интервью успешно удалено' });
    return true;
  } catch (error) {
    handleApiError(error, 'Ошибка при удалении интервью');
    toast.error('Ошибка', { description: 'Не удалось удалить интервью' });
    return false;
  }
};

export const startInterview = async (id: string): Promise<boolean> => {
  try {
    await api.post(`/interviews/${id}/start`);
    toast.success('Успех', { description: 'Интервью начато' });
    return true;
  } catch (error) {
    handleApiError(error, 'Ошибка при старте интервью');
    toast.error('Ошибка', { description: 'Не удалось начать интервью' });
    return false;
  }
};

export const endInterview = async (id: string): Promise<boolean> => {
  try {
    await api.post(`/interviews/${id}/end`);
    toast.success('Успех', { description: 'Интервью завершено' });
    return true;
  } catch (error) {
    handleApiError(error, 'Ошибка при завершении интервью');
    toast.error('Ошибка', { description: 'Не удалось завершить интервью' });
    return false;
  }
};

export const getInterviewTimeline = async (
  id: string
): Promise<IInterviewTimeline | null> => {
  try {
    const { data } = await api.get<IInterviewTimeline>(
      `/interviews/${id}/timeline`
    );
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при получении таймлайна интервью');
    toast.error('Ошибка', {
      description: 'Не удалось получить таймлайн интервью',
    });
    return null;
  }
};

export const getInterviewSummary = async (
  id: string
): Promise<IInterviewSummary | null> => {
  try {
    const { data } = await api.get<IInterviewSummary>(
      `/interviews/${id}/summary`
    );
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при получении резюме интервью');
    toast.error('Ошибка', {
      description: 'Не удалось получить резюме интервью',
    });
    return null;
  }
};

export const getInterviewStatus = async (
  id: string
): Promise<IInterviewStatus | null> => {
  try {
    const { data } = await api.get<IInterviewStatus>(
      `/interviews/${id}/status`
    );
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при получении статуса интервью');
    toast.error('Ошибка', {
      description: 'Не удалось получить статус интервью',
    });
    return null;
  }
};

export const getInterviewStats = async (): Promise<IInterviewStats | null> => {
  try {
    const { data } = await api.get<IInterviewStats>(
      `/interviews/stats/overview`
    );
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при получении статистики интервью');
    toast.error('Ошибка', {
      description: 'Не удалось получить статистику интервью',
    });
    return null;
  }
};
