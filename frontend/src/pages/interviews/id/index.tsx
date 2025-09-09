import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useGetInterviewById } from '@/services/queries/interviews';
import { Loader } from '@/components/common/loader';
import { Breadcrumbs } from '@/components/shared/breadcrumbs';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardHeader,
  CardContent,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Calendar,
  User,
  Clock,
  FileText,
  Hash,
  CalendarClock,
  CheckCircle,
  XCircle,
  AlertCircle,
  StickyNote,
  Brain,
  Target,
  TrendingUp,
} from 'lucide-react';

export const CurrentInterviewPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const { data: interview, isLoading, error } = useGetInterviewById(id!);

  if (isLoading) return <Loader />;

  if (error || !interview) {
    return (
      <div className="text-center py-10">
        <p className="text-red-500">Интервью не найдено или произошла ошибка</p>
        <Link to="/interviews">
          <Button variant="outline" className="mt-4">
            Вернуться к списку интервью
          </Button>
        </Link>
      </div>
    );
  }

  const formatDuration = (seconds: number) => {
    const minutes = Math.round(seconds / 60);
    if (minutes >= 60) {
      const hours = Math.floor(minutes / 60);
      const remainingMinutes = minutes % 60;
      return `${hours} ч ${remainingMinutes} мин`;
    }
    return `${minutes} мин`;
  };

  const getStatusVariant = (
    status: string
  ): 'default' | 'secondary' | 'destructive' | 'outline' | undefined => {
    switch (status) {
      case 'scheduled':
        return 'default';
      case 'in_progress':
        return 'secondary';
      case 'completed':
        return 'default';
      case 'cancelled':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'scheduled':
        return <Calendar className="w-4 h-4" />;
      case 'in_progress':
        return <AlertCircle className="w-4 h-4" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4" />;
      case 'cancelled':
        return <XCircle className="w-4 h-4" />;
      default:
        return <FileText className="w-4 h-4" />;
    }
  };

  return (
    <div className="mt-6 space-y-6">
      <Breadcrumbs extraLabel={`Интервью #${interview.id?.slice(0, 8)}`} />

      <Card>
        <CardHeader>
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div className="flex-1">
              <CardTitle className="text-2xl">{interview.position}</CardTitle>
              <CardDescription className="flex items-center gap-2 mt-2">
                <Brain className="w-4 h-4" />
                Тип интервью:{' '}
                {interview.interview_type === 'technical'
                  ? 'Техническое'
                  : 'Поведенческое'}
              </CardDescription>
            </div>
            <div className="flex flex-wrap gap-2">
              <Badge
                variant={getStatusVariant(interview.status)}
                className="flex items-center gap-1"
              >
                {getStatusIcon(interview.status)}
                {interview.status === 'scheduled' && 'Запланировано'}
                {interview.status === 'in_progress' && 'В процессе'}
                {interview.status === 'completed' && 'Завершено'}
                {interview.status === 'cancelled' && 'Отменено'}
              </Badge>
              <Badge variant="outline" className="flex items-center gap-1">
                <Target className="w-4 h-4" />
                {interview.current_state}
              </Badge>
            </div>
          </div>
        </CardHeader>

        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Hash className="w-4 h-4 text-muted-foreground" />
              <span>
                <span className="font-medium">ID интервью:</span>{' '}
                {interview.id?.slice(0, 8)}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-muted-foreground" />
              <span>
                <span className="font-medium">Кандидат ID:</span>{' '}
                {interview.candidate_id?.slice(0, 8)}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-muted-foreground" />
              <span>
                <span className="font-medium">Интервьюер:</span>{' '}
                {interview.interviewer_id}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 text-muted-foreground" />
              <span>
                <span className="font-medium">Запланировано:</span>{' '}
                {new Date(interview.scheduled_at).toLocaleString('ru-RU', {
                  day: '2-digit',
                  month: '2-digit',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-muted-foreground" />
              <span>
                <span className="font-medium">Длительность:</span>{' '}
                {formatDuration(interview.estimated_duration)}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-muted-foreground" />
              <span>
                <span className="font-medium">Вопросов:</span>{' '}
                {interview.max_questions}
              </span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-muted rounded-lg">
            <div className="flex items-center gap-2">
              <CalendarClock className="w-4 h-4 text-muted-foreground" />
              <div>
                <div className="text-xs text-muted-foreground">Создано</div>
                <div className="text-sm">
                  {new Date(interview.created_at).toLocaleString('ru-RU', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <CalendarClock className="w-4 h-4 text-muted-foreground" />
              <div>
                <div className="text-xs text-muted-foreground">Обновлено</div>
                <div className="text-sm">
                  {new Date(interview.updated_at).toLocaleString('ru-RU', {
                    day: '2-digit',
                    month: '2-digit',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </div>
              </div>
            </div>

            {interview.started_at && (
              <div className="flex items-center gap-2">
                <CalendarClock className="w-4 h-4 text-muted-foreground" />
                <div>
                  <div className="text-xs text-muted-foreground">Начало</div>
                  <div className="text-sm">
                    {new Date(interview.started_at).toLocaleString('ru-RU', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                    })}
                  </div>
                </div>
              </div>
            )}
          </div>

          {(interview.total_score > 0 || interview.recommendation) && (
            <Card className="border-primary/20">
              <CardHeader className="pb-3">
                <CardTitle className="text-lg flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  Результаты оценки
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                {interview.total_score > 0 && (
                  <div className="flex items-center gap-2">
                    <div className="font-medium">Общий балл:</div>
                    <Badge variant="secondary" className="text-lg">
                      {interview.total_score.toFixed(1)}
                    </Badge>
                  </div>
                )}

                {interview.recommendation && (
                  <div>
                    <div className="font-medium mb-1 flex items-center gap-2">
                      <Target className="w-4 h-4" />
                      Рекомендация:
                    </div>
                    <p className="text-sm bg-background p-3 rounded border">
                      {interview.recommendation}
                    </p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {(interview.overall_feedback || interview.notes) && (
            <div className="space-y-4">
              {interview.overall_feedback && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <FileText className="w-5 h-5" />
                    Общий отзыв
                  </h3>
                  <div className="text-sm bg-background p-4 rounded border">
                    {interview.overall_feedback}
                  </div>
                </div>
              )}

              {interview.notes && (
                <div>
                  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                    <StickyNote className="w-5 h-5" />
                    Заметки
                  </h3>
                  <div className="text-sm bg-background p-4 rounded border whitespace-pre-wrap">
                    {interview.notes}
                  </div>
                </div>
              )}
            </div>
          )}

          {Object.keys(interview.extra_data || {}).length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-2">
                Дополнительная информация
              </h3>
              <div className="text-sm bg-background p-4 rounded border">
                <pre className="whitespace-pre-wrap text-xs">
                  {JSON.stringify(interview.extra_data, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {Object.keys(interview.interview_plan || {}).length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-2">План интервью</h3>
              <div className="text-sm bg-background p-4 rounded border">
                <pre className="whitespace-pre-wrap text-xs">
                  {JSON.stringify(interview.interview_plan, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {Object.keys(interview.context || {}).length > 0 && (
            <div>
              <h3 className="text-lg font-semibold mb-2">Контекст</h3>
              <div className="text-sm bg-background p-4 rounded border">
                <pre className="whitespace-pre-wrap text-xs">
                  {JSON.stringify(interview.context, null, 2)}
                </pre>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
