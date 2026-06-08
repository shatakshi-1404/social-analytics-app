import axios from 'axios';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';
const client = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' },
});

export const api = {
  // Dashboard
  getDashboard: () => client.get('/analytics/dashboard/'),
  getSentimentChart: (days = 7) => client.get(`/analytics/dashboard/sentiment_chart/?days=${days}`),
  getEngagementTrend: (topicId, days = 14) =>
    client.get(`/analytics/dashboard/engagement_trend/?topic_id=${topicId}&days=${days}`),
  refreshAll: () => client.post('/analytics/dashboard/refresh_all/'),

  // Topics
  getTopics: () => client.get('/analytics/topics/'),
  createTopic: (data) => client.post('/analytics/topics/', data),
  deleteTopic: (id) => client.delete(`/analytics/topics/${id}/`),
  refreshTopic: (id) => client.post(`/analytics/topics/${id}/refresh/`),
  analyzeTopic: (id) => client.post(`/analytics/topics/${id}/analyze/`),
  getTopicStats: (id) => client.get(`/analytics/topics/${id}/stats/`),

  // Summaries
  getSummaries: (topicId, platform) => {
    let url = '/analytics/summaries/?';
    if (topicId) url += `topic_id=${topicId}&`;
    if (platform) url += `platform=${platform}&`;
    return client.get(url);
  },

  // Metrics
  getMetrics: (topicId, days = 7) =>
    client.get(`/analytics/metrics/?topic_id=${topicId}&days=${days}`),

  // Alerts
   getAlerts: () => client.get('/alerts/subscriptions/'),
  createAlert: (data) => client.post('/alerts/subscriptions/', data),
  deleteAlert: (id) => client.delete(`/alerts/subscriptions/${id}/`),
  toggleAlert: (id, data) => client.patch(`/alerts/subscriptions/${id}/`, data),

  // Alert Events
  getAlertEvents: (unread = false) =>
    client.get(`/alerts/events/?unread=${unread}`),
  markAllRead: () => client.post('/alerts/events/mark_all_read/'),
};

export default client;