import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import {
  Users,
  Calendar,
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
} from 'lucide-react';

const mockData = {
  totalVacancies: 24,
  activeVacancies: 18,
  interviewsToday: 7,
  interviewsThisWeek: 23,
  nextInterview: {
    candidate: 'Анна Петрова',
    position: 'Senior Frontend Developer',
    time: '14:30',
    date: 'Сегодня',
  },
  interviewStats: {
    completed: 156,
    scheduled: 34,
    cancelled: 8,
  },
  recentActivity: [
    {
      id: 1,
      action: 'Новое собеседование',
      description: 'Иван Иванов для позиции Designer',
      time: '10 минут назад',
    },
    {
      id: 2,
      action: 'Завершено',
      description: 'Собеседование с Мария Сидорова',
      time: '1 час назад',
    },
    {
      id: 3,
      action: 'Новая вакансия',
      description: 'Backend Developer открыта',
      time: '2 часа назад',
    },
  ],
};

export const AnalyticsDashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Аналитика</h1>
        <p className="text-muted-foreground">
          Обзор ключевых метрик HR процессов
        </p>
      </div>

      {/* Основные метрики */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Всего вакансий
            </CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.totalVacancies}</div>
            <p className="text-xs text-muted-foreground">
              {mockData.activeVacancies} активных
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Сегодня</CardTitle>
            <Calendar className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{mockData.interviewsToday}</div>
            <p className="text-xs text-muted-foreground">собеседований</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">На неделе</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {mockData.interviewsThisWeek}
            </div>
            <p className="text-xs text-muted-foreground">запланировано</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Завершено</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {mockData.interviewStats.completed}
            </div>
            <p className="text-xs text-muted-foreground">за всё время</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Clock className="h-5 w-5" />
              Ближайшее собеседование
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="rounded-lg border p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold">
                      {mockData.nextInterview.candidate}
                    </h3>
                    <p className="text-sm text-muted-foreground">
                      {mockData.nextInterview.position}
                    </p>
                  </div>
                  <Badge variant="secondary">
                    {mockData.nextInterview.date}
                  </Badge>
                </div>
                <div className="mt-2 flex items-center gap-2 text-sm">
                  <Clock className="h-4 w-4" />
                  <span>{mockData.nextInterview.time}</span>
                </div>
              </div>
              <div className="flex gap-2">
                <button className="flex-1 rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90">
                  Подготовиться
                </button>
                <button className="flex-1 rounded-md bg-primary px-4 py-2 text-sm text-primary-foreground hover:bg-primary/90">
                  Перенести
                </button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Статистика собеседований */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              Статистика собеседований
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Завершено</span>
                </div>
                <span className="font-semibold">
                  {mockData.interviewStats.completed}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Clock className="h-4 w-4 text-blue-500" />
                  <span>Запланировано</span>
                </div>
                <span className="font-semibold">
                  {mockData.interviewStats.scheduled}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <XCircle className="h-4 w-4 text-red-500" />
                  <span>Отменено</span>
                </div>
                <span className="font-semibold">
                  {mockData.interviewStats.cancelled}
                </span>
              </div>
              <div className="pt-2">
                <div className="relative h-2 w-full overflow-hidden rounded-full bg-muted">
                  <div
                    className="absolute left-0 top-0 h-full bg-green-500"
                    style={{ width: '75%' }}
                  />
                  <div
                    className="absolute left-[75%] top-0 h-full bg-blue-500"
                    style={{ width: '15%' }}
                  />
                  <div
                    className="absolute left-[90%] top-0 h-full bg-red-500"
                    style={{ width: '10%' }}
                  />
                </div>
                <div className="mt-2 flex justify-between text-xs text-muted-foreground">
                  <span>75% завершено</span>
                  <span>15% запланировано</span>
                  <span>10% отменено</span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Последняя активность */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertCircle className="h-5 w-5" />
            Последняя активность
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mockData.recentActivity.map((activity) => (
              <div
                key={activity.id}
                className="flex items-start gap-4 border-b pb-4 last:border-0 last:pb-0"
              >
                <div className="mt-1 h-2 w-2 rounded-full bg-primary"></div>
                <div className="flex-1">
                  <p className="font-medium">{activity.action}</p>
                  <p className="text-sm text-muted-foreground">
                    {activity.description}
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    {activity.time}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
