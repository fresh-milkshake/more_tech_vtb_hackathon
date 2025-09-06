import React from 'react';
import { Outlet, Link } from 'react-router-dom';
import VTBLogo from '../../assets/vtb-pulse-logo.svg';
import { Container } from '@/components/shared/container';
import styles from './main-layout.module.scss';
import { cn } from '@/lib/utils';
import { UserDropdown } from '@/components/user-dropdown';

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
                <UserDropdown />
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
