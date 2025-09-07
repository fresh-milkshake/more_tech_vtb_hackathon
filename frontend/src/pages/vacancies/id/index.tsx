import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useGetVacancyById } from '@/services/queries/vacancies';
import { useUpdateVacancy } from '@/services/mutations/vacancies';
import {
  Card,
  CardHeader,
  CardContent,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Briefcase,
  MapPin,
  DollarSign,
  Clock,
  Calendar,
  Pencil,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { CreateVacancyForm } from '@/components/forms/create-vacancy-form';
import type { VacancyFormValues } from '@/components/forms/create-vacancy-form';
import { Loader } from '@/components/common/loader';
import { Breadcrumbs } from '@/components/shared/breadcrumbs';

export const VacancyPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const vacancyId = Number(id);

  const { data: vacancy, isLoading, error } = useGetVacancyById(vacancyId);
  const updateVacancyMutation = useUpdateVacancy();

  if (isLoading) return <Loader />;

  if (error || !vacancy) {
    return (
      <div className="text-center py-10">
        <p className="text-red-500">Вакансия не найдена или произошла ошибка</p>
        <Link to="/vacancies">
          <Button variant="outline" className="mt-4">
            Вернуться к списку вакансий
          </Button>
        </Link>
      </div>
    );
  }

  const handleUpdateVacancy = (values: VacancyFormValues) => {
    updateVacancyMutation.mutate({
      id: vacancy.id,
      data: {
        ...values,
        updated_at: new Date().toISOString(),
      },
    });
  };

  return (
    <div className="mt-6 space-y-6">
      <Breadcrumbs extraLabel={vacancy.title} />

      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle className="text-3xl">{vacancy.title}</CardTitle>
              <CardDescription className="flex items-center gap-2 mt-2">
                <Briefcase className="w-4 h-4" />
                {vacancy.company_name}
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Badge variant="secondary">{vacancy.experience_level}</Badge>

              {/* Кнопка редактирования */}
              <Dialog>
                <DialogTrigger asChild>
                  <Button size="icon" variant="outline">
                    <Pencil className="w-4 h-4" />
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-lg">
                  <DialogHeader>
                    <DialogTitle>Редактировать вакансию</DialogTitle>
                  </DialogHeader>

                  <CreateVacancyForm
                    defaultValues={{
                      title: vacancy.title,
                      description: vacancy.description,
                      requirements: vacancy.requirements,
                      responsibilities: vacancy.responsibilities,
                      company_name: vacancy.company_name,
                      location: vacancy.location,
                      salary_range: vacancy.salary_range,
                      employment_type: vacancy.employment_type,
                      experience_level: vacancy.experience_level,
                    }}
                    onSubmit={handleUpdateVacancy}
                    isSubmitting={updateVacancyMutation.isPending}
                  />
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex items-center gap-2 text-sm">
              <MapPin className="w-4 h-4 text-muted-foreground" />
              <span>{vacancy.location}</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <DollarSign className="w-4 h-4 text-muted-foreground" />
              <span>{vacancy.salary_range} ₽</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Clock className="w-4 h-4 text-muted-foreground" />
              <span>{vacancy.employment_type}</span>
            </div>
            <div className="flex items-center gap-2 text-sm">
              <Calendar className="w-4 h-4 text-muted-foreground" />
              <span>
                Создано: {new Date(vacancy.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>

          <div>
            <Badge
              variant={vacancy.is_active ? 'default' : 'destructive'}
              className="text-sm"
            >
              {vacancy.is_active ? 'Активная' : 'Неактивная'}
            </Badge>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2">Описание</h3>
            <p className="text-sm text-muted-foreground">
              {vacancy.description}
            </p>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2">Требования</h3>
            <p className="text-sm text-muted-foreground">
              {vacancy.requirements}
            </p>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2">Обязанности</h3>
            <p className="text-sm text-muted-foreground">
              {vacancy.responsibilities}
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
