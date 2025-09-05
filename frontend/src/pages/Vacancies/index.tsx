import React from 'react';

interface Props {
  className?: string;
}

export const VacanciesPage: React.FC<Props> = ({ className }) => {
  return <div className={className}>this is vacancies</div>;
};
