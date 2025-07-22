import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { 
  Bot, 
  Brain, 
  Database, 
  MessageSquare, 
  Settings, 
  BookOpen,
  Loader2,
  AlertCircle
} from 'lucide-react';
import { getBeingDetails, Being } from '@/lib/api';

const AgentDetails = () => {
  const [being, setBeing] = useState<Being | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchBeingDetails = async () => {
      try {
        const data = await getBeingDetails();
        setBeing(data);
      } catch (err) {
        setError('Failed to fetch agent details');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchBeingDetails();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="text-center">
          <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto mb-4" />
          <p className="text-muted-foreground">Loading agent details...</p>
        </div>
      </div>
    );
  }

  if (error || !being) {
    return (
      <div className="flex items-center justify-center h-screen bg-background">
        <div className="text-center">
          <AlertCircle className="h-12 w-12 text-destructive mx-auto mb-4" />
          <p className="text-destructive">{error || 'Failed to load agent details'}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="mx-auto w-20 h-20 bg-gradient-primary rounded-full flex items-center justify-center shadow-glow">
            <Bot className="h-10 w-10 text-white" />
          </div>
          <div>
            <h1 className="text-4xl font-bold text-foreground mb-2">
              {being.name}
            </h1>
            <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
              {being.bio}
            </p>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Basic Information */}
          <Card className="bg-gradient-card border-border shadow-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Settings className="h-5 w-5 text-primary" />
                Basic Information
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold text-foreground mb-2">Model Provider</h3>
                <Badge variant="secondary" className="bg-primary text-primary-foreground">
                  {being.modelProvider}
                </Badge>
              </div>
              
              <div>
                <h3 className="font-semibold text-foreground mb-2">Context ID</h3>
                <code className="text-sm bg-muted text-muted-foreground px-2 py-1 rounded">
                  {being.contextId}
                </code>
              </div>
              
              <div>
                <h3 className="font-semibold text-foreground mb-2">Knowledge Base</h3>
                <div className="flex items-center gap-2">
                  <Database className="h-4 w-4 text-agent-primary" />
                  <span className="text-sm text-muted-foreground">
                    {being.knowledge.length} documents
                  </span>
                </div>
              </div>
              
              <div>
                <h3 className="font-semibold text-foreground mb-2">Example Responses</h3>
                <div className="flex items-center gap-2">
                  <MessageSquare className="h-4 w-4 text-agent-secondary" />
                  <span className="text-sm text-muted-foreground">
                    {being.exampleResponses.length} examples
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Personality */}
          <Card className="bg-gradient-card border-border shadow-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-primary" />
                Personality
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-foreground leading-relaxed">
                {being.personality}
              </p>
            </CardContent>
          </Card>

          {/* System Prompt */}
          <Card className="lg:col-span-2 bg-gradient-card border-border shadow-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-5 w-5 text-primary" />
                System Prompt
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-48 w-full">
                <pre className="text-sm text-foreground whitespace-pre-wrap font-mono">
                  {being.system}
                </pre>
              </ScrollArea>
            </CardContent>
          </Card>

          {/* Knowledge Base */}
          {being.knowledge.length > 0 && (
            <Card className="bg-gradient-card border-border shadow-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5 text-primary" />
                  Knowledge Base
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-48 w-full">
                  <div className="space-y-2">
                    {being.knowledge.map((doc, index) => (
                      <div key={index} className="text-sm text-muted-foreground">
                        <span className="font-mono">{index + 1}.</span> {doc}
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          )}

          {/* Example Responses */}
          {being.exampleResponses.length > 0 && (
            <Card className="bg-gradient-card border-border shadow-card">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <MessageSquare className="h-5 w-5 text-primary" />
                  Example Responses
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ScrollArea className="h-48 w-full">
                  <div className="space-y-3">
                    {being.exampleResponses.map((response, index) => (
                      <div key={index} className="p-3 bg-muted rounded-lg">
                        <p className="text-sm text-foreground">{response}</p>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default AgentDetails;