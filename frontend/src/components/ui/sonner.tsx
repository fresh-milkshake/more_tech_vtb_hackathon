'use client';

import { useTheme } from 'next-themes';
import { Toaster as Sonner, type ToasterProps } from 'sonner';
import { useEffect, useState } from 'react';
import styles from './sonner.module.scss'; // Импортируем CSS-модуль

const Toaster = ({ ...props }: ToasterProps) => {
  const { theme = 'system' } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) return null;

  return (
    <Sonner
      theme={theme as ToasterProps['theme']}
      className="toaster"
      richColors={false} // Отключаем встроенные цветовые стили sonner
      toastOptions={{
        className: styles.customToast, // Используем класс из CSS-модуля
        style: {
          background: 'var(--popover)',
          color: '#000000',
          border: 'var(--border)',
        },
      }}
      {...props}
    />
  );
};

export { Toaster };
