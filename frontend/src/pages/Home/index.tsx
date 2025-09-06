import React from 'react';
import { AnalyticsDashboard } from '@/components/dashboard';
import { Container } from '@/components/shared/container';

interface Props {
  className?: string;
}

export const HomePage: React.FC<Props> = ({ className }) => {
  return (
    <Container className={className}>
      <div className="py-6">
        <AnalyticsDashboard />
      </div>
    </Container>
  );
};
