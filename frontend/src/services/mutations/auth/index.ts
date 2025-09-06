import { useMutation } from '@tanstack/react-query';
import { authorization, registration } from '../../api/auth';
import type {
  IAuthorizationRequestData,
  IAuthorizationCredentials,
  IRegistrationRequestData,
  IRegistrationCredentials,
} from '../../api/auth/auth.types';
import { useAuthStore } from '../../../store/auth-store';
import { LocalStorageNames } from '@/constants';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import type { AxiosError } from 'axios';

export const useAuthorization = () => {
  const login = useAuthStore((state) => state.login);
  const navigate = useNavigate();

  return useMutation<
    IAuthorizationCredentials,
    AxiosError | Error,
    IAuthorizationRequestData
  >({
    mutationFn: async (requestData) => {
      const response = await authorization(requestData);
      if (!response?.data)
        throw new Error('Ошибка авторизации, данные отсутствуют');
      return response.data;
    },
    onSuccess: (data) => {
      localStorage.setItem(LocalStorageNames.TOKEN, data.access_token);
      login();
      toast.success('Успех', { description: 'Вы успешно вошли в систему' });
      navigate('/');
    },
    onError: (error) => {
      console.error('Ошибка в мутации авторизации:', error);
      toast.error('Ошибка', {
        description: error?.message || 'Не удалось войти',
      });
    },
  });
};

export const useRegistration = () => {
  return useMutation<
    IRegistrationCredentials,
    AxiosError | Error,
    IRegistrationRequestData
  >({
    mutationFn: async (requestData) => {
      const response = await registration(requestData);
      if (!response?.data)
        throw new Error('Ошибка регистрации, данные отсутствуют');
      return response.data;
    },
    onSuccess: () => {
      toast.success('Успех', {
        description: 'Регистрация прошла успешно. Теперь вы можете войти.',
      });
    },
    onError: (error) => {
      console.error('Ошибка в мутации регистрации:', error);
      toast.error('Ошибка', {
        description: error?.message || 'Не удалось зарегистрироваться',
      });
    },
  });
};
