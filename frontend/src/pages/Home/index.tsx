import React from 'react';
import { Button } from '@/components/ui/button';
import { useNavigate } from 'react-router-dom';

interface Props {
  className?: string;
}

export const HomePage: React.FC<Props> = ({ className }) => {
  const navigate = useNavigate();

  return (
    <div
      className={`flex flex-col items-center justify-center p-4 ${className}`}
    >
      <h1 className="text-3xl font-bold mb-4">Добро пожаловать, бро! 🚀</h1>
      <p className="text-lg mb-6">Это твоя главная страница!</p>
      <div className="flex gap-4">
        <Button onClick={() => navigate('/auth')}>Перейти к авторизации</Button>
      </div>
    </div>
  );
};
