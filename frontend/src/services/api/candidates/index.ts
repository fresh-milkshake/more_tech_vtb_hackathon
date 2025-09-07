import api, { handleApiError } from '..';
import { toast } from 'sonner';
import type {
  ICandidate,
  ICandidatesRequestParams,
  ICandidatesResponse,
  IInterview,
} from './candidates.types';

export const getCandidates = async (
  params: ICandidatesRequestParams = {}
): Promise<ICandidatesResponse | null> => {
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
    const url = `/candidates${queryString ? `?${queryString}` : ''}`;

    const { data } = await api.get<ICandidatesResponse>(url);
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при получении кандидатов');
    toast.error('Ошибка', {
      description: 'Не удалось получить список кандидатов',
    });
    return null;
  }
};

export const getCandidateById = async (
  id: number
): Promise<ICandidate | null> => {
  try {
    const { data } = await api.get<ICandidate>(`/candidates/${id}`);
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при получении кандидата');
    toast.error('Ошибка', {
      description: 'Не удалось получить информацию о кандидате',
    });
    return null;
  }
};

export const getCandidateInterviews = async (
  id: number
): Promise<IInterview[] | null> => {
  try {
    const { data } = await api.get<IInterview[]>(
      `/candidates/${id}/interviews`
    );
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при получении интервью кандидата');
    toast.error('Ошибка', {
      description: 'Не удалось получить список интервью кандидата',
    });
    return null;
  }
};

export const createCandidate = async (
  candidateData: Omit<ICandidate, 'id'>
): Promise<ICandidate | null> => {
  try {
    const { data } = await api.post<ICandidate>('/candidates', candidateData, {
      headers: { 'Content-Type': 'application/json' },
    });
    toast.success('Успех', { description: 'Кандидат успешно создан' });
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при создании кандидата');
    toast.error('Ошибка', { description: 'Не удалось создать кандидата' });
    return null;
  }
};

export const updateCandidate = async (
  id: number,
  candidateData: Partial<ICandidate>
): Promise<ICandidate | null> => {
  try {
    const { data } = await api.put<ICandidate>(
      `/candidates/${id}`,
      candidateData,
      {
        headers: { 'Content-Type': 'application/json' },
      }
    );
    toast.success('Успех', { description: 'Кандидат успешно обновлен' });
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при обновлении кандидата');
    toast.error('Ошибка', { description: 'Не удалось обновить кандидата' });
    return null;
  }
};

export const deleteCandidate = async (id: number): Promise<boolean> => {
  try {
    await api.delete(`/candidates/${id}`);
    toast.success('Успех', { description: 'Кандидат успешно удален' });
    return true;
  } catch (error) {
    handleApiError(error, 'Ошибка при удалении кандидата');
    toast.error('Ошибка', { description: 'Не удалось удалить кандидата' });
    return false;
  }
};

export const uploadCandidateResume = async (
  uuid: string,
  file: File
): Promise<{ success: boolean; message: string } | null> => {
  try {
    const formData = new FormData();
    formData.append('file', file);

    const { data } = await api.post<{ success: boolean; message: string }>(
      `/candidates/${uuid}/upload-resume`,
      formData,
      {
        headers: { 'Content-Type': 'multipart/form-data' },
      }
    );

    toast.success('Успех', { description: 'Резюме успешно загружено' });
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при загрузке резюме');
    toast.error('Ошибка', { description: 'Не удалось загрузить резюме' });
    return null;
  }
};
