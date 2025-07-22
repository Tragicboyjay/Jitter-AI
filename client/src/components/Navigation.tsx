import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { MessageSquare, User, Bot } from 'lucide-react';

const Navigation = () => {
  const location = useLocation();
  
  return (
    <nav className="fixed top-4 left-1/2 transform -translate-x-1/2 z-50">
      <div className="flex items-center gap-2 bg-card/80 backdrop-blur-sm border border-border rounded-full p-2 shadow-card">
        <div className="flex items-center gap-2 px-3">
          <Bot className="h-5 w-5 text-primary" />
          <span className="font-semibold text-foreground">AI Agent</span>
        </div>
        
        <div className="flex items-center gap-1">
          <Button
            variant={location.pathname === '/chat' ? 'default' : 'ghost'}
            size="sm"
            asChild
            className="rounded-full"
          >
            <Link to="/chat" className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Chat
            </Link>
          </Button>
          
          <Button
            variant={location.pathname === '/agent' ? 'default' : 'ghost'}
            size="sm"
            asChild
            className="rounded-full"
          >
            <Link to="/agent" className="flex items-center gap-2">
              <User className="h-4 w-4" />
              Agent
            </Link>
          </Button>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;