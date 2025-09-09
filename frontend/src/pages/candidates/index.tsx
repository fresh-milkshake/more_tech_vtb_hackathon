import React from 'react';
import { useSearchParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useGetCandidates } from '@/services/queries/candidates';
import { CandidatesList } from '@/components/candidates-components/candidates-list';
import { CandidatesPagination } from '@/components/candidates-components/candidates-pagination';
import { Breadcrumbs } from '@/components/shared/breadcrumbs';

export const CandidatesPage: React.FC<{ className?: string }> = ({
  className,
}) => {
  const [searchParams, setSearchParams] = useSearchParams();

  const pageParam = searchParams.get('page');
  const currentPage = pageParam ? parseInt(pageParam, 10) : 1;

  const setPage = (page: number) => {
    const params = new URLSearchParams(searchParams);
    params.set('page', String(page));
    setSearchParams(params);
  };

  const { data, isLoading, error } = useGetCandidates({
    page: currentPage,
    per_page: 10,
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
        </div>
      )}
    </div>
  );
};
