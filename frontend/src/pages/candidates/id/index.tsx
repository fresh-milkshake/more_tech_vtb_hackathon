import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useGetCandidateById } from '@/services/queries/candidates';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Loader } from '@/components/common/loader';
import { Breadcrumbs } from '@/components/shared/breadcrumbs';
import {
  Mail,
  Phone,
  Linkedin,
  Github,
  Globe,
  Calendar,
  Briefcase,
  Clock,
} from 'lucide-react';

interface Props {
  className?: string;
}

export const CurrentCandidatePage: React.FC<Props> = ({ className }) => {
  const { id } = useParams<{ id: string }>();

  const isValidId = !!id && id.length > 0;

  const {
    data: candidate,
    isLoading,
    error,
  } = useGetCandidateById(isValidId ? id : '');

  if (!isValidId) {
    return (
      <div className="text-center py-10">
        <p className="text-red-500">Некорректный ID кандидата</p>
        <Link to="/candidates">
          <Button variant="outline" className="mt-4">
            Вернуться к списку кандидатов
          </Button>
        </Link>
      </div>
    );
  }

  if (isLoading) {
    return <Loader />;
  }

  if (error) {
    console.error('Error loading candidate:', error);
  }

  if (error || !candidate) {
    return (
      <div className="text-center py-10">
        <p className="text-red-500">Кандидат не найден или произошла ошибка</p>
        <Link to="/candidates">
          <Button variant="outline" className="mt-4">
            Вернуться к списку кандидатов
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className={`mt-6 space-y-6 ${className}`}>
      <Breadcrumbs
        extraLabel={`${candidate.first_name} ${candidate.last_name} | ${candidate.applied_position}`}
      />

      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
            <div>
              <CardTitle className="text-3xl">
                {candidate.first_name} {candidate.last_name}
              </CardTitle>
              <p className="text-muted-foreground mt-1">
                {candidate.applied_position}
              </p>
            </div>
            <Badge variant="secondary">
              {candidate.experience_years} опыта
            </Badge>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Контактная информация */}
          <div>
            <h3 className="text-lg font-semibold mb-3">
              Контактная информация
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="flex items-center gap-2 text-sm">
                <Mail className="w-4 h-4 text-muted-foreground" />
                <a
                  href={`mailto:${candidate.email}`}
                  className="hover:underline"
                >
                  {candidate.email}
                </a>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Phone className="w-4 h-4 text-muted-foreground" />
                <a href={`tel:${candidate.phone}`} className="hover:underline">
                  {candidate.phone}
                </a>
              </div>
              {candidate.linkedin_url && (
                <div className="flex items-center gap-2 text-sm">
                  <Linkedin className="w-4 h-4 text-muted-foreground" />
                  <a
                    href={candidate.linkedin_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:underline"
                  >
                    LinkedIn
                  </a>
                </div>
              )}
              {candidate.github_url && (
                <div className="flex items-center gap-2 text-sm">
                  <Github className="w-4 h-4 text-muted-foreground" />
                  <a
                    href={candidate.github_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:underline"
                  >
                    GitHub
                  </a>
                </div>
              )}
              {candidate.portfolio_url && (
                <div className="flex items-center gap-2 text-sm">
                  <Globe className="w-4 h-4 text-muted-foreground" />
                  <a
                    href={candidate.portfolio_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="hover:underline"
                  >
                    Портфолио
                  </a>
                </div>
              )}
            </div>
          </div>

          {/* Основная информация */}
          <div>
            <h3 className="text-lg font-semibold mb-3">
              Информация о кандидате
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex items-center gap-2 text-sm">
                <Briefcase className="w-4 h-4 text-muted-foreground" />
                <span>
                  {candidate.current_position} в{' '}
                  {candidate.current_company || '—'}
                </span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Clock className="w-4 h-4 text-muted-foreground" />
                <span>{candidate.experience_years} опыта</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Calendar className="w-4 h-4 text-muted-foreground" />
                <span>
                  Дата добавления:{' '}
                  {new Date(candidate.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>

          {/* Навыки */}
          {candidate.skills && candidate.skills.length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Навыки</h3>
              <div className="flex flex-wrap gap-2">
                {candidate.skills.map((skill, index) => (
                  <Badge key={index} variant="outline">
                    {skill}
                  </Badge>
                ))}
              </div>
            </div>
          )}

          {/* Резюме */}
          {candidate.resume_text && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Резюме</h3>
              <div className="p-4 bg-muted rounded-lg">
                <p className="text-sm whitespace-pre-wrap">
                  {candidate.resume_text}
                </p>
              </div>
            </div>
          )}

          {/* Заметки */}
          {candidate.notes && (
            <div>
              <h3 className="text-lg font-semibold mb-3">Заметки</h3>
              <p className="text-sm text-muted-foreground">{candidate.notes}</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
