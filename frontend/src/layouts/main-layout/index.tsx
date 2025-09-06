// src/layouts/main-layout.tsx
import React from 'react';
import { Outlet, useNavigate, Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { User, Settings, LogOut } from 'lucide-react';
import VTBLogo from '../../assets/vtb-pulse-logo.svg';
import { Container } from '@/components/shared/container';
import styles from './main-layout.module.scss';
import { cn } from '@/lib/utils';

interface Props {
  className?: string;
  showHeader?: boolean;
  showFooter?: boolean;
}

export const Layout: React.FC<Props> = ({
  className = '',
  showHeader = true,
  showFooter = true,
}) => {
  const navigate = useNavigate();

  return (
    <div className={`min-h-screen flex flex-col ${className}`}>
      {showHeader && (
        <header className="border-b bg-background">
          <Container>
            <div className="flex h-12 md:h-16 items-center justify-between">
              <Link
                to="/"
                className={cn(
                  'transition-transform w-[100px] duration-200 hover:fill-primary hover:opacity-90',
                  styles.logoWrapper
                )}
              >
                <img src={VTBLogo} className={styles.logo} alt="VTB Logo" />
              </Link>
              <div className="flex items-center gap-4">
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button
                      variant="ghost"
                      className="relative h-8 w-8 rounded-full"
                    >
                      U
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent
                    className="w-full max-w-xs"
                    align="end"
                    forceMount
                  >
                    <div className="flex items-center justify-start gap-2 p-2">
                      <div className="flex flex-col space-y-1 leading-none">
                        <p className="font-medium text-sm">Гость</p>
                        <p className="text-muted-foreground text-xs">
                          guest@example.com
                        </p>
                      </div>
                    </div>
                    <DropdownMenuItem onSelect={() => navigate('/profile')}>
                      <User className="mr-2 h-4 w-4" />
                      <span>Профиль</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem onSelect={() => navigate('/settings')}>
                      <Settings className="mr-2 h-4 w-4" />
                      <span>Настройки</span>
                    </DropdownMenuItem>
                    <DropdownMenuItem onSelect={() => navigate('/auth')}>
                      <LogOut className="mr-2 h-4 w-4" />
                      <span>Выйти</span>
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </div>
          </Container>
        </header>
      )}

      <main className="flex-grow">
        <Container>
          <div className="py-6">
            <Outlet />
          </div>
        </Container>
      </main>

      {showFooter && (
        <footer className="border-t bg-muted">
          <Container>
            <div className="py-4 text-center text-sm text-muted-foreground">
              © {new Date().getFullYear()} VTB | HR Pulse. Все права защищены.
            </div>
          </Container>
        </footer>
      )}
    </div>
  );
};
