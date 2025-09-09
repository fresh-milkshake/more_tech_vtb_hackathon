import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  createInterview,
  updateInterview,
  deleteInterview,
  startInterview,
  endInterview,
} from '@/services/api/interviews';
import type {
  IInterview,
  ICreateInterviewRequestParams,
} from '@/services/api/interviews/interviews.types';
import { toast } from 'sonner';

export const useCreateInterview = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: ICreateInterviewRequestParams) => createInterview(data),
    onSuccess: (interview) => {
      if (!interview) return;
      toast.success('Интервью создано');
      queryClient.invalidateQueries({ queryKey: ['get-interviews'] });
    },
    onError: () => toast.error('Не удалось создать интервью'),
  });
};

export const useUpdateInterview = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<IInterview> }) =>
      updateInterview(id, data),
    onSuccess: (interview) => {
      if (!interview) return;
      toast.success('Интервью обновлено');
      queryClient.invalidateQueries({
        queryKey: ['get-interview-by-id', interview.id],
      });
      queryClient.invalidateQueries({ queryKey: ['get-interviews'] });
    },
    onError: () => toast.error('Не удалось обновить интервью'),
  });
};

export const useDeleteInterview = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => deleteInterview(id),
    onSuccess: () => {
      toast.success('Интервью удалено');
      queryClient.invalidateQueries({ queryKey: ['get-interviews'] });
    },
    onError: () => toast.error('Не удалось удалить интервью'),
  });
};

export const useStartInterview = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => startInterview(id),
    onSuccess: (_, id) => {
      toast.success('Интервью начато');
      queryClient.invalidateQueries({ queryKey: ['get-interview-status', id] });
      queryClient.invalidateQueries({ queryKey: ['get-interviews'] });
    },
    onError: () => toast.error('Не удалось начать интервью'),
  });
};

export const useEndInterview = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: string) => endInterview(id),
    onSuccess: (_, id) => {
      toast.success('Интервью завершено');
      queryClient.invalidateQueries({ queryKey: ['get-interview-status', id] });
      queryClient.invalidateQueries({ queryKey: ['get-interviews'] });
    },
    onError: () => toast.error('Не удалось завершить интервью'),
  });
};
