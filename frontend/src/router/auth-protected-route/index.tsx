import type { PropsWithChildren, ReactNode } from 'react';
import { Navigate } from 'react-router';
import { useAuthStore } from '../../store/auth-store';

function AuthProtectedRoute({ children }: PropsWithChildren): ReactNode {
  const isLoggedIn = useAuthStore((state) => state.isLoggedIn);

  return isLoggedIn ? <Navigate to="/" /> : children;
}

export default AuthProtectedRoute;
