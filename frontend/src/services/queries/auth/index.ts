// src/services/queries/auth/index.ts
import { useQuery } from '@tanstack/react-query';
import { getCurrentUser } from '../../api/auth';
import { LocalStorageNames } from '@/constants';
import type { IUser } from '@/types';

export const useGetCurrentUserInfo = () => {
  const getCachedUser = (): IUser | null => {
    try {
      const cached = localStorage.getItem(LocalStorageNames.USER);
      return cached ? JSON.parse(cached) : null;
    } catch {
      return null;
    }
  };

  const cachedUser = getCachedUser();
  const lastUpdated = localStorage.getItem(LocalStorageNames.USER_UPDATED_AT);
  const isStale = lastUpdated
    ? Date.now() - parseInt(lastUpdated, 10) > 1000 * 60 * 5
    : true;

  return useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const user = await getCurrentUser();
      if (user) {
        localStorage.setItem(LocalStorageNames.USER, JSON.stringify(user));
        localStorage.setItem(
          LocalStorageNames.USER_UPDATED_AT,
          Date.now().toString()
        );
      } else {
        localStorage.removeItem(LocalStorageNames.USER);
        localStorage.removeItem(LocalStorageNames.USER_UPDATED_AT);
      }
      return user;
    },
    staleTime: 1000 * 60 * 5, // 5 минут
    ...(cachedUser && !isStale ? { initialData: cachedUser } : {}),
  });
};
