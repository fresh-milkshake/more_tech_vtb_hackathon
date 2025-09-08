import { AxiosError } from 'axios';
import api, { handleApiError } from '..';
import type {
  IAuthorizationRequestData,
  IAuthorizationCredentials,
  IRegistrationRequestData,
  IRegistrationCredentials,
} from './auth.types';
import type { IUser } from '@/types';

export const authorization = async (
  requestData: IAuthorizationRequestData
): Promise<IAuthorizationCredentials> => {
  try {
    const params = new URLSearchParams();
    Object.entries(requestData).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        params.append(key, String(value));
      }
    });

    const response = await api.post<IAuthorizationCredentials>(
      '/auth/login',
      params,
      {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      }
    );

    if (!response?.data) {
      throw new Error('Неверные логин или пароль');
    }

    return response.data;
  } catch (error: unknown) {
    if (error instanceof AxiosError && error.response?.status === 401) {
      throw new Error('Неверные логин или пароль');
    }
    throw new Error(handleApiError(error, 'Ошибка при авторизации'));
  }
};

export const registration = async (
  requestData: IRegistrationRequestData
): Promise<IRegistrationCredentials> => {
  try {
    const response = await api.post<IRegistrationCredentials>(
      '/auth/register',
      requestData,
      {
        headers: { 'Content-Type': 'application/json' },
      }
    );

    if (!response?.data) {
      throw new Error('Ошибка регистрации, данные отсутствуют');
    }

    return response.data;
  } catch (error: unknown) {
    throw new Error(handleApiError(error, 'Ошибка при регистрации'));
  }
};

export const getCurrentUser = async (): Promise<IUser | null> => {
  try {
    const { data } = await api.get<IUser>('/auth/me');
    return data;
  } catch (error: unknown) {
    throw new Error(
      handleApiError(error, 'Ошибка при получении данных пользователя')
    );
  }
};
