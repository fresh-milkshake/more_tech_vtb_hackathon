import React from 'react';

interface Props {
  className?: string;
}

export const CandidatesPage: React.FC<Props> = ({ className }) => {
  return <div className={className}>Это страница кандидатов bruh</div>;
};
