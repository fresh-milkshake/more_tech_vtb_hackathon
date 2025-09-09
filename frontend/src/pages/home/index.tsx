import React from 'react';
import { Link } from 'react-router-dom';
import { AnalyticsDashboard } from '@/components/dashboard';
import { Container } from '@/components/shared/container';
import { Badge } from '@/components/ui/badge';
import { Users, Briefcase, Calendar } from 'lucide-react';
import { cn } from '@/lib/utils';

interface Props {
  className?: string;
}

export const HomePage: React.FC<Props> = ({ className }) => {
  return (
    <Container className={cn(className, '!px-0')}>
      <div className="py-6">
        <div className="flex flex-wrap gap-4 mb-6">
          <Link to="/vacancies">
            <Badge
              variant="outline"
              className="flex items-center gap-2 text-sm py-2 px-4 cursor-pointer hover:shadow-md transition-all duration-200 border-[#0af]"
            >
              <Briefcase className="w-4 h-4 text-[#0af]" />
              <span>Вакансии</span>
            </Badge>
          </Link>

          <Link to="/interviews">
            <Badge
              variant="outline"
              className="flex items-center gap-2 text-sm py-2 px-4 cursor-pointer hover:shadow-md transition-all duration-200 border-[#0af]"
            >
              <Calendar className="w-4 h-4 text-[#0af]" />
              <span>Интервью</span>
            </Badge>
          </Link>

          <Link to="/candidates">
            <Badge
              variant="outline"
              className="flex items-center gap-2 text-sm py-2 px-4 cursor-pointer hover:shadow-md transition-all duration-200 border-[#0af]"
            >
              <Users className="w-4 h-4 text-[#0af]" />
              <span>Кандидаты</span>
            </Badge>
          </Link>

          <Link to="/public-interview/e9328d06-c0c9-45bc-800a-b0be9ce9cecb">
            <Badge
              variant="outline"
              className="flex items-center gap-2 text-sm py-2 px-4 cursor-pointer hover:shadow-md transition-all duration-200 border-[#0af]"
            >
              <span>Моковое интервью</span>
            </Badge>
          </Link>
        </div>
        <AnalyticsDashboard />
      </div>
    </Container>
  );
};
