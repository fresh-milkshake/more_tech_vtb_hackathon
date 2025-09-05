import { create } from 'zustand';
import { LocalStorageNames } from '@/types';
import { jwtDecode } from 'jwt-decode';
import router from '@/router';

type State = {
  isLoggedIn: boolean;
  user: Nullable<IUser>;
};

interface IUser {
  id: number;
  name: string;
  email: string;
}

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
  const isLoggedIn = true;
  return { user, isLoggedIn };
};

export const useAuthStore = create<State & Actions>((set, get) => ({
  ...getInitialUserState(),
  setUser: (user) => set({ user }),
  logout: () => {
    localStorage.removeItem(LocalStorageNames.TOKEN);
    localStorage.removeItem(LocalStorageNames.REFRESH_TOKEN);
    set({ user: null, isLoggedIn: false });
    router.navigate('/auth');
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
