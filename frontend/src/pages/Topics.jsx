import React, { useEffect, useState } from 'react';
import { Plus, X } from 'lucide-react';
import { api } from '../api/client';
import TopicCard from '../components/TopicCard';
import toast from 'react-hot-toast';

export default function Topics() {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({ name: '', keywords: '' });
  const [submitting, setSubmitting] = useState(false);

  const fetchTopics = async () => {
    try {
      const res = await api.getTopics();
      setTopics(res.data.results || res.data);
    } catch {
      toast.error('Failed to load topics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchTopics(); }, []);

  const handleSubmit = async () => {
    if (!form.name.trim()) return toast.error('Topic name is required');
    setSubmitting(true);
    try {
      const keywords = form.keywords.split(',').map(k => k.trim()).filter(Boolean);
      await api.createTopic({ name: form.name.trim(), keywords, is_active: true });
      toast.success(`Topic "${form.name}" created!`);
      setForm({ name: '', keywords: '' });
      setShowForm(false);
      fetchTopics();
    } catch (err) {
      toast.error(err.response?.data?.name?.[0] || 'Failed to create topic');
    }
    setSubmitting(false);
  };

  return (
    <div>
      <div className="page-header">
        <div>
          <h1>Topics</h1>
          <p>Manage tracked topics and trigger data fetches</p>
        </div>
        <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? <X size={14} /> : <Plus size={14} />}
          {showForm ? 'Cancel' : 'Add Topic'}
        </button>
      </div>

      {showForm && (
        <div className="card" style={{ marginBottom: '1.5rem', maxWidth: 480 }}>
          <div className="section-title">New Topic</div>
          <div className="form-group">
            <label>Topic Name *</label>
            <input
              placeholder="e.g. Artificial Intelligence"
              value={form.name}
              onChange={e => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div className="form-group">
            <label>Keywords (comma-separated)</label>
            <input
              placeholder="e.g. AI, machine learning, LLM"
              value={form.keywords}
              onChange={e => setForm({ ...form, keywords: e.target.value })}
            />
          </div>
          <button className="btn btn-primary" onClick={handleSubmit} disabled={submitting}>
            {submitting ? 'Creating...' : 'Create Topic'}
          </button>
        </div>
      )}

      {loading ? (
        <div className="loading-spinner">Loading topics...</div>
      ) : topics.length === 0 ? (
        <div className="empty-state">
          No topics yet. Create your first topic to start tracking!
        </div>
      ) : (
        <div className="grid-3">
          {topics.map(topic => (
            <TopicCard
              key={topic.id}
              topic={topic}
              onDelete={id => setTopics(prev => prev.filter(t => t.id !== id))}
              onRefresh={fetchTopics}
            />
          ))}
        </div>
      )}
    </div>
  );
}