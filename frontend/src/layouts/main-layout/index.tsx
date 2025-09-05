import React from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { User, Settings, LogOut } from 'lucide-react';

interface Props {
  className?: string;
  showHeader?: boolean;
  showFooter?: boolean;
  maxWidth?: string;
}

export const Layout: React.FC<Props> = ({
  className = '',
  showHeader = true,
  showFooter = true,
  maxWidth = 'max-w-7xl',
}) => {
  const navigate = useNavigate();

  return (
    <div className={`min-h-screen flex flex-col ${className}`}>
      {showHeader && (
        <header className="border-b bg-background">
          <div
            className={`mx-auto ${maxWidth} flex h-12 md:h-16 items-center justify-between px-4`}
          >
            <div className="text-xl font-bold text-foreground">МойПроект</div>
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
        </header>
      )}

      <main className={`flex-grow mx-auto ${maxWidth} px-4 py-6`}>
        <Outlet />
      </main>

      {showFooter && (
        <footer className="border-t bg-muted py-4">
          <div
            className={`mx-auto ${maxWidth} px-4 text-center text-sm text-muted-foreground`}
          >
            © {new Date().getFullYear()} МойПроект. Все права защищены.
          </div>
        </footer>
      )}
    </div>
  );
};
