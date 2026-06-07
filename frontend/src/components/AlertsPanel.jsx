import React from 'react';
import { Bell, CheckCheck } from 'lucide-react';
import { api } from '../api/client';
import toast from 'react-hot-toast';

export default function AlertsPanel({ events, onRefresh }) {
  const handleMarkAllRead = async () => {
    try {
      await api.markAllRead();
      toast.success('All alerts marked as read');
      onRefresh?.();
    } catch {
      toast.error('Failed to mark as read');
    }
  };

  const unread = events.filter(e => !e.is_read);

  return (
    <div className="card">
      <div className="section-header">
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Bell size={16} color="var(--accent-2)" />
          <h2>Recent Alerts</h2>
          {unread.length > 0 && (
            <span className="badge badge-negative">{unread.length} new</span>
          )}
        </div>
        {unread.length > 0 && (
          <button className="btn btn-ghost btn-sm" onClick={handleMarkAllRead}>
            <CheckCheck size={12} /> Mark all read
          </button>
        )}
      </div>

      {events.length === 0 ? (
        <div className="empty-state">No alerts triggered yet</div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', maxHeight: 320, overflowY: 'auto' }}>
          {events.map(event => (
            <div key={event.id} style={{
              padding: '0.875rem',
              background: event.is_read ? 'transparent' : 'rgba(255,101,132,0.06)',
              border: `1px solid ${event.is_read ? 'var(--border)' : 'rgba(255,101,132,0.3)'}`,
              borderRadius: 8,
            }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                <span style={{ fontWeight: 600, fontSize: '0.85rem' }}>{event.alert_name}</span>
                <span style={{ fontSize: '0.7rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                  {new Date(event.triggered_at).toLocaleString()}
                </span>
              </div>
              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                {event.message}
              </p>
              {!event.is_read && (
                <div style={{ marginTop: '0.4rem' }}>
                  <span className="badge badge-negative">New</span>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}