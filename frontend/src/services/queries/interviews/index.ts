import { useQuery } from '@tanstack/react-query';
import {
  getInterviews,
  getInterviewById,
  getInterviewTimeline,
  getInterviewSummary,
  getInterviewStatus,
  getInterviewStats,
} from '@/services/api/interviews';
import type { IInterviewsRequestParams } from '@/services/api/interviews/interviews.types';
import { keepPreviousData } from '@tanstack/react-query';

export const useGetInterviews = (params: IInterviewsRequestParams = {}) => {
  return useQuery({
    queryKey: ['get-interviews', JSON.stringify(params)],
    queryFn: () => getInterviews(params),
    placeholderData: keepPreviousData,
  });
};

export const useGetInterviewById = (id: string) => {
  return useQuery({
    queryKey: ['get-interview-by-id', id],
    queryFn: () => getInterviewById(id),
    staleTime: 1000 * 60 * 5,
    enabled: !!id,
  });
};

export const useGetInterviewTimeline = (id: string) => {
  return useQuery({
    queryKey: ['get-interview-timeline', id],
    queryFn: () => getInterviewTimeline(id),
    enabled: !!id,
  });
};

export const useGetInterviewSummary = (id: string) => {
  return useQuery({
    queryKey: ['get-interview-summary', id],
    queryFn: () => getInterviewSummary(id),
    enabled: !!id,
  });
};

export const useGetInterviewStatus = (id: string) => {
  return useQuery({
    queryKey: ['get-interview-status', id],
    queryFn: () => getInterviewStatus(id),
    enabled: !!id,
  });
};

export const useGetInterviewStats = () => {
  return useQuery({
    queryKey: ['get-interview-stats'],
    queryFn: () => getInterviewStats(),
    staleTime: 1000 * 60 * 10,
  });
};
