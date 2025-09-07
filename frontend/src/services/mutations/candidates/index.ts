// candidates/mutations.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  createCandidate,
  updateCandidate,
  deleteCandidate,
  uploadCandidateResume,
} from '@/services/api/candidates';
import type { ICandidate } from '@/services/api/candidates/candidates.types';
import { toast } from 'sonner';

export const useCreateCandidate = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Omit<ICandidate, 'id'>) => createCandidate(data),
    onSuccess: (candidate) => {
      if (!candidate) return;
      toast.success('Кандидат создан');
      queryClient.invalidateQueries({ queryKey: ['get-candidates'] });
    },
    onError: () => toast.error('Не удалось создать кандидата'),
  });
};

export const useUpdateCandidate = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<ICandidate> }) =>
      updateCandidate(id, data),
    onSuccess: (candidate) => {
      if (!candidate) return;
      toast.success('Кандидат обновлен');
      queryClient.invalidateQueries({
        queryKey: ['get-candidate-by-id', candidate.id],
      });
      queryClient.invalidateQueries({ queryKey: ['get-candidates'] });
    },
    onError: () => toast.error('Не удалось обновить кандидата'),
  });
};

export const useDeleteCandidate = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => deleteCandidate(id),
    onSuccess: () => {
      toast.success('Кандидат удален');
      queryClient.invalidateQueries({ queryKey: ['get-candidates'] });
    },
    onError: () => toast.error('Не удалось удалить кандидата'),
  });
};

export const useUploadCandidateResume = () => {
  return useMutation({
    mutationFn: ({ uuid, file }: { uuid: string; file: File }) =>
      uploadCandidateResume(uuid, file),
    onSuccess: () => {
      toast.success('Резюме загружено');
    },
    onError: () => toast.error('Не удалось загрузить резюме'),
  });
};
