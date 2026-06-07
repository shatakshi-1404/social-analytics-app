import React from 'react';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend);

export default function SentimentChart({ data }) {
  if (!data || data.length === 0) {
    return <div className="empty-state">No sentiment data yet</div>;
  }

  const colorMap = {
    positive: '#43e97b',
    negative: '#ff6584',
    neutral: '#a0a0d0',
    mixed: '#f7971e',
  };

  const labels = data.map(d => d.sentiment.charAt(0).toUpperCase() + d.sentiment.slice(1));
  const values = data.map(d => d.count);
  const bgColors = data.map(d => colorMap[d.sentiment] || '#6c63ff');

  const chartData = {
    labels,
    datasets: [{
      data: values,
      backgroundColor: bgColors.map(c => c + '99'),
      borderColor: bgColors,
      borderWidth: 2,
      hoverOffset: 8,
    }]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '65%',
    plugins: {
      legend: {
        position: 'right',
        labels: { color: '#9090c0', font: { family: 'Space Mono', size: 11 }, padding: 12 }
      },
      tooltip: {
        backgroundColor: '#16163a',
        borderColor: '#2a2a5a',
        borderWidth: 1,
        titleColor: '#e8e8ff',
        bodyColor: '#9090c0',
      }
    }
  };

  return (
    <div style={{ height: 200 }}>
      <Doughnut data={chartData} options={options} />
    </div>
  );
}