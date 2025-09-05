import type { PropsWithChildren, ReactNode } from 'react';
import { useAuthStore } from '../../store/auth-store';
import { Navigate } from 'react-router';

function ProtectedRoute({ children }: PropsWithChildren): ReactNode {
  const isLoggedIn = useAuthStore((state) => state.isLoggedIn);

  return isLoggedIn ? children : <Navigate to="/auth" replace />;
}

export default ProtectedRoute;
