import React, { useState } from 'react';
import { RefreshCw, Trash2, Zap } from 'lucide-react';
import { api } from '../api/client';
import toast from 'react-hot-toast';

export default function TopicCard({ topic, onDelete, onRefresh }) {
  const [loading, setLoading] = useState(false);

  const handleRefresh = async () => {
    setLoading(true);
    try {
      await api.refreshTopic(topic.id);
      toast.success(`Refreshing data for "${topic.name}"`);
      onRefresh?.();
    } catch {
      toast.error('Failed to refresh');
    }
    setLoading(false);
  };

  const handleAnalyze = async () => {
    try {
      await api.analyzeTopic(topic.id);
      toast.success(`AI analysis started for "${topic.name}"`);
    } catch {
      toast.error('Failed to start analysis');
    }
  };

  const handleDelete = async () => {
    if (!window.confirm(`Delete topic "${topic.name}"?`)) return;
    try {
      await api.deleteTopic(topic.id);
      toast.success('Topic deleted');
      onDelete?.(topic.id);
    } catch {
      toast.error('Failed to delete');
    }
  };

  return (
    <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <h3 style={{ fontWeight: 700, fontSize: '1rem', marginBottom: '0.25rem' }}>{topic.name}</h3>
          <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
            {(topic.keywords || []).slice(0, 4).map((kw, i) => (
              <span key={i} style={{
                fontSize: '0.7rem', fontFamily: 'var(--font-mono)',
                background: 'rgba(108,99,255,0.12)', color: 'var(--accent)',
                padding: '0.15rem 0.5rem', borderRadius: 20
              }}>{kw}</span>
            ))}
          </div>
        </div>
        <span style={{
          width: 8, height: 8, borderRadius: '50%', marginTop: 6,
          background: topic.is_active ? 'var(--positive)' : 'var(--text-secondary)',
          boxShadow: topic.is_active ? '0 0 8px var(--positive)' : 'none',
          flexShrink: 0,
        }} />
      </div>

      <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
        Created {new Date(topic.created_at).toLocaleDateString()}
      </div>

      <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
        <button className="btn btn-ghost btn-sm" onClick={handleRefresh} disabled={loading}>
          <RefreshCw size={12} /> {loading ? 'Fetching...' : 'Fetch'}
        </button>
        <button className="btn btn-ghost btn-sm" onClick={handleAnalyze}>
          <Zap size={12} /> Analyze
        </button>
        <button className="btn btn-danger btn-sm" onClick={handleDelete}>
          <Trash2 size={12} />
        </button>
      </div>
    </div>
  );
}