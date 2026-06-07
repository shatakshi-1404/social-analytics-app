import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Hash, Bell, Zap } from 'lucide-react';

const links = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/topics', label: 'Topics', icon: Hash },
  { to: '/alerts', label: 'Alerts', icon: Bell },
];

export default function Sidebar() {
  return (
    <aside style={{
      position: 'fixed', top: 'var(--navbar-height)', left: 0, bottom: 0,
      width: 'var(--sidebar-width)',
      background: '#0d1117',
      borderRight: '1px solid var(--border)',
      display: 'flex', flexDirection: 'column',
      zIndex: 90,
      padding: '16px 0',
    }}>
      <div style={{ padding: '0 14px', marginBottom: '10px' }}>
        <span style={{ fontSize: 9, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '1.5px', fontFamily: 'var(--font-body)' }}>
          Navigation
        </span>
      </div>

      {links.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/'}
          style={({ isActive }) => ({
            display: 'flex', alignItems: 'center', gap: '9px',
            padding: '9px 14px',
            textDecoration: 'none',
            fontSize: '13px',
            fontFamily: 'var(--font-body)',
            fontWeight: isActive ? 600 : 400,
            color: isActive ? 'var(--pink)' : 'var(--text-muted)',
            background: isActive ? 'rgba(236,72,153,0.08)' : 'transparent',
            borderRight: isActive ? '2px solid var(--pink)' : '2px solid transparent',
            transition: 'all 0.15s',
          })}
        >
          <Icon size={15} />
          {label}
        </NavLink>
      ))}

      <div style={{ marginTop: 'auto', padding: '14px', borderTop: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Zap size={11} color="var(--yellow)" />
          <span style={{ fontSize: 10, color: 'var(--text-dim)', fontFamily: 'var(--font-body)' }}>
            Powered by Claude AI
          </span>
        </div>
      </div>
    </aside>
  );
}