import React from 'react';
import { Link } from 'react-router-dom';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Calendar,
  Clock,
  User,
  Hash,
  Brain,
  Target,
  CheckCircle,
  AlertCircle,
  XCircle,
} from 'lucide-react';
import type { IInterview } from '@/services/api/interviews/interviews.types';

export const InterviewCard: React.FC<{ interview: IInterview }> = ({
  interview,
}) => {
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
      case 'draft':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'scheduled':
        return <Calendar className="w-3 h-3" />;
      case 'in_progress':
        return <AlertCircle className="w-3 h-3" />;
      case 'completed':
        return <CheckCircle className="w-3 h-3" />;
      case 'cancelled':
        return <XCircle className="w-3 h-3" />;
      case 'draft':
        return <Target className="w-3 h-3" />;
      default:
        return <Target className="w-3 h-3" />;
    }
  };

  const getInterviewTypeLabel = (type: string) => {
    switch (type) {
      case 'technical':
        return 'Техническое';
      case 'behavioral':
        return 'Поведенческое';
      case 'hr':
        return 'HR';
      default:
        return type;
    }
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.round(seconds / 60);
    if (minutes >= 60) {
      const hours = Math.floor(minutes / 60);
      const remainingMinutes = minutes % 60;
      return `${hours}ч ${remainingMinutes}м`;
    }
    return `${minutes} мин`;
  };

  return (
    <Link to={`/interviews/${interview.id}`} className="h-full block">
      <Card className="hover:shadow-md transition-shadow duration-200 h-full flex flex-col">
        <CardHeader className="pb-3">
          <div className="flex justify-between items-start gap-2">
            <div className="flex-1 min-w-0">
              <CardTitle className="text-lg truncate">
                {interview.position}
              </CardTitle>
              <CardDescription className="flex items-center gap-1 mt-1 text-xs">
                <User className="w-3 h-3 flex-shrink-0" />
                <span className="truncate">
                  Кандидат: {interview.candidate_id?.slice(0, 8)}
                </span>
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent className="flex-1 flex flex-col justify-between">
          <div className="space-y-2 text-sm text-muted-foreground">
            <div className="flex items-center gap-2">
              <Calendar className="w-4 h-4 flex-shrink-0" />
              <span className="text-xs">
                {new Date(interview.scheduled_at).toLocaleDateString('ru-RU', {
                  day: '2-digit',
                  month: '2-digit',
                  year: '2-digit',
                })}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 flex-shrink-0" />
              <span className="text-xs">
                {formatDuration(interview.estimated_duration)}
              </span>
            </div>

            <div className="flex items-center gap-2">
              <Hash className="w-4 h-4 flex-shrink-0" />
              <span className="text-xs truncate">
                ID: {interview.id?.slice(0, 8)}
              </span>
            </div>
          </div>

          <div className="mt-3 space-y-2">
            <div className="flex flex-wrap gap-1">
              <Badge
                variant="outline"
                className="text-xs flex items-center gap-1 h-5"
              >
                <Brain className="w-3 h-3" />
                {getInterviewTypeLabel(interview.interview_type)}
              </Badge>

              <Badge
                variant="outline"
                className="text-xs flex items-center gap-1 h-5"
              >
                <Target className="w-3 h-3" />
                {interview.current_state}
              </Badge>
            </div>

            {interview.interviewer_id && (
              <div className="flex flex-wrap gap-1">
                <Badge variant="outline" className="text-xs h-5">
                  Интервьюер: {interview.interviewer_id}
                </Badge>
              </div>
            )}

            <div className="flex flex-wrap gap-1">
              <Badge
                variant={getStatusVariant(interview.status)}
                className="flex items-center gap-1 h-5"
              >
                {getStatusIcon(interview.status)}
                <span className="text-xs">
                  {interview.status === 'scheduled' && 'Запланировано'}
                  {interview.status === 'in_progress' && 'В процессе'}
                  {interview.status === 'completed' && 'Завершено'}
                  {interview.status === 'cancelled' && 'Отменено'}
                </span>
              </Badge>

              {interview.total_score > 0 && (
                <Badge variant="secondary" className="text-xs h-5">
                  Оценка: {interview.total_score.toFixed(1)}
                </Badge>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </Link>
  );
};
