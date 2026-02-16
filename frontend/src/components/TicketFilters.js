import React from 'react';
import './TicketFilters.css';

const CATEGORIES = ['billing', 'technical', 'account', 'general'];
const PRIORITIES = ['low', 'medium', 'high', 'critical'];
const STATUSES = ['open', 'in_progress', 'resolved', 'closed'];

function TicketFilters({ filters, onFilterChange }) {
  const handleChange = (filterName, value) => {
    onFilterChange({
      ...filters,
      [filterName]: value,
    });
  };

  const clearFilters = () => {
    onFilterChange({
      category: '',
      priority: '',
      status: '',
      search: '',
    });
  };

  const hasActiveFilters = Object.values(filters).some(v => v !== '');

  return (
    <div className="ticket-filters-container">
      <h2>Filter Tickets</h2>
      
      <div className="filters-grid">
        <div className="filter-group">
          <label htmlFor="search">Search</label>
          <input
            id="search"
            type="text"
            placeholder="Search title or description..."
            value={filters.search || ''}
            onChange={(e) => handleChange('search', e.target.value)}
          />
        </div>

        <div className="filter-group">
          <label htmlFor="category">Category</label>
          <select
            id="category"
            value={filters.category || ''}
            onChange={(e) => handleChange('category', e.target.value)}
          >
            <option value="">All Categories</option>
            {CATEGORIES.map((cat) => (
              <option key={cat} value={cat}>
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="priority">Priority</label>
          <select
            id="priority"
            value={filters.priority || ''}
            onChange={(e) => handleChange('priority', e.target.value)}
          >
            <option value="">All Priorities</option>
            {PRIORITIES.map((pri) => (
              <option key={pri} value={pri}>
                {pri.charAt(0).toUpperCase() + pri.slice(1)}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="status">Status</label>
          <select
            id="status"
            value={filters.status || ''}
            onChange={(e) => handleChange('status', e.target.value)}
          >
            <option value="">All Statuses</option>
            {STATUSES.map((stat) => (
              <option key={stat} value={stat}>
                {stat.replace('_', ' ').charAt(0).toUpperCase() + stat.slice(1).replace('_', ' ')}
              </option>
            ))}
          </select>
        </div>
      </div>

      {hasActiveFilters && (
        <button className="clear-filters-button" onClick={clearFilters}>
          Clear All Filters
        </button>
      )}
    </div>
  );
}

export default TicketFilters;
