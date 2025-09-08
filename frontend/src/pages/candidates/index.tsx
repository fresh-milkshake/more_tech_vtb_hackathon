import React from 'react';
import { useSearchParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useGetCandidates } from '@/services/queries/candidates';
import { CandidatesFiltersForm } from '@/components/candidates-components/candidates-filters-form';
import { CandidatesList } from '@/components/candidates-components/candidates-list';
import { CandidatesPagination } from '@/components/candidates-components/candidates-pagination';
import { Breadcrumbs } from '@/components/shared/breadcrumbs';

interface CandidateFilters {
  search?: string;
  applied_position?: string;
  experience_years?: string;
  status?: string;
  skills?: string;
}

export const CandidatesPage: React.FC<{ className?: string }> = ({
  className,
}) => {
  const [searchParams, setSearchParams] = useSearchParams();

  const pageParam = searchParams.get('page');
  const currentPage = pageParam ? parseInt(pageParam, 10) : 1;

  const filters: CandidateFilters = {
    search: searchParams.get('search') || '',
    applied_position: searchParams.get('applied_position') || '',
    experience_years: searchParams.get('experience_years') || '',
    status: searchParams.get('status') || '',
    skills: searchParams.get('skills') || '',
  };

  const setFilters = (newFilters: CandidateFilters) => {
    const params = new URLSearchParams(searchParams);

    if (newFilters.search) params.set('search', newFilters.search);
    else params.delete('search');

    if (newFilters.applied_position)
      params.set('applied_position', newFilters.applied_position);
    else params.delete('applied_position');

    if (newFilters.experience_years)
      params.set('experience_years', newFilters.experience_years);
    else params.delete('experience_years');

    if (newFilters.status) params.set('status', newFilters.status);
    else params.delete('status');

    if (newFilters.skills) params.set('skills', newFilters.skills);
    else params.delete('skills');

    params.set('page', '1');
    setSearchParams(params);
  };

  const setPage = (page: number) => {
    const params = new URLSearchParams(searchParams);
    params.set('page', String(page));
    setSearchParams(params);
  };

  const { data, isLoading, error } = useGetCandidates({
    page: currentPage,
    per_page: 10,
    ...(filters.search && { search: filters.search }),
    ...(filters.applied_position && {
      applied_position: filters.applied_position,
    }),
    ...(filters.experience_years && {
      experience_years: filters.experience_years,
    }),
    ...(filters.status && { status: filters.status }),
    ...(filters.skills && { skills: filters.skills }),
  });

  if (error) {
    return (
      <div className="text-center py-10">
        <p className="text-red-500">Ошибка загрузки кандидатов</p>
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

  const candidates = data?.candidates || [];
  const totalPages = data?.total_pages || 1;

  return (
    <div className={className}>
      <Breadcrumbs className="mb-4" />

      <div className="flex justify-between items-center mb-4">
        <CandidatesFiltersForm
          filters={filters}
          onChange={setFilters}
          onClear={() =>
            setFilters({
              search: '',
              applied_position: '',
              experience_years: '',
              status: '',
              skills: '',
            })
          }
        />
      </div>

      <CandidatesList candidates={candidates} isLoading={isLoading} />

      {data && data.total > 0 && (
        <div className="flex flex-col items-center gap-4 mt-6">
          <p className="text-sm text-muted-foreground">
            Показано {candidates.length} из {data.total} кандидатов
          </p>

          <CandidatesPagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setPage}
          />
        </div>
      )}

      {data?.total === 0 && (
        <div className="text-center py-10">
          <p className="text-muted-foreground">Кандидаты не найдены</p>
          <Button
            variant="ghost"
            onClick={() =>
              setFilters({
                search: '',
                applied_position: '',
                experience_years: '',
                status: '',
                skills: '',
              })
            }
            className="mt-2"
          >
            Сбросить фильтры
          </Button>
        </div>
      )}
    </div>
  );
};
