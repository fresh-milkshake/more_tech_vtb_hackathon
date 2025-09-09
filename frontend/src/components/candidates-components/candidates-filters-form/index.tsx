import React from 'react';
import { useForm } from 'react-hook-form';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Search } from 'lucide-react';

interface CandidateFilters {
  search?: string;
  applied_position?: string;
  experience_years?: string;
  status?: string;
  skills?: string;
}

export const CandidatesFiltersForm: React.FC<{
  filters: CandidateFilters;
  onChange: (filters: CandidateFilters) => void;
  onClear: () => void;
}> = ({ filters, onChange, onClear }) => {
  const { register, watch, reset } = useForm<CandidateFilters>({
    defaultValues: filters,
  });

  // Дебаунс для всех инпутов
  const watched = watch();
  React.useEffect(() => {
    reset(filters);
  }, [filters, reset]);

  React.useEffect(() => {
    const t = setTimeout(() => {
      onChange({ ...watched });
    }, 500); // дебаунс 500ms
    return () => clearTimeout(t);
  }, [watched, onChange]);

  return (
    <div className="mb-6">
      <div className="flex gap-2 mb-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <Input
            placeholder="Поиск по имени или email..."
            {...register('search')}
            className="pl-10"
          />
        </div>
        <Input
          placeholder="Должность..."
          {...register('applied_position')}
          className="w-1/3"
        />
        <Input
          placeholder="Опыт (годы)..."
          {...register('experience_years')}
          className="w-1/4"
        />
      </div>

      <div className="flex flex-wrap gap-2 mb-6">
        <Input
          placeholder="Навыки (через запятую)..."
          {...register('skills')}
          className="w-1/3"
        />
        {['new', 'in_progress', 'hired'].map((status) => (
          <Button
            key={status}
            variant={filters.status === status ? 'default' : 'outline'}
            size="sm"
            onClick={() => onChange({ ...watched, status })}
          >
            {status === 'new'
              ? 'Новые'
              : status === 'in_progress'
              ? 'В процессе'
              : 'Наняты'}
          </Button>
        ))}
        <Button
          variant={filters.status === '' ? 'default' : 'outline'}
          size="sm"
          onClick={() => onChange({ ...watched, status: '' })}
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
