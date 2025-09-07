import type { FC } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Button } from '@/components/ui/button';
import { User, Settings, LogOut } from 'lucide-react';
import { useGetCurrentUserInfo } from '@/services/queries/auth';
import { logout } from '@/store/auth-store';

export const UserDropdown: FC = () => {
  const navigate = useNavigate();
  const { data: user, isLoading } = useGetCurrentUserInfo();
  const displayUser = user;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button
          variant="default"
          className="relative text-white  rounded bg-black"
        >
          {displayUser?.full_name || 'Гость'}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent className="w-full max-w-xs" align="end" forceMount>
        <div className="flex items-center justify-start gap-2 p-2">
          <div className="flex flex-col space-y-1 leading-none">
            <p className="font-medium text-sm">
              {isLoading ? 'Загрузка...' : displayUser?.full_name || 'Гость'}
            </p>
            <p className="text-muted-foreground text-xs">
              {isLoading ? '' : displayUser?.email || 'guest@example.com'}
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
        <DropdownMenuItem
          onSelect={() => {
            logout();
            navigate('/auth');
          }}
        >
          <LogOut className="mr-2 h-4 w-4" />
          <span>Выйти</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
};
