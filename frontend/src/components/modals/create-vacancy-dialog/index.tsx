import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { CreateVacancyForm } from '@/components/forms/create-vacancy-form';
import type { VacancyFormValues } from '@/components/forms/create-vacancy-form';
import { useCreateVacancy } from '@/services/mutations/vacancies';
import type { IVacancy } from '@/services/api/vacancies/vacancies.types';

export const CreateVacancyDialog = () => {
  const createVacancyMutation = useCreateVacancy();

  const handleCreateVacancy = (values: VacancyFormValues) => {
    const now = new Date().toISOString();

    const vacancyData: Omit<IVacancy, 'id'> = {
      ...values,
      salary_range: values.salary_range || '',
      employment_type: values.employment_type || '',
      experience_level: values.experience_level || '',
      is_active: true,
      is_published: false,
      document_status: 'draft',
      created_by_user_id: 1,
      created_at: now,
      updated_at: now,
      interview_links_count: 0,
    };

    createVacancyMutation.mutate(vacancyData);
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button>Создать вакансию</Button>
      </DialogTrigger>

      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Создание вакансии</DialogTitle>
        </DialogHeader>

        <CreateVacancyForm
          onSubmit={handleCreateVacancy}
          isSubmitting={createVacancyMutation.isPending}
        />
      </DialogContent>
    </Dialog>
  );
};
