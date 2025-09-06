import React from 'react';
import AuthForm from '@/components/forms/auth-form';
import { cn } from '@/lib/utils';

interface Props {
  className?: string;
}

export const AuthPage: React.FC<Props> = ({ className }) => {
  return (
    <div
      className={cn('flex items-center justify-center min-h-screen', className)}
    >
      <AuthForm />
    </div>
  );
};
