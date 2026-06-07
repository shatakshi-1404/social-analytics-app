import React, { useEffect, useState, useCallback } from 'react';
import { TrendingUp, MessageCircle, Video, FileText, RefreshCw } from 'lucide-react';
import { api } from '../api/client';
import SentimentChart from '../components/SentimentChart';
import TrendChart from '../components/TrendChart';
import AlertsPanel from '../components/AlertsPanel';
import toast from 'react-hot-toast';

const SentimentBadge = ({ sentiment }) => (
  <span className={`badge badge-${sentiment || 'neutral'}`}>{sentiment || 'neutral'}</span>
);

export default function Home() {
  const [dashboard, setDashboard] = useState(null);
  const [sentiment, setSentiment] = useState([]);
  const [engagement, setEngagement] = useState([]);
  const [alertEvents, setAlertEvents] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchAll = useCallback(async () => {
    try {
      const [dash, sent, alerts] = await Promise.all([
        api.getDashboard(),
        api.getSentimentChart(7),
        api.getAlertEvents(false),
      ]);
      setDashboard(dash.data);
      setSentiment(sent.data);
      setAlertEvents(alerts.data.results || alerts.data || []);

      if (dash.data?.top_topics?.length > 0) {
        const engRes = await api.getEngagementTrend(dash.data.top_topics[0].id, 14);
        setEngagement(engRes.data.results || engRes.data || []);
      }
    } catch (err) {
      toast.error('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAll(); }, [fetchAll]);

  if (loading) return <div className="loading-spinner">Loading dashboard...</div>;

  const stats = [
    { label: 'Active Topics', value: dashboard?.total_topics || 0, icon: TrendingUp },
    { label: 'Tweets Tracked', value: (dashboard?.total_tweets || 0).toLocaleString(), icon: MessageCircle },
    { label: 'Videos Tracked', value: (dashboard?.total_videos || 0).toLocaleString(), icon: Video },
    { label: 'AI Summaries', value: dashboard?.total_summaries || 0, icon: FileText },
  ];

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p>Real-time social media intelligence powered by AI</p>
        </div>
        <button className="btn btn-ghost btn-sm" onClick={fetchAll}>
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      {/* Stats */}
      <div className="stats-grid">
        {stats.map(({ label, value, icon: Icon }) => (
          <div key={label} className="stat-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <span className="label">{label}</span>
              <Icon size={16} color="var(--accent)" />
            </div>
            <span className="value">{value}</span>
          </div>
        ))}
      </div>

      {/* Charts */}
      <div className="grid-2" style={{ marginBottom: '1.5rem' }}>
        <div className="card">
          <div className="section-title">📊 Sentiment Distribution (7d)</div>
          <SentimentChart data={sentiment} />
        </div>
        <div className="card">
          <div className="section-title">📈 Engagement Trend (14d)</div>
          <TrendChart data={engagement} />
        </div>
      </div>

      {/* Recent Summaries + Alerts */}
      <div className="grid-2">
        <div className="card">
          <div className="section-title">
  <span className="section-title-dot" style={{ background: 'var(--pink)' }} />
  Latest AI Summaries
</div>
          {!dashboard?.recent_summaries?.length ? (
            <div className="empty-state">No summaries yet — add a topic and fetch data</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxHeight: 400, overflowY: 'auto' }}>
              {dashboard.recent_summaries.map(s => (
                <div key={s.id} style={{
                  padding: '1rem', background: 'var(--bg-secondary)',
                  borderRadius: 8, border: '1px solid var(--border)'
                }}>
                  <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '0.5rem', flexWrap: 'wrap' }}>
                    <span style={{ fontWeight: 700, fontSize: '0.875rem' }}>{s.topic_name}</span>
                    <span className={`badge badge-${s.platform}`}>{s.platform}</span>
                    <SentimentBadge sentiment={s.sentiment} />
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.6, marginBottom: '0.5rem' }}>
                    {s.summary_text}
                  </p>
                  <div style={{ display: 'flex', gap: '0.4rem', flexWrap: 'wrap' }}>
                    {(s.trending_keywords || []).slice(0, 5).map((kw, i) => (
                      <span key={i} style={{
                        fontSize: '0.7rem', fontFamily: 'var(--font-mono)',
                        background: 'rgba(108,99,255,0.1)', color: 'var(--accent)',
                        padding: '0.1rem 0.4rem', borderRadius: 4
                      }}>#{kw}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <AlertsPanel events={alertEvents.slice(0, 8)} onRefresh={fetchAll} />
      </div>
    </div>
  );
}