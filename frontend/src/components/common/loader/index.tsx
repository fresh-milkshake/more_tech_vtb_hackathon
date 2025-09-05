import { Loader2 } from 'lucide-react';

export const Loader = () => (
  <div className="flex items-center justify-center w-full h-full p-6">
    <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
  </div>
);
