import { useQuery } from '@tanstack/react-query';
import {
  getCandidates,
  getCandidateById,
  getCandidateInterviews,
} from '@/services/api/candidates';
import type { ICandidatesRequestParams } from '@/services/api/candidates/candidates.types';
import { keepPreviousData } from '@tanstack/react-query';

export const useGetCandidates = (params: ICandidatesRequestParams = {}) => {
  return useQuery({
    queryKey: ['get-candidates', JSON.stringify(params)],
    queryFn: () => getCandidates(params),
    placeholderData: keepPreviousData,
  });
};

export const useGetCandidateById = (id: number) => {
  return useQuery({
    queryKey: ['get-candidate-by-id', id],
    queryFn: () => getCandidateById(id),
    staleTime: 1000 * 60 * 5,
    enabled: !!id,
  });
};

export const useGetCandidateInterviews = (id: number) => {
  return useQuery({
    queryKey: ['get-candidate-interviews', id],
    queryFn: () => getCandidateInterviews(id),
    staleTime: 1000 * 60 * 5,
    enabled: !!id,
  });
};
