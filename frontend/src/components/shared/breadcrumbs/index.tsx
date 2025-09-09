import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Breadcrumb,
  BreadcrumbList,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbSeparator,
} from '@/components/ui/breadcrumb';

const PATH_LABELS: Record<string, string> = {
  '/': 'Главная',
  '/vacancies': 'Вакансии',
  '/candidates': 'Кандидаты',
  '/interviews': 'Интервью',
};

interface BreadcrumbsProps {
  extraLabel?: string;
  className?: string;
}

export const Breadcrumbs: React.FC<BreadcrumbsProps> = ({
  extraLabel,
  className,
}) => {
  const location = useLocation();
  const pathnames = location.pathname.split('/').filter(Boolean);

  return (
    <Breadcrumb className={className}>
      <BreadcrumbList>
        {/* Главная */}
        <BreadcrumbItem>
          <BreadcrumbLink asChild>
            <Link to="/" className="text-black hover:text-gray-700">
              {PATH_LABELS['/']}
            </Link>
          </BreadcrumbLink>
        </BreadcrumbItem>

        {pathnames.map((segment, index) => {
          const path = '/' + pathnames.slice(0, index + 1).join('/');
          const isLast = index === pathnames.length - 1;
          const label = PATH_LABELS[path] || segment;

          return (
            <React.Fragment key={path}>
              <BreadcrumbSeparator />
              <BreadcrumbItem>
                {isLast && extraLabel ? (
                  <span className="text-black">{extraLabel}</span>
                ) : (
                  <BreadcrumbLink asChild>
                    <Link to={path} className="text-black hover:text-gray-700">
                      {label}
                    </Link>
                  </BreadcrumbLink>
                )}
              </BreadcrumbItem>
            </React.Fragment>
          );
        })}
      </BreadcrumbList>
    </Breadcrumb>
  );
};
