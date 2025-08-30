import { useEffect, useRef, useState, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';

interface WebSocketMessage {
  type: string;
  [key: string]: any;
}

interface WebSocketHook {
  isConnected: boolean;
  sendMessage: (message: WebSocketMessage) => void;
  subscribe: (type: string, id: string) => void;
  unsubscribe: (type: string, id: string) => void;
  lastMessage: WebSocketMessage | null;
  error: string | null;
}

export const useWebSocket = (): WebSocketHook => {
  const { user } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [error, setError] = useState<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const handleNotification = useCallback((message: WebSocketMessage) => {
    const { notification_type, data } = message;
    
    // Create browser notification
    if ('Notification' in window && Notification.permission === 'granted') {
      new Notification('Melbourne Celebrant Portal', {
        body: data.message,
        icon: '/favicon.ico',
        tag: notification_type
      });
    }

    // You can also dispatch a custom event for components to listen to
    window.dispatchEvent(new CustomEvent('websocket-notification', {
      detail: { type: notification_type, data }
    }));
  }, []);

  const handleDashboardUpdate = useCallback((message: WebSocketMessage) => {
    // Dispatch event for dashboard components to update
    window.dispatchEvent(new CustomEvent('dashboard-update', {
      detail: message.data
    }));
  }, []);

  const handleCoupleUpdate = useCallback((message: WebSocketMessage) => {
    // Dispatch event for couple components to update
    window.dispatchEvent(new CustomEvent('couple-update', {
      detail: { couple_id: message.couple_id, data: message.data }
    }));
  }, []);

  const handleInvoiceUpdate = useCallback((message: WebSocketMessage) => {
    // Dispatch event for invoice components to update
    window.dispatchEvent(new CustomEvent('invoice-update', {
      detail: { invoice_id: message.invoice_id, data: message.data }
    }));
  }, []);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    switch (message.type) {
      case 'notification':
        handleNotification(message);
        break;
      case 'dashboard_update':
        handleDashboardUpdate(message);
        break;
      case 'couple_update':
        handleCoupleUpdate(message);
        break;
      case 'invoice_update':
        handleInvoiceUpdate(message);
        break;
      case 'pong':
        // Handle pong response
        break;
      case 'subscription_confirmed':
        break;
      case 'unsubscription_confirmed':
        break;
      case 'error':
        console.error('WebSocket error message:', message.message);
        break;
      default:
        // console.log('Unknown message type:', message.type); // Removed console.log
      }
  }, [handleNotification, handleDashboardUpdate, handleCoupleUpdate, handleInvoiceUpdate]);

  const connect = useCallback(() => {
    if (!user) return;

    try {
      // Get token from localStorage or cookies
      const token = localStorage.getItem('token') || '';
      
      const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000'}/api/v1/ws/connect?token=${token}`;
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsConnected(true);
        setError(null);
        // console.log('WebSocket connected'); // Removed console.log

        // Start ping interval
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000); // Ping every 30 seconds
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          setLastMessage(message);

          // Handle different message types
          handleMessage(message);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.onclose = (event) => {
        setIsConnected(false);
        // console.log('WebSocket disconnected:', event.code, event.reason); // Removed console.log

        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }

        // Attempt to reconnect if not a normal closure
        if (event.code !== 1000) {
          reconnectTimeoutRef.current = setTimeout(() => {
            // console.log('Attempting to reconnect...'); // Removed console.log
            connect();
          }, 5000); // Reconnect after 5 seconds
        }
      };

      ws.onerror = (event) => {
        setError('WebSocket connection error');
        console.error('WebSocket error:', event);
      };

      wsRef.current = ws;
    } catch (err) {
      setError('Failed to create WebSocket connection');
      console.error('WebSocket connection error:', err);
    }
  }, [user, handleMessage]);

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close(1000, 'User initiated disconnect');
      wsRef.current = null;
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }

    setIsConnected(false);
  }, []);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }, []);

  const subscribe = useCallback((type: string, id: string) => {
    sendMessage({
      type: 'subscribe',
      subscription_type: type,
      subscription_id: id
    });
  }, [sendMessage]);

  const unsubscribe = useCallback((type: string, id: string) => {
    sendMessage({
      type: 'unsubscribe',
      subscription_type: type,
      subscription_id: id
    });
  }, [sendMessage]);

  // Connect on mount and when user changes
  useEffect(() => {
    if (user) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [user, connect, disconnect]);

  // Request notification permission
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  return {
    isConnected,
    sendMessage,
    subscribe,
    unsubscribe,
    lastMessage,
    error
  };
};

// Hook for listening to WebSocket events
export const useWebSocketEvent = (eventName: string, callback: (data: any) => void) => {
  useEffect(() => {
    const handleEvent = (event: CustomEvent) => {
      callback(event.detail);
    };

    window.addEventListener(eventName, handleEvent as EventListener);

    return () => {
      window.removeEventListener(eventName, handleEvent as EventListener);
    };
  }, [eventName, callback]);
};

// Hook for notifications
export const useNotifications = () => {
  const [notifications, setNotifications] = useState<any[]>([]);

  useWebSocketEvent('websocket-notification', (data) => {
    setNotifications(prev => [...prev, { ...data, id: Date.now(), timestamp: new Date() }]);
  });

  const clearNotification = (id: number) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const clearAllNotifications = () => {
    setNotifications([]);
  };

  return {
    notifications,
    clearNotification,
    clearAllNotifications
  };
};
