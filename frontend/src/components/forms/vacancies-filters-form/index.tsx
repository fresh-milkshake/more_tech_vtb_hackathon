import React from 'react';
import { useForm } from 'react-hook-form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search } from 'lucide-react';

interface VacancyFilters {
  search: string;
  is_active: boolean | undefined;
}

export const VacanciesFiltersForm: React.FC<{
  filters: VacancyFilters;
  onChange: (filters: VacancyFilters) => void;
  onClear: () => void;
}> = ({ filters, onChange, onClear }) => {
  const { register, watch, reset } = useForm<{ search: string }>({
    defaultValues: { search: filters.search },
  });

  const searchValue = watch('search');

  React.useEffect(() => {
    reset({ search: filters.search });
  }, [filters.search, reset]);

  React.useEffect(() => {
    const t = setTimeout(() => {
      if (searchValue !== filters.search) {
        onChange({ ...filters, search: searchValue });
      }
    }, 500);
    return () => clearTimeout(t);
  }, [searchValue, filters, onChange]);

  return (
    <div className="mb-6">
      <div className="flex gap-2 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Поиск по вакансиям..."
            {...register('search')}
            className="pl-10"
          />
        </div>
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        <Button
          variant={filters.is_active === true ? 'default' : 'outline'}
          size="sm"
          onClick={() => onChange({ ...filters, is_active: true })}
        >
          Активные
        </Button>
        <Button
          variant={filters.is_active === false ? 'default' : 'outline'}
          size="sm"
          onClick={() => onChange({ ...filters, is_active: false })}
        >
          Неактивные
        </Button>
        <Button
          variant={filters.is_active === undefined ? 'default' : 'outline'}
          size="sm"
          onClick={() => onChange({ ...filters, is_active: undefined })}
        >
          Все
        </Button>
        <Button variant="ghost" size="sm" onClick={onClear}>
          Сбросить фильтры
        </Button>
      </div>
    </div>
  );
};
