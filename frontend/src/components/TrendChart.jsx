import React from 'react';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement,
  LineElement, Title, Tooltip, Legend, Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

export default function TrendChart({ data, title }) {
  if (!data || data.length === 0) {
    return <div className="empty-state">No trend data available yet</div>;
  }

  const labels = [...new Set(data.map(d => d.date))].sort();
  const platforms = [...new Set(data.map(d => d.platform))];

  const colors = {
    twitter: { line: '#1da1f2', bg: 'rgba(29,161,242,0.08)' },
    youtube: { line: '#ff4444', bg: 'rgba(255,68,68,0.08)' },
    combined: { line: '#6c63ff', bg: 'rgba(108,99,255,0.08)' },
  };

  const datasets = platforms.map(platform => {
    const platformData = data.filter(d => d.platform === platform);
    const vals = labels.map(date => {
      const entry = platformData.find(d => d.date === date);
      return entry ? entry.avg_engagement : null;
    });
    const c = colors[platform] || colors.combined;
    return {
      label: platform.charAt(0).toUpperCase() + platform.slice(1),
      data: vals,
      borderColor: c.line,
      backgroundColor: c.bg,
      fill: true,
      tension: 0.4,
      pointRadius: 4,
      pointHoverRadius: 6,
      borderWidth: 2,
      spanGaps: true,
    };
  });

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#9090c0', font: { family: 'Space Mono', size: 11 } }
      },
      tooltip: {
        backgroundColor: '#16163a',
        borderColor: '#2a2a5a',
        borderWidth: 1,
        titleColor: '#e8e8ff',
        bodyColor: '#9090c0',
      }
    },
    scales: {
      x: {
        grid: { color: 'rgba(42,42,90,0.5)' },
        ticks: { color: '#9090c0', font: { family: 'Space Mono', size: 10 } }
      },
      y: {
        grid: { color: 'rgba(42,42,90,0.5)' },
        ticks: { color: '#9090c0', font: { family: 'Space Mono', size: 10 } }
      }
    }
  };

  return (
    <div style={{ height: 260 }}>
      <Line data={{ labels, datasets }} options={options} />
    </div>
  );
}