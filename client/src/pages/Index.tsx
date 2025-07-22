import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Loader2, Bot } from 'lucide-react';

const Index = () => {
  const navigate = useNavigate();

  useEffect(() => {
    // Redirect to chat page after a brief moment
    const timer = setTimeout(() => {
      navigate('/chat');
    }, 1000);

    return () => clearTimeout(timer);
  }, [navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-center space-y-6">
        <div className="mx-auto w-20 h-20 bg-gradient-primary rounded-full flex items-center justify-center shadow-glow">
          <Bot className="h-10 w-10 text-white" />
        </div>
        <div>
          <h1 className="text-4xl font-bold mb-4 text-foreground">
            Light AI Framework
          </h1>
          <p className="text-xl text-muted-foreground mb-6">
            Connecting to your AI agent...
          </p>
          <Loader2 className="h-8 w-8 animate-spin text-primary mx-auto" />
        </div>
      </div>
    </div>
  );
};

export default Index;
