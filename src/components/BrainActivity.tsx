import { Brain, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';

interface BrainActivityProps {
  confusionLevel: number;
}

export const BrainActivity = ({ confusionLevel }: BrainActivityProps) => {
  const getActivityLevel = (confusion: number) => {
    if (confusion < 30) return 'low';
    if (confusion < 60) return 'medium';
    if (confusion < 80) return 'high';
    return 'critical';
  };

  const activityLevel = getActivityLevel(confusionLevel);

  const neurons = Array.from({ length: 12 }, (_, i) => ({
    id: i,
    x: Math.random() * 80 + 10,
    y: Math.random() * 80 + 10,
    delay: Math.random() * 2,
  }));

  return (
    <div className="glass-card p-6 rounded-xl h-full">
      <div className="flex items-center gap-3 mb-6">
        <Brain className="w-5 h-5 text-primary animate-neural-pulse" />
        <h3 className="font-semibold">Neural Activity</h3>
      </div>

      {/* Brain Visualization */}
      <div className="relative aspect-square bg-gradient-to-br from-neural-low/20 to-neural-high/20 rounded-xl mb-6 overflow-hidden">
        
        {/* Neural Network Pattern */}
        <div className="absolute inset-0">
          {neurons.map((neuron) => (
            <div
              key={neuron.id}
              className={cn(
                "absolute w-2 h-2 rounded-full animate-neural-pulse",
                activityLevel === 'low' && 'bg-neural-low',
                activityLevel === 'medium' && 'bg-neural-medium',
                activityLevel === 'high' && 'bg-neural-high',
                activityLevel === 'critical' && 'bg-neural-critical'
              )}
              style={{
                left: `${neuron.x}%`,
                top: `${neuron.y}%`,
                animationDelay: `${neuron.delay}s`,
              }}
            />
          ))}
        </div>

        {/* Central Brain Icon */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className={cn(
            "p-4 rounded-full border-2 transition-all duration-500",
            activityLevel === 'low' && 'border-neural-low/50 bg-neural-low/10',
            activityLevel === 'medium' && 'border-neural-medium/50 bg-neural-medium/10',
            activityLevel === 'high' && 'border-neural-high/50 bg-neural-high/10',
            activityLevel === 'critical' && 'border-neural-critical/50 bg-neural-critical/10 animate-neural-pulse'
          )}>
            <Brain className={cn(
              "w-12 h-12 transition-colors duration-500",
              activityLevel === 'low' && 'text-neural-low',
              activityLevel === 'medium' && 'text-neural-medium',
              activityLevel === 'high' && 'text-neural-high',
              activityLevel === 'critical' && 'text-neural-critical'
            )} />
          </div>
        </div>

        {/* Activity Waves */}
        <div className="absolute inset-0">
          {[1, 2, 3].map((wave) => (
            <div
              key={wave}
              className={cn(
                "absolute inset-0 rounded-xl border-2 opacity-20 animate-neural-pulse",
                activityLevel === 'low' && 'border-neural-low',
                activityLevel === 'medium' && 'border-neural-medium',
                activityLevel === 'high' && 'border-neural-high',
                activityLevel === 'critical' && 'border-neural-critical'
              )}
              style={{
                animationDelay: `${wave * 0.5}s`,
                animationDuration: '3s',
              }}
            />
          ))}
        </div>
      </div>

      {/* Activity Status */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Activity Level</span>
          <div className={cn(
            "px-2 py-1 rounded text-xs font-medium capitalize",
            activityLevel === 'low' && 'bg-neural-low/20 text-neural-low',
            activityLevel === 'medium' && 'bg-neural-medium/20 text-neural-medium',
            activityLevel === 'high' && 'bg-neural-high/20 text-neural-high',
            activityLevel === 'critical' && 'bg-neural-critical/20 text-neural-critical'
          )}>
            {activityLevel}
          </div>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Neural Frequency</span>
          <span className="font-mono text-sm">
            {Math.round(8 + confusionLevel * 0.2)} Hz
          </span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Signal Quality</span>
          <div className="flex items-center gap-1">
            <Zap className="w-3 h-3 text-accent" />
            <span className="font-mono text-sm">98%</span>
          </div>
        </div>
      </div>
    </div>
  );
};