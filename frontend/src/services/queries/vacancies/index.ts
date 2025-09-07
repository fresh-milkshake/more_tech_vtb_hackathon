// src/services/queries/vacancies/index.ts
import { useQuery } from '@tanstack/react-query';
import { getVacancies, getVacancyById } from '../../api/vacancies';
import type { IVacanciesRequestParams } from '@/services/api/vacancies/vacancies.types';
import { keepPreviousData } from '@tanstack/react-query';

export const useGetVacancies = (params: IVacanciesRequestParams = {}) => {
  return useQuery({
    queryKey: ['get-vacancies', JSON.stringify(params)],
    queryFn: () => getVacancies(params),
    placeholderData: keepPreviousData,
  });
};

export const useGetVacancyById = (id: number) => {
  return useQuery({
    queryKey: ['get-vacancy-by-id', id],
    queryFn: () => getVacancyById(id),
    staleTime: 1000 * 60 * 5,
    enabled: !!id,
  });
};
