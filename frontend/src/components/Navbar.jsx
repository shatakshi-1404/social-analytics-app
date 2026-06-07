import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Bell, RefreshCw } from 'lucide-react';
import { api } from '../api/client';
import toast from 'react-hot-toast';

export default function Navbar() {
  const [unreadCount, setUnreadCount] = useState(0);
  const [live, setLive] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await api.getAlertEvents(true);
        setUnreadCount(res.data.count || res.data.results?.length || 0);
      } catch {}
    };
    fetch();
    const t = setInterval(fetch, 30000);
    return () => clearInterval(t);
  }, []);

  const handleRefresh = async () => {
    try {
      await api.refreshAll();
      toast.success('Refresh started for all topics');
    } catch {
      toast.error('Failed to start refresh');
    }
  };

  return (
    <nav style={{
      position: 'fixed', top: 0, left: 0, right: 0,
      height: 'var(--navbar-height)',
      background: 'rgba(13,17,23,0.97)',
      backdropFilter: 'blur(10px)',
      borderBottom: '1px solid var(--border)',
      zIndex: 100,
      display: 'flex', alignItems: 'center',
      justifyContent: 'space-between',
      padding: '0 20px',
    }}>
      <Link to="/" style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{
          fontFamily: 'var(--font-head)', fontWeight: 800,
          fontSize: '16px', letterSpacing: '-0.5px', color: '#f9fafb',
        }}>
          Social<span style={{ color: 'var(--pink)' }}>Pulse</span>
        </span>
      </Link>

      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <div style={{
          display: 'flex', alignItems: 'center', gap: '5px',
          padding: '4px 10px', borderRadius: 20,
          background: 'rgba(250,204,21,0.08)',
          border: '1px solid rgba(250,204,21,0.15)',
        }}>
          <span style={{
            width: 5, height: 5, borderRadius: '50%',
            background: 'var(--yellow)',
            boxShadow: '0 0 6px var(--yellow)',
          }} />
          <span style={{ fontSize: 10, color: 'var(--yellow)', fontWeight: 600 }}>LIVE</span>
        </div>

        <button className="btn btn-ghost btn-sm" onClick={handleRefresh}>
          <RefreshCw size={12} /> Refresh
        </button>

        <Link to="/alerts" style={{ position: 'relative', textDecoration: 'none' }}>
          <button className="btn btn-ghost btn-sm">
            <Bell size={13} />
            {unreadCount > 0 && (
              <span style={{
                position: 'absolute', top: -3, right: -3,
                background: 'var(--pink)', color: 'white',
                borderRadius: '50%', width: 14, height: 14,
                fontSize: 9, display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontWeight: 700,
              }}>{unreadCount}</span>
            )}
          </button>
        </Link>
      </div>
    </nav>
  );
}