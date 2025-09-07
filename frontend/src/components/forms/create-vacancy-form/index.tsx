// src/components/forms/vacancy-form.tsx
import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import {
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
} from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import type { IVacancy } from '@/services/api/vacancies/vacancies.types';

const vacancySchema = z.object({
  title: z.string().min(3, 'Введите название вакансии'),
  description: z.string().min(5, 'Введите описание'),
  requirements: z.string().min(3, 'Укажите требования'),
  responsibilities: z.string().min(3, 'Укажите обязанности'),
  company_name: z.string().min(2, 'Введите название компании'),
  location: z.string().min(2, 'Укажите локацию'),
  salary_range: z.string().optional(),
  employment_type: z.string().optional(),
  experience_level: z.string().optional(),
});

export type VacancyFormValues = z.infer<typeof vacancySchema>;

interface VacancyFormProps {
  defaultValues?: Partial<IVacancy>;
  onSubmit: (values: VacancyFormValues) => void;
  isSubmitting?: boolean;
}

export const CreateVacancyForm: React.FC<VacancyFormProps> = ({
  defaultValues,
  onSubmit,
  isSubmitting,
}) => {
  const form = useForm<VacancyFormValues>({
    resolver: zodResolver(vacancySchema),
    defaultValues: {
      title: defaultValues?.title ?? '',
      description: defaultValues?.description ?? '',
      requirements: defaultValues?.requirements ?? '',
      responsibilities: defaultValues?.responsibilities ?? '',
      company_name: defaultValues?.company_name ?? '',
      location: defaultValues?.location ?? '',
      salary_range: defaultValues?.salary_range ?? '',
      employment_type: defaultValues?.employment_type ?? '',
      experience_level: defaultValues?.experience_level ?? '',
    },
  });

  const handleSubmit = (values: VacancyFormValues) => {
    onSubmit(values);
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="title"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Название вакансии</FormLabel>
              <FormControl>
                <Input placeholder="Backend разработчик Python" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="description"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Описание</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Разработка и поддержка серверной части..."
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="requirements"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Требования</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Python, Django, PostgreSQL..."
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="responsibilities"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Обязанности</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="Разработка API, работа с БД..."
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="company_name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Компания</FormLabel>
              <FormControl>
                <Input placeholder="Digital Agency" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="location"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Локация</FormLabel>
              <FormControl>
                <Input placeholder="Санкт-Петербург" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <div className="grid grid-cols-3 gap-4">
          <FormField
            control={form.control}
            name="salary_range"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Зарплата</FormLabel>
                <FormControl>
                  <Input placeholder="150000-220000" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="employment_type"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Тип занятости</FormLabel>
                <FormControl>
                  <Input placeholder="Полная занятость" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="experience_level"
            render={({ field }) => (
              <FormItem>
                <FormLabel>Уровень</FormLabel>
                <FormControl>
                  <Input placeholder="Senior" {...field} />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <Button type="submit" disabled={isSubmitting}>
          {isSubmitting ? 'Сохраняем...' : 'Сохранить'}
        </Button>
      </form>
    </Form>
  );
};
