import { useMutation } from '@tanstack/react-query';
import { authorization, registration } from '@/services/api/auth';
import type {
  IAuthorizationRequestData,
  IAuthorizationCredentials,
  IRegistrationRequestData,
  IRegistrationCredentials,
} from '@/services/api/auth/auth.types';
import { useAuthStore } from '@/store/auth-store';
import { LocalStorageNames } from '@/constants';
import { setApiToken } from '@/services/api';

export const useAuthorization = () => {
  const login = useAuthStore((state) => state.login);

  return useMutation<
    IAuthorizationCredentials,
    Error,
    IAuthorizationRequestData
  >({
    mutationFn: async (requestData) => {
      const data = await authorization(requestData);
      if (!data) throw new Error('Неверные логин или пароль');
      return data;
    },
    onSuccess: (data) => {
      // сохраняем токен
      localStorage.setItem(LocalStorageNames.TOKEN, data.access_token);
      // сразу задаём токен в axios
      setApiToken(data.access_token);
      // обновляем Zustand store
      login();
    },
  });
};

export const useRegistration = () => {
  return useMutation<IRegistrationCredentials, Error, IRegistrationRequestData>(
    {
      mutationFn: async (requestData) => {
        const data = await registration(requestData);
        if (!data) throw new Error('Ошибка регистрации, данные отсутствуют');
        return data;
      },
    }
  );
};
