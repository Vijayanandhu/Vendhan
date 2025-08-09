import React, { useEffect, useState } from 'react';

export default function NotificationBadge() {
  const [notifications, setNotifications] = useState([]);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    fetch('/api/notifications')
      .then(res => res.json())
      .then(data => setNotifications(data.notifications || []));
    const interval = setInterval(() => {
      fetch('/api/notifications')
        .then(res => res.json())
        .then(data => setNotifications(data.notifications || []));
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const unreadCount = notifications.filter(n => !n.read).length;
  const lastFive = notifications.slice(-5).reverse();

  function markAllRead() {
    fetch('/api/notifications/mark-read', { method: 'POST' })
      .then(() => setNotifications(n => n.map(x => ({ ...x, read: true }))));
  }

  return (
    <div className="relative inline-block">
      <button onClick={() => { setShowDropdown(!showDropdown); if (!showDropdown) markAllRead(); }} className="relative">
        <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>
        {unreadCount > 0 && <span className="absolute -top-1 -right-1 bg-red-600 text-white rounded-full text-xs px-1">{unreadCount}</span>}
      </button>
      {showDropdown && (
        <div className="absolute right-0 mt-2 w-64 bg-white border rounded shadow-lg z-10">
          <div className="p-2 font-bold border-b">Notifications</div>
          {lastFive.length === 0 ? <div className="p-2">No notifications</div> : lastFive.map((n, i) => (
            <div key={i} className="p-2 border-b last:border-b-0 text-sm">
              <div className="font-semibold">{n.title}</div>
              <div>{n.message}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
