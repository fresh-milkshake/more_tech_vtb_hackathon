import React, { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';
import type { ICandidate } from '@/services/api/candidates/candidates.types';
import { Link } from 'react-router-dom';
import { Linkedin, Github, Globe, ChevronUp, ChevronDown } from 'lucide-react';

interface CandidatesListProps {
  candidates: ICandidate[];
  isLoading: boolean;
}

type SortDirection = 'asc' | 'desc' | null;

type SortConfig = {
  key: keyof ICandidate;
  direction: SortDirection;
} | null;

const gradeOrder: Record<string, number> = {
  Intern: 0,
  Junior: 1,
  Middle: 2,
  Senior: 3,
  Lead: 4,
  'Tech Lead': 5,
};

export const CandidatesList: React.FC<CandidatesListProps> = ({
  candidates,
  isLoading,
}) => {
  const [sortConfig, setSortConfig] = useState<SortConfig>(null);

  const extractNumber = (str: string | number) => {
    if (typeof str === 'number') return str;
    const match = str.match(/\d+/);
    return match ? parseInt(match[0], 10) : 0;
  };

  const sortedCandidates = React.useMemo(() => {
    if (!sortConfig || !sortConfig.direction) return candidates;

    return [...candidates].sort((a, b) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      let aVal: any = a[sortConfig.key];
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      let bVal: any = b[sortConfig.key];

      // Опыт
      if (sortConfig.key === 'experience_years') {
        aVal = extractNumber(aVal);
        bVal = extractNumber(bVal);
      }

      // Грейд
      if (sortConfig.key === 'applied_position') {
        aVal = gradeOrder[aVal] ?? 0;
        bVal = gradeOrder[bVal] ?? 0;
      }

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal;
      }

      return sortConfig.direction === 'asc'
        ? String(aVal).localeCompare(String(bVal))
        : String(bVal).localeCompare(String(aVal));
    });
  }, [candidates, sortConfig]);

  const handleSort = (key: keyof ICandidate) => {
    setSortConfig((prev) => {
      if (!prev || prev.key !== key) return { key, direction: 'asc' };
      if (prev.direction === 'asc') return { key, direction: 'desc' };
      return { key, direction: null }; // сброс сортировки
    });
  };

  const renderSortIcon = (key: keyof ICandidate) => {
    if (!sortConfig || sortConfig.key !== key || !sortConfig.direction)
      return null;
    return sortConfig.direction === 'asc' ? (
      <ChevronUp className="inline ml-1" size={14} />
    ) : (
      <ChevronDown className="inline ml-1" size={14} />
    );
  };

  if (isLoading) {
    return (
      <Table>
        <TableHeader>
          <TableRow>
            {['Имя', 'Должность', 'Опыт', 'Навыки', 'Email'].map((head) => (
              <TableHead key={head}>{head}</TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {[...Array(5)].map((_, index) => (
            <TableRow key={index}>
              {[...Array(5)].map((_, i) => (
                <TableCell key={i}>
                  <Skeleton className="h-4 w-32" />
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    );
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead
            className="cursor-pointer"
            onClick={() => handleSort('first_name')}
          >
            Имя {renderSortIcon('first_name')}
          </TableHead>
          <TableHead
            className="cursor-pointer"
            onClick={() => handleSort('applied_position')}
          >
            Должность {renderSortIcon('applied_position')}
          </TableHead>
          <TableHead
            className="cursor-pointer"
            onClick={() => handleSort('experience_years')}
          >
            Опыт {renderSortIcon('experience_years')}
          </TableHead>
          <TableHead>Навыки</TableHead>
          <TableHead>Email</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {sortedCandidates.map((candidate) => (
          <TableRow
            key={candidate.id}
            className="hover:bg-gray-100 transition-colors"
          >
            <TableCell>
              <div className="flex items-center gap-2">
                <Link
                  to={`/candidates/${candidate.id}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 font-medium"
                >
                  {candidate.first_name} {candidate.last_name}
                </Link>
                {candidate.linkedin_url && (
                  <a
                    href={candidate.linkedin_url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <Linkedin size={16} />
                  </a>
                )}
                {candidate.github_url && (
                  <a
                    href={candidate.github_url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <Github size={16} />
                  </a>
                )}
                {candidate.portfolio_url && (
                  <a
                    href={candidate.portfolio_url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <Globe size={16} />
                  </a>
                )}
              </div>
            </TableCell>
            <TableCell>{candidate.applied_position}</TableCell>
            <TableCell>{candidate.experience_years}</TableCell>
            <TableCell>{candidate.skills.join(', ')}</TableCell>
            <TableCell>{candidate.email}</TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};
