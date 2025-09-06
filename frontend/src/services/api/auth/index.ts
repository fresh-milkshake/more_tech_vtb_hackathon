import api, { handleApiError } from '..';
import { toast } from 'sonner';
import type {
  IAuthorizationRequestData,
  IAuthorizationCredentials,
  IRegistrationRequestData,
  IRegistrationCredentials,
} from './auth.types';
import type { IUser } from '@/types';

export const authorization = async (requestData: IAuthorizationRequestData) => {
  try {
    const params = new URLSearchParams();
    Object.entries(requestData).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, String(value));
      }
    });

    return await api.post<IAuthorizationCredentials>('/auth/login', params, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  } catch (error) {
    handleApiError(error, 'Ошибка при авторизации');
    toast.error('Ошибка', { description: 'Не удалось войти' });
  }
};

export const registration = async (requestData: IRegistrationRequestData) => {
  try {
    return await api.post<IRegistrationCredentials>(
      '/auth/register',
      requestData,
      {
        headers: { 'Content-Type': 'application/json' },
      }
    );
  } catch (error) {
    handleApiError(error, 'Ошибка при регистрации');
    toast.error('Ошибка', { description: 'Не удалось зарегистрироваться' });
  }
};

export const getCurrentUser = async (): Promise<IUser | null> => {
  try {
    const { data } = await api.get<IUser>('/auth/me');
    return data;
  } catch (error) {
    handleApiError(error, 'Ошибка при получении данных пользователя');
    return null;
  }
};
