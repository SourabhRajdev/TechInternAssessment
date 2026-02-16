import React from 'react';
import './StatsDashboard.css';

function StatsDashboard({ stats }) {
  if (!stats) {
    return (
      <div className="stats-dashboard-container">
        <h2>Statistics</h2>
        <div className="loading">Loading statistics...</div>
      </div>
    );
  }

  return (
    <div className="stats-dashboard-container">
      <h2>Statistics Dashboard</h2>
      
      <div className="stats-grid">
        {/* Overview Stats */}
        <div className="stat-card highlight">
          <div className="stat-value">{stats.total_tickets}</div>
          <div className="stat-label">Total Tickets</div>
        </div>

        <div className="stat-card highlight">
          <div className="stat-value">{stats.open_tickets}</div>
          <div className="stat-label">Open Tickets</div>
        </div>

        <div className="stat-card highlight">
          <div className="stat-value">{stats.avg_tickets_per_day}</div>
          <div className="stat-label">Avg per Day</div>
        </div>
      </div>

      {/* Priority Breakdown */}
      <div className="breakdown-section">
        <h3>Priority Breakdown</h3>
        <div className="breakdown-grid">
          {Object.entries(stats.priority_breakdown).map(([priority, count]) => (
            <div key={priority} className={`breakdown-card priority-${priority}`}>
              <div className="breakdown-value">{count}</div>
              <div className="breakdown-label">
                {priority.charAt(0).toUpperCase() + priority.slice(1)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Category Breakdown */}
      <div className="breakdown-section">
        <h3>Category Breakdown</h3>
        <div className="breakdown-grid">
          {Object.entries(stats.category_breakdown).map(([category, count]) => (
            <div key={category} className="breakdown-card category">
              <div className="breakdown-value">{count}</div>
              <div className="breakdown-label">
                {category.charAt(0).toUpperCase() + category.slice(1)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default StatsDashboard;
