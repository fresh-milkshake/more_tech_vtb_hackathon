import React from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Briefcase, MapPin, DollarSign, Clock } from 'lucide-react';
import type { IVacancy } from '@/services/api/vacancies/vacancies.types';
import { Link } from 'react-router-dom';

export const VacancyCard: React.FC<{ vacancy: IVacancy }> = ({ vacancy }) => (
  <Link to={`/vacancies/${vacancy.id}`} className="h-full">
    <Card className="hover:shadow-md transition-shadow duration-200 h-full flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex justify-between items-start">
          <div>
            <CardTitle className="text-lg">{vacancy.title}</CardTitle>
            <CardDescription className="flex items-center gap-1 mt-1">
              <Briefcase className="w-4 h-4" />
              {vacancy.company_name}
            </CardDescription>
          </div>
          <Badge variant="secondary">{vacancy.experience_level}</Badge>
        </div>
      </CardHeader>

      <CardContent className="flex-1 flex flex-col justify-between">
        <div>
          <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
            {vacancy.description}
          </p>

          <div className="space-y-2">
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
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mt-4">
          <Badge variant="outline" className="text-xs">
            Требования
          </Badge>
          <Badge variant="outline" className="text-xs">
            Обязанности
          </Badge>
        </div>
      </CardContent>
    </Card>
  </Link>
);
