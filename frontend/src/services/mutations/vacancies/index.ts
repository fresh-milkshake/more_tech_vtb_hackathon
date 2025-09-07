import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  createVacancy,
  updateVacancy,
  deleteVacancy,
} from '@/services/api/vacancies';
import type { IVacancy } from '@/services/api/vacancies/vacancies.types';
import { toast } from 'sonner';

export const useCreateVacancy = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Omit<IVacancy, 'id'>) => createVacancy(data),
    onSuccess: (vacancy) => {
      if (!vacancy) return;
      toast.success('Вакансия создана');
      queryClient.invalidateQueries({ queryKey: ['get-vacancies'] });
    },
    onError: () => toast.error('Не удалось создать вакансию'),
  });
};

export const useUpdateVacancy = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: Partial<IVacancy> }) =>
      updateVacancy(id, data),
    onSuccess: (vacancy) => {
      if (!vacancy) return;
      toast.success('Вакансия обновлена');
      queryClient.invalidateQueries({
        queryKey: ['get-vacancy-by-id', vacancy.id],
      });
      queryClient.invalidateQueries({ queryKey: ['get-vacancies'] });
    },
    onError: () => toast.error('Не удалось обновить вакансию'),
  });
};

export const useDeleteVacancy = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (id: number) => deleteVacancy(id),
    onSuccess: () => {
      toast.success('Вакансия удалена');
      queryClient.invalidateQueries({ queryKey: ['get-vacancies'] });
    },
    onError: () => toast.error('Не удалось удалить вакансию'),
  });
};
