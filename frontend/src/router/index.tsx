import { createBrowserRouter, Navigate } from 'react-router-dom';
import { Suspense } from 'react';
import { AuthLayout } from '@/layouts/auth-layout';
import { Layout } from '@/layouts/main-layout';
import { AuthPage } from '@/pages/Auth';
import { HomePage } from '@/pages/Home';
import { Loader } from '@/components/common/loader';

const router = createBrowserRouter([
  {
    path: '/auth',
    element: <AuthLayout />,
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<Loader />}>
            <AuthPage />
          </Suspense>
        ),
      },
    ],
  },
  {
    path: '/',
    element: <Layout />,
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<Loader />}>
            <HomePage />
          </Suspense>
        ),
      },
    ],
  },
  {
    path: '*',
    element: <Navigate to="/" replace />,
  },
]);

export default router;
