import React, { useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useGetInterviews } from '@/services/queries/interviews';
import { InterviewsList } from '@/components/interviews-components/interviews-list';
//import { InterviewsPagination } from '@/components/interviews-components/interviews-pagination';
import { Breadcrumbs } from '@/components/shared/breadcrumbs';

export const InterviewsPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();

  const pageParam = searchParams.get('page');
  const currentPage = pageParam ? parseInt(pageParam, 10) : 1;

  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [currentPage]);

  //const setPage = (page: number) => {
  //  const params = new URLSearchParams(searchParams);
  //  params.set('page', String(page));
  //  setSearchParams(params);
  //};

  const { data, isLoading, error, isFetching } = useGetInterviews({
    page: currentPage,
    page_size: 9,
  });

  if (error) {
    return (
      <div className="text-center py-10">
        <p className="text-red-500">Ошибка загрузки интервью</p>
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

  const interviews = data?.interviews || [];
  //const totalPages = data?.total || 1;

  return (
    <div>
      <Breadcrumbs className="mb-4" />

      <InterviewsList
        interviews={interviews}
        isLoading={isLoading || isFetching}
      />

      {/*{data && data.total > 0 && (
        <div className="flex flex-col items-center gap-4 mt-6">
          <p className="text-sm text-muted-foreground">
            Показано {interviews.length} из {data.total} интервью
          </p>

          <InterviewsPagination
            currentPage={currentPage}
            totalPages={totalPages}
            onPageChange={setPage}
          />
        </div>
      )}*/}

      {data?.total === 0 && (
        <div className="text-center py-10">
          <p className="text-muted-foreground">Интервью не найдены</p>
          <Button
            variant="ghost"
            onClick={() => setSearchParams(new URLSearchParams())}
            className="mt-2"
          >
            Сбросить
          </Button>
        </div>
      )}
    </div>
  );
};
