import { useState } from 'react';
import { MessageCircle, Send, X, Bot } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { cn } from '@/lib/utils';

interface Message {
  id: number;
  text: string;
  isBot: boolean;
  timestamp: Date;
}

interface ChatBotProps {
  /**
   * When true, the chatbot renders as an inline panel instead of a floating widget.
   */
  inline?: boolean;
}

export const ChatBot = ({ inline = false }: ChatBotProps) => {
  const [isOpen, setIsOpen] = useState(inline);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 1,
      text: "Hi! I'm your AI learning assistant. I can help explain concepts without giving away solutions. What would you like to know?",
      isBot: true,
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');

  const sendMessage = () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: messages.length + 1,
      text: input,
      isBot: false,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');

    // Simulate bot response
    setTimeout(() => {
      const botResponse: Message = {
        id: messages.length + 2,
        text: getBotResponse(input),
        isBot: true,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, botResponse]);
    }, 1000);
  };

  const getBotResponse = (userInput: string) => {
    const input = userInput.toLowerCase();

    if (input.includes('quadratic') || input.includes('formula')) {
      return "The quadratic formula is a powerful tool! Remember, it's x = (-b ± √(b²-4ac)) / 2a. Try identifying your a, b, and c values first. What part are you finding challenging?";
    }

    if (input.includes('derivative') || input.includes('differentiate')) {
      return 'For derivatives, start with the power rule: bring down the exponent and reduce it by 1. For example, x³ becomes 3x². What function are you trying to differentiate?';
    }

    if (input.includes('limit') || input.includes('infinity')) {
      return "When dealing with limits at infinity, focus on the highest power terms in both numerator and denominator. They often determine the behavior. What's your specific limit problem?";
    }

    if (input.includes('confused') || input.includes('stuck')) {
      return "I can see your confusion levels are elevated. Let's break this down step by step. What specific part of the problem is causing difficulty? I can guide you through the process.";
    }

    return "I'm here to help guide your thinking! Can you tell me more about what specific concept or step you're working on? I'll provide hints without giving away the solution.";
  };

  const chatContent = (
    <>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border/50">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center">
            <Bot className="w-4 h-4 text-primary" />
          </div>
          <div>
            <h4 className="font-medium">AI Assistant</h4>
            <p className="text-xs text-muted-foreground">Online</p>
          </div>
        </div>
        {!inline && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsOpen(false)}
          >
            <X className="w-4 h-4" />
          </Button>
        )}
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.map(message => (
          <div
            key={message.id}
            className={cn(
              'flex',
              message.isBot ? 'justify-start' : 'justify-end'
            )}
          >
            <div
              className={cn(
                'max-w-[80%] p-3 rounded-lg text-sm',
                message.isBot
                  ? 'bg-muted/50 text-foreground'
                  : 'bg-primary text-primary-foreground'
              )}
            >
              {message.text}
            </div>
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-border/50">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask for help..."
            onKeyPress={e => e.key === 'Enter' && sendMessage()}
            className="flex-1"
          />
          <Button onClick={sendMessage} size="sm">
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </>
  );

  if (inline) {
    return (
      <div className="glass-card rounded-xl border border-border/50 flex flex-col h-full">
        {chatContent}
      </div>
    );
  }

  if (!isOpen) {
    return (
      <Button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 w-14 h-14 rounded-full glow-primary neural-pulse"
        size="lg"
      >
        <MessageCircle className="w-6 h-6" />
      </Button>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 w-80 h-96 glass-card rounded-xl border border-border/50 flex flex-col">
      {chatContent}
    </div>
  );
};
