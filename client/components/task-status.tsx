import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { analyzeAPI } from '@/lib/api-client';
import { formatDate } from '@/lib/utils';

interface TaskStatusProps {
  taskId: string;
  onComplete?: () => void;
}

export function TaskStatus({ taskId, onComplete }: TaskStatusProps) {
  const [status, setStatus] = useState<{
    status: 'pending' | 'processing' | 'completed' | 'failed';
    message: string;
    estimated_completion_time?: string;
  } | null>(null);

  useEffect(() => {
    let intervalId: ReturnType<typeof setInterval>;

    const checkStatus = async () => {
      try {
        const response = await analyzeAPI.getTaskStatus(taskId);
        setStatus(response);

        if (response.status === 'completed' || response.status === 'failed') {
          clearInterval(intervalId);
          if (response.status === 'completed' && onComplete) {
            onComplete();
          }
        }
      } catch (error) {
        console.error('Failed to fetch task status:', error);
      }
    };

    // Check immediately and then every 5 seconds
    checkStatus();
    intervalId = setInterval(checkStatus, 5000);

    return () => {
      clearInterval(intervalId);
    };
  }, [taskId, onComplete]);

  if (!status) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Analysis Status</CardTitle>
        <CardDescription>Task ID: {taskId}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center gap-4">
          <div className="flex-1">
            <p className="text-sm font-medium text-muted-foreground">Status</p>
            <p className="mt-1 text-lg font-semibold capitalize">{status.status}</p>
          </div>
          {status.estimated_completion_time && (
            <div className="flex-1">
              <p className="text-sm font-medium text-muted-foreground">
                Estimated Completion
              </p>
              <p className="mt-1 text-lg font-semibold">
                {formatDate(status.estimated_completion_time)}
              </p>
            </div>
          )}
        </div>
        {status.message && (
          <p className="text-sm text-muted-foreground">{status.message}</p>
        )}
      </CardContent>
    </Card>
  );
}