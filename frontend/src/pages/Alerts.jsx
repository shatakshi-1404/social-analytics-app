import React, { useEffect, useState } from 'react';
import { Plus, X, Bell, Trash2 } from 'lucide-react';
import { api } from '../api/client';
import AlertsPanel from '../components/AlertsPanel';
import toast from 'react-hot-toast';

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [events, setEvents] = useState([]);
  const [topics, setTopics] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', topic: '', alert_type: 'sentiment_drop', threshold: '', email: '' });
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      const [a, e, t] = await Promise.all([
        api.getAlerts(),
        api.getAlertEvents(false),
        api.getTopics(),
      ]);
      setAlerts(a.data.results || a.data);
      setEvents(e.data.results || e.data);
      setTopics(t.data.results || t.data);
    } catch {
      toast.error('Failed to load alerts');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleSubmit = async () => {
    if (!form.name || !form.topic || !form.threshold) {
      return toast.error('Fill in all required fields');
    }
    try {
      await api.createAlert({ ...form, threshold: parseFloat(form.threshold) });
      toast.success('Alert created!');
      setForm({ name: '', topic: '', alert_type: 'sentiment_drop', threshold: '', email: '' });
      setShowForm(false);
      fetchData();
    } catch {
      toast.error('Failed to create alert');
    }
  };

  const handleDelete = async (id) => {
    try {
      await api.deleteAlert(id);
      toast.success('Alert deleted');
      setAlerts(prev => prev.filter(a => a.id !== id));
    } catch {
      toast.error('Failed to delete alert');
    }
  };

  const alertTypeLabels = {
    sentiment_drop: 'Sentiment Drop (score < threshold)',
    engagement_spike: 'Engagement Spike (score > threshold)',
    volume_spike: 'Volume Spike (posts > threshold)',
  };

  if (loading) return <div className="loading-spinner">Loading alerts...</div>;

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Alerts</h1>
          <p>Subscribe to threshold alerts for topics</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? <X size={14} /> : <Plus size={14} />}
          {showForm ? 'Cancel' : 'New Alert'}
        </button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: '1.5rem', maxWidth: 500 }}>
          <div className="section-title">Create Alert</div>
          <div className="form-group">
            <label>Alert Name *</label>
            <input
              placeholder="e.g. AI Sentiment Drop"
              value={form.name}
              onChange={e => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Topic *</label>
            <select value={form.topic} onChange={e => setForm({ ...form, topic: e.target.value })}>
              <option value="">Select a topic</option>
              {topics.map(t => <option key={t.id} value={t.id}>{t.name}</option>)}
            </select>
          </div>
          <div className="form-group">
            <label>Alert Type *</label>
            <select value={form.alert_type} onChange={e => setForm({ ...form, alert_type: e.target.value })}>
              {Object.entries(alertTypeLabels).map(([v, l]) => (
                <option key={v} value={v}>{l}</option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>Threshold *</label>
            <input
              type="number" step="0.1"
              placeholder={form.alert_type === 'sentiment_drop' ? 'e.g. -0.3' : 'e.g. 70'}
              value={form.threshold}
              onChange={e => setForm({ ...form, threshold: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Email (optional)</label>
            <input
              type="email" placeholder="you@example.com"
              value={form.email}
              onChange={e => setForm({ ...form, email: e.target.value })}
            />
          </div>
          <button className="btn btn-primary" onClick={handleSubmit}>Create Alert</button>
        </div>
      )}

      <div className="grid-2">
        <div>
          <div className="section-title" style={{ marginBottom: '1rem' }}>
            <Bell size={16} color="var(--accent)" /> Configured Alerts
          </div>
          {alerts.length === 0 ? (
            <div className="empty-state">No alerts configured yet</div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {alerts.map(alert => (
                <div key={alert.id} className="card" style={{ padding: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '0.9rem', marginBottom: '0.3rem' }}>{alert.name}</div>
                      <div style={{ fontSize: '0.75rem', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                        {alert.topic_name} · {alert.alert_type.replace(/_/g, ' ')} · threshold: {alert.threshold}
                      </div>
                      <div style={{ marginTop: '0.4rem', display: 'flex', gap: '0.4rem' }}>
                        <span className={`badge ${alert.is_active ? 'badge-positive' : 'badge-neutral'}`}>
                          {alert.is_active ? 'Active' : 'Paused'}
                        </span>
                        <span className="badge badge-neutral">{alert.event_count} events</span>
                      </div>
                    </div>
                    <button className="btn btn-danger btn-sm" onClick={() => handleDelete(alert.id)}>
                      <Trash2 size={12} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <AlertsPanel events={events} onRefresh={fetchData} />
      </div>
    </div>
  );
}