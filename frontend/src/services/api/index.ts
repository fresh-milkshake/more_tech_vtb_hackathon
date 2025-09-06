import axios, { AxiosError } from 'axios';
import { LocalStorageNames } from '@/constants';
import { logout } from '@/store/auth-store';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(LocalStorageNames.TOKEN);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 || error.response?.status === 403) {
      logout();
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
): never => {
  if (error instanceof AxiosError) {
    const message = error.response?.data?.message || 'Неизвестная ошибка';
    throw new Error(`${defaultMessage}: ${message}`);
  }
  throw new Error(defaultMessage);
};
