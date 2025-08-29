import { useEffect, useState } from 'react';
import { TrendingUp, AlertTriangle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface ConfusionGraphProps {
  confusionLevel: number;
}

export const ConfusionGraph = ({ confusionLevel }: ConfusionGraphProps) => {
  const [history, setHistory] = useState<number[]>([]);

  useEffect(() => {
    setHistory(prev => [...prev.slice(-19), confusionLevel]);
  }, [confusionLevel]);

  const getConfusionColor = (level: number) => {
    if (level < 30) return 'text-success';
    if (level < 60) return 'text-warning';
    return 'text-destructive';
  };

  const getConfusionBg = (level: number) => {
    if (level < 30) return 'bg-success/20';
    if (level < 60) return 'bg-warning/20';
    return 'bg-destructive/20';
  };

  return (
    <div className="glass-card p-6 rounded-xl h-full">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <TrendingUp className="w-5 h-5 text-primary" />
          <h3 className="font-semibold">Confusion Levels</h3>
        </div>
        {confusionLevel > 75 && (
          <div className="flex items-center gap-2 text-destructive animate-neural-pulse">
            <AlertTriangle className="w-4 h-4" />
            <span className="text-sm font-medium">High Confusion</span>
          </div>
        )}
      </div>

      {/* Current Level Display */}
      <div className="mb-6">
        <div className="flex items-baseline gap-2 mb-2">
          <span className={cn("text-3xl font-bold font-mono", getConfusionColor(confusionLevel))}>
            {Math.round(confusionLevel)}%
          </span>
          <span className="text-muted-foreground text-sm">confusion level</span>
        </div>
        
        {/* Progress Bar */}
        <div className="w-full bg-muted/30 rounded-full h-3 overflow-hidden">
          <div 
            className={cn(
              "h-full transition-all duration-300 rounded-full",
              getConfusionBg(confusionLevel)
            )}
            style={{ width: `${confusionLevel}%` }}
          />
        </div>
      </div>

      {/* Real-time Graph */}
      <div className="relative h-32 mb-4">
        <div className="absolute inset-0 flex items-end justify-between gap-1">
          {history.map((level, index) => (
            <div
              key={index}
              className={cn(
                "flex-1 rounded-t transition-all duration-300",
                level < 30 ? 'bg-success/60' :
                level < 60 ? 'bg-warning/60' : 'bg-destructive/60'
              )}
              style={{ height: `${level}%` }}
            />
          ))}
        </div>
        
        {/* Grid lines */}
        <div className="absolute inset-0 pointer-events-none">
          {[25, 50, 75].map(line => (
            <div
              key={line}
              className="absolute left-0 right-0 border-t border-border/30"
              style={{ bottom: `${line}%` }}
            />
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="flex justify-between text-xs text-muted-foreground">
        <span>Low</span>
        <span>Moderate</span>
        <span>High</span>
      </div>
    </div>
  );
};