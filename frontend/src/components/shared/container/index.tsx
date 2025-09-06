import React from 'react';
import { cn } from '@/lib/utils';

interface ContainerProps {
  children: React.ReactNode;
  className?: string;
}

export const Container: React.FC<ContainerProps> = ({
  children,
  className = '',
}) => {
  return (
    <div className={cn('mx-auto max-w-[1920px] px-8 sm:px-4', className)}>
      {children}
    </div>
  );
};
