import { createBrowserRouter, Navigate } from 'react-router-dom';
import { Suspense } from 'react';
import { AuthLayout } from '@/layouts/auth-layout';
import { Layout } from '@/layouts/main-layout';
import { AuthPage } from '@/pages/auth';
import { HomePage } from '@/pages/home';
import { Loader } from '@/components/common/loader';
import AuthProtectedRoute from './auth-protected-route';
import ProtectedRoute from './protected-route';
import { VacanciesPage } from '@/pages/vacancies';
import { CandidatesPage } from '@/pages/candidates';
import { InterviewsPage } from '@/pages/interviews';
import { VacancyPage } from '@/pages/vacancies/id';
import { CurrentCandidatePage } from '@/pages/candidates/id';
import { CurrentInterviewPage } from '@/pages/interviews/id';

const router = createBrowserRouter([
  {
    path: '/auth',
    element: <AuthLayout />,
    children: [
      {
        index: true,
        element: (
          <Suspense fallback={<Loader />}>
            <AuthProtectedRoute>
              <AuthPage />
            </AuthProtectedRoute>
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
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          </Suspense>
        ),
      },
      {
        path: '/vacancies',
        element: (
          <Suspense fallback={<Loader />}>
            <ProtectedRoute>
              <VacanciesPage />
            </ProtectedRoute>
          </Suspense>
        ),
      },
      {
        path: '/vacancies/:id',
        element: (
          <Suspense fallback={<Loader />}>
            <ProtectedRoute>
              <VacancyPage />
            </ProtectedRoute>
          </Suspense>
        ),
      },
      {
        path: '/candidates',
        element: (
          <Suspense fallback={<Loader />}>
            <ProtectedRoute>
              <CandidatesPage />
            </ProtectedRoute>
          </Suspense>
        ),
      },
      {
        path: '/candidates/:id',
        element: (
          <Suspense fallback={<Loader />}>
            <ProtectedRoute>
              <CurrentCandidatePage />
            </ProtectedRoute>
          </Suspense>
        ),
      },
      {
        path: '/interviews',
        element: (
          <Suspense fallback={<Loader />}>
            <ProtectedRoute>
              <InterviewsPage />
            </ProtectedRoute>
          </Suspense>
        ),
      },
      {
        path: '/interviews/:id',
        element: (
          <Suspense fallback={<Loader />}>
            <ProtectedRoute>
              <CurrentInterviewPage />
            </ProtectedRoute>
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
