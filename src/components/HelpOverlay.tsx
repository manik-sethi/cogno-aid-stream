import { X, Lightbulb, Brain } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface HelpOverlayProps {
  onClose: () => void;
}

export const HelpOverlay = ({ onClose }: HelpOverlayProps) => {
  return (
    <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="glass-card p-6 rounded-xl max-w-md w-full mx-4 border border-warning/30 glow-accent">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-warning/20 flex items-center justify-center animate-neural-pulse">
              <Brain className="w-5 h-5 text-warning" />
            </div>
            <div>
              <h3 className="font-semibold text-warning">Confusion Detected</h3>
              <p className="text-sm text-muted-foreground">AI assistance activated</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onClose}>
            <X className="w-4 h-4" />
          </Button>
        </div>

        {/* Screenshot Analysis */}
        <div className="mb-4 p-4 bg-muted/20 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Lightbulb className="w-4 h-4 text-accent" />
            <span className="font-medium text-sm">Screen Analysis Complete</span>
          </div>
          <p className="text-sm text-muted-foreground">
            I can see you're working on a quadratic equation. Here are some hints to help you progress:
          </p>
        </div>

        {/* Helpful Suggestions */}
        <div className="space-y-3 mb-6">
          <div className="p-3 bg-accent/10 border border-accent/20 rounded-lg">
            <h4 className="font-medium text-sm mb-1">💡 Approach Suggestion</h4>
            <p className="text-sm text-muted-foreground">
              Try identifying the coefficients (a, b, c) in your quadratic equation first.
            </p>
          </div>

          <div className="p-3 bg-primary/10 border border-primary/20 rounded-lg">
            <h4 className="font-medium text-sm mb-1">🔍 Focus Area</h4>
            <p className="text-sm text-muted-foreground">
              The discriminant (b² - 4ac) will tell you about the nature of your solutions.
            </p>
          </div>

          <div className="p-3 bg-success/10 border border-success/20 rounded-lg">
            <h4 className="font-medium text-sm mb-1">✨ Next Step</h4>
            <p className="text-sm text-muted-foreground">
              Once you have a, b, c identified, substitute them into the quadratic formula.
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <Button onClick={onClose} className="flex-1">
            Got it, thanks!
          </Button>
          <Button variant="outline" onClick={onClose}>
            More Help
          </Button>
        </div>
      </div>
    </div>
  );
};