import { Wifi, WifiOff, Brain } from 'lucide-react';
import { cn } from '@/lib/utils';

interface BCIStatusProps {
  isConnected: boolean;
}

export const BCIStatus = ({ isConnected }: BCIStatusProps) => {
  return (
    <div className="flex items-center gap-4">
      {/* Connection Status */}
      <div className={cn(
        "flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium",
        isConnected 
          ? "bg-success/20 text-success border border-success/30" 
          : "bg-destructive/20 text-destructive border border-destructive/30"
      )}>
        {isConnected ? (
          <>
            <Wifi className="w-4 h-4" />
            <span>Connected</span>
          </>
        ) : (
          <>
            <WifiOff className="w-4 h-4" />
            <span>Disconnected</span>
          </>
        )}
      </div>

      {/* Signal Strength */}
      {isConnected && (
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-primary animate-neural-pulse" />
          <div className="flex gap-1">
            {[1, 2, 3, 4].map((bar) => (
              <div
                key={bar}
                className={cn(
                  "w-1 bg-primary rounded-full transition-all duration-300",
                  bar <= 3 ? "h-2 opacity-100" : "h-1 opacity-30"
                )}
              />
            ))}
          </div>
          <span className="text-xs text-muted-foreground">85%</span>
        </div>
      )}
    </div>
  );
};