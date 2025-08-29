import React, { useState, useEffect } from 'react';
import { Bell, X, CheckCircle, AlertCircle, Info, Clock } from 'lucide-react';
import { useNotifications } from '@/hooks/useWebSocket';

interface Notification {
  id: number;
  type: string;
  data: any;
  timestamp: Date;
}

const NotificationCenter: React.FC = () => {
  const { notifications, clearNotification, clearAllNotifications } = useNotifications();
  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);

  // Update unread count when notifications change
  useEffect(() => {
    setUnreadCount(notifications.length);
  }, [notifications]);

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'invoice_reminder':
        return <AlertCircle className="w-5 h-5 text-orange-500" />;
      case 'ceremony_reminder':
        return <Clock className="w-5 h-5 text-blue-500" />;
      case 'payment_received':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'new_couple':
        return <Info className="w-5 h-5 text-purple-500" />;
      default:
        return <Info className="w-5 h-5 text-gray-500" />;
    }
  };

  const getNotificationTitle = (type: string) => {
    switch (type) {
      case 'invoice_reminder':
        return 'Invoice Reminder';
      case 'ceremony_reminder':
        return 'Ceremony Reminder';
      case 'payment_received':
        return 'Payment Received';
      case 'new_couple':
        return 'New Couple';
      default:
        return 'Notification';
    }
  };

  const formatTime = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
  };

  const handleNotificationClick = (notification: Notification) => {
    // Handle notification click based on type
    switch (notification.type) {
      case 'invoice_reminder':
        window.location.href = `/invoices/${notification.data.invoice_id}`;
        break;
      case 'ceremony_reminder':
        window.location.href = `/ceremonies/${notification.data.ceremony_id}`;
        break;
      case 'new_couple':
        window.location.href = `/couples/${notification.data.couple_id}`;
        break;
      default:
        break;
    }
    
    clearNotification(notification.id);
  };

  return (
    <div className="relative">
      {/* Notification Bell */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 text-gray-600 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 rounded-lg"
      >
        <Bell className="w-6 h-6" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Notification Panel */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900">Notifications</h3>
            <div className="flex items-center space-x-2">
              {notifications.length > 0 && (
                <button
                  onClick={clearAllNotifications}
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  Clear all
                </button>
              )}
              <button
                onClick={() => setIsOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Notifications List */}
          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 ? (
              <div className="p-4 text-center text-gray-500">
                <Bell className="w-8 h-8 mx-auto mb-2 text-gray-300" />
                <p>No notifications</p>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className="p-4 hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => handleNotificationClick(notification)}
                  >
                    <div className="flex items-start space-x-3">
                      {getNotificationIcon(notification.type)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-gray-900">
                            {getNotificationTitle(notification.type)}
                          </p>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              clearNotification(notification.id);
                            }}
                            className="text-gray-400 hover:text-gray-600"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                        <p className="text-sm text-gray-600 mt-1">
                          {notification.data.message}
                        </p>
                        <p className="text-xs text-gray-400 mt-2">
                          {formatTime(notification.timestamp)}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="p-4 border-t border-gray-200">
              <button
                onClick={() => setIsOpen(false)}
                className="w-full text-sm text-blue-600 hover:text-blue-800 font-medium"
              >
                View all notifications
              </button>
            </div>
          )}
        </div>
      )}

      {/* Backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

export default NotificationCenter;
