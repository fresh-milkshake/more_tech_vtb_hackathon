import React, { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useGetVacancies } from '@/services/queries/vacancies';
import { VacanciesFiltersForm } from '@/components/forms/vacancies-filters-form';
import { VacancyList } from '@/components/vacancies-components/vacancies-list';
import { VacanciesPagination } from '@/components/vacancies-components/vacancies-pagination';
import { CreateVacancyDialog } from '@/components/modals/create-vacancy-dialog';
import { Breadcrumbs } from '@/components/shared/breadcrumbs';

interface VacancyFilters {
  search: string;
  is_active: boolean | undefined;
}

export const VacanciesPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const pageParam = searchParams.get('page');
  const currentPage = pageParam ? parseInt(pageParam, 10) : 1;

  const filters: VacancyFilters = {
    search: searchParams.get('search') || '',
    is_active: (() => {
      const val = searchParams.get('is_active');
      if (val === 'true') return true;
      if (val === 'false') return false;
      return undefined;
    })(),
  };

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [currentPage]);

  const setFilters = (newFilters: VacancyFilters) => {
    const params = new URLSearchParams(searchParams);

    if (newFilters.search) params.set('search', newFilters.search);
    else params.delete('search');

    if (newFilters.is_active !== undefined)
      params.set('is_active', String(newFilters.is_active));
    else params.delete('is_active');

    params.set('page', '1');
    setSearchParams(params);
  };

  const setPage = (page: number) => {
    const params = new URLSearchParams(searchParams);
    params.set('page', String(page));
    setSearchParams(params);
  };

  const { data, isLoading, error, isFetching } = useGetVacancies({
    page: currentPage,
    per_page: 10,
    ...(filters.search && { search: filters.search }),
    ...(filters.is_active !== undefined && { is_active: filters.is_active }),
  });

  if (error) {
    return (
      <div className="text-center py-10">
        <p className="text-red-500">Ошибка загрузки вакансий</p>
        <Button
          onClick={() => window.location.reload()}
          className="mt-4"
          variant="outline"
        >
          Повторить попытку
        </Button>
      </div>
    );
  }

  const vacancies = data?.vacancies || [];
  const totalPages = data?.total_pages || 1;

  return (
    <div>
      <Breadcrumbs className="mb-4" />

      <div className="flex justify-between items-center mb-4">
        <VacanciesFiltersForm
          filters={filters}
          onChange={setFilters}
          onClear={() => setFilters({ search: '', is_active: undefined })}
        />
        <CreateVacancyDialog />
      </div>

      {/* Используем isFetching для отображения скелетона при переходе по страницам */}
      <VacancyList vacancies={vacancies} isLoading={isLoading || isFetching} />

      {data && data.total > 0 && (
        <div className="flex flex-col items-center gap-4 mt-6">
          <p className="text-sm text-muted-foreground">
            Показано {vacancies.length} из {data.total} вакансий
          </p>

          <VacanciesPagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setPage}
          />
        </div>
      )}

      {data?.total === 0 && (
        <div className="text-center py-10">
          <p className="text-muted-foreground">Вакансии не найдены</p>
          <Button
            variant="ghost"
            onClick={() => setFilters({ search: '', is_active: undefined })}
            className="mt-2"
          >
            Сбросить фильтры
          </Button>
        </div>
      )}
    </div>
  );
};
