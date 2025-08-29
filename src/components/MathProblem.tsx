import { useState } from 'react';
import { Calculator, CheckCircle, XCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

const problems = [
  {
    id: 1,
    question: "Solve for x: 3x² + 12x - 15 = 0",
    answer: "x = 1 or x = -5",
    hint: "Try using the quadratic formula: x = (-b ± √(b²-4ac)) / 2a"
  },
  {
    id: 2,
    question: "Find the derivative of f(x) = 2x³ - 6x² + 4x - 1",
    answer: "f'(x) = 6x² - 12x + 4",
    hint: "Use the power rule: d/dx[xⁿ] = nxⁿ⁻¹"
  },
  {
    id: 3,
    question: "Evaluate: lim(x→∞) (3x² + 2x + 1)/(x² - x + 2)",
    answer: "3",
    hint: "Divide numerator and denominator by the highest power of x"
  }
];

export const MathProblem = () => {
  const [currentProblem, setCurrentProblem] = useState(0);
  const [answer, setAnswer] = useState('');
  const [showResult, setShowResult] = useState<'correct' | 'incorrect' | null>(null);

  const problem = problems[currentProblem];

  const checkAnswer = () => {
    const isCorrect = answer.toLowerCase().includes(problem.answer.toLowerCase().replace(/\s/g, ''));
    setShowResult(isCorrect ? 'correct' : 'incorrect');
    
    if (isCorrect) {
      setTimeout(() => {
        nextProblem();
      }, 2000);
    }
  };

  const nextProblem = () => {
    setCurrentProblem((prev) => (prev + 1) % problems.length);
    setAnswer('');
    setShowResult(null);
  };

  return (
    <div className="glass-card p-6 rounded-xl h-full">
      <div className="flex items-center gap-3 mb-6">
        <Calculator className="w-5 h-5 text-primary" />
        <h3 className="font-semibold">Current Problem</h3>
      </div>

      <div className="space-y-6">
        {/* Problem Statement */}
        <div className="p-4 bg-muted/20 rounded-lg">
          <p className="text-lg font-medium mb-2">Problem {problem.id}:</p>
          <p className="text-foreground">{problem.question}</p>
        </div>

        {/* Answer Input */}
        <div className="space-y-3">
          <label className="text-sm font-medium text-muted-foreground">
            Your Answer:
          </label>
          <div className="flex gap-2">
            <Input
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Enter your solution..."
              className="flex-1"
              disabled={showResult === 'correct'}
            />
            <Button 
              onClick={checkAnswer}
              disabled={!answer.trim() || showResult === 'correct'}
              variant="default"
            >
              Check
            </Button>
          </div>
        </div>

        {/* Result Display */}
        {showResult && (
          <div className={`flex items-center gap-2 p-3 rounded-lg ${
            showResult === 'correct' 
              ? 'bg-success/20 text-success border border-success/30' 
              : 'bg-destructive/20 text-destructive border border-destructive/30'
          }`}>
            {showResult === 'correct' ? (
              <>
                <CheckCircle className="w-5 h-5" />
                <span className="font-medium">Correct! Well done.</span>
              </>
            ) : (
              <>
                <XCircle className="w-5 h-5" />
                <span className="font-medium">Not quite right. Try again!</span>
              </>
            )}
          </div>
        )}

        {/* Hint Section */}
        <div className="p-4 bg-accent/10 border border-accent/20 rounded-lg">
          <p className="text-sm font-medium text-accent mb-1">Hint:</p>
          <p className="text-sm text-muted-foreground">{problem.hint}</p>
        </div>

        {/* Progress */}
        <div className="flex justify-between items-center text-sm text-muted-foreground">
          <span>Problem {currentProblem + 1} of {problems.length}</span>
          <Button 
            variant="outline" 
            size="sm" 
            onClick={nextProblem}
          >
            Next Problem
          </Button>
        </div>
      </div>
    </div>
  );
};