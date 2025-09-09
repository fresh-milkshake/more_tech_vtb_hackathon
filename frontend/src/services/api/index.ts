import axios, { AxiosError } from 'axios';
import { LocalStorageNames } from '@/constants';
import { logout } from '@/store/auth-store';

interface ApiErrorResponse {
  message?: string;
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

// функция для установки токена вручную
export const setApiToken = (token: string | null) => {
  if (token) {
    api.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common.Authorization;
  }
};

// интерсептор на случай если токен в localStorage есть
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(LocalStorageNames.TOKEN);
  if (token) {
    config.headers = config.headers ?? {};
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// глобальная обработка 401/403
api.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error.response?.status;
    const url = error.config?.url || '';

    if (status === 401 && !url.includes('/auth/login')) {
      logout();
      setApiToken(null);
    }

    if (status === 403) {
      logout();
      setApiToken(null);
    }

    return Promise.reject(error);
  }
);

const ws = new WebSocket(import.meta.env.VITE_SOCKET_URL);

export default api;
export { ws };

export const handleApiError = (
  error: unknown,
  defaultMessage: string
): string => {
  if (error instanceof AxiosError) {
    const message =
      (error.response?.data as ApiErrorResponse)?.message ||
      error.response?.statusText ||
      'Неизвестная ошибка';
    return `${defaultMessage}: ${message}`;
  }
  return defaultMessage;
};
