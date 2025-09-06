import { create } from 'zustand';
import { LocalStorageNames } from '@/constants';
import { jwtDecode } from 'jwt-decode';
import type { IUser } from '@/types';
type State = {
  isLoggedIn: boolean;
  user: Nullable<IUser>;
};

type Actions = {
  logout: () => void;
  login: () => void;
  setUser: (user: Nullable<IUser>) => void;
};

const decodeToken = (token: string): Nullable<IUser> => {
  try {
    return jwtDecode<IUser>(token);
  } catch (error) {
    console.error(`Произошла ошибка при декодировании токена: ${error}`);
    return null;
  }
};

const getInitialUserState = (): Pick<State, 'isLoggedIn' | 'user'> => {
  const token = localStorage.getItem(LocalStorageNames.TOKEN);
  const user = token ? decodeToken(token) : null;
  const isLoggedIn = !!user;
  return { user, isLoggedIn };
};

export const useAuthStore = create<State & Actions>((set, get) => ({
  ...getInitialUserState(),
  setUser: (user) => set({ user, isLoggedIn: !!user }),
  logout: () => {
    localStorage.removeItem(LocalStorageNames.TOKEN);
    localStorage.removeItem(LocalStorageNames.REFRESH_TOKEN);
    localStorage.removeItem(LocalStorageNames.USER);
    localStorage.removeItem(LocalStorageNames.USER_UPDATED_AT);

    set({ user: null, isLoggedIn: false });
  },
  login: () => {
    const token = localStorage.getItem(LocalStorageNames.TOKEN);
    if (token) {
      try {
        const decodedUserData = jwtDecode<IUser>(token);
        set({ user: decodedUserData, isLoggedIn: true });
      } catch (error) {
        console.error(`Ошибка авторизации: ${error}`);
        get().logout();
      }
    }
  },
}));

export const logout = () => useAuthStore.getState().logout();
