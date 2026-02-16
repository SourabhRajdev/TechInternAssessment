import React, { useState, useEffect, useCallback } from 'react';
import TicketForm from './components/TicketForm';
import TicketList from './components/TicketList';
import TicketFilters from './components/TicketFilters';
import StatsDashboard from './components/StatsDashboard';
import { fetchTickets, fetchStats } from './api';
import './App.css';

function App() {
  const [tickets, setTickets] = useState([]);
  const [stats, setStats] = useState(null);
  const [filters, setFilters] = useState({
    category: '',
    priority: '',
    status: '',
    search: '',
  });
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // Load tickets with current filters
  const loadTickets = useCallback(async () => {
    try {
      setError('');
      const data = await fetchTickets(filters);
      setTickets(data);
    } catch (err) {
      setError('Failed to load tickets: ' + err.message);
      console.error('Error loading tickets:', err);
    }
  }, [filters]);

  // Load statistics
  const loadStats = useCallback(async () => {
    try {
      const data = await fetchStats();
      setStats(data);
    } catch (err) {
      console.error('Error loading stats:', err);
      // Don't show error for stats - it's not critical
    }
  }, []);

  // Initial load
  useEffect(() => {
    const initialize = async () => {
      setIsLoading(true);
      await Promise.all([loadTickets(), loadStats()]);
      setIsLoading(false);
    };
    initialize();
  }, [loadTickets, loadStats]);

  // Reload tickets when filters change
  useEffect(() => {
    if (!isLoading) {
      loadTickets();
    }
  }, [filters, isLoading, loadTickets]);

  // Handle new ticket creation
  const handleTicketCreated = (newTicket) => {
    // Add to list (optimistic update)
    setTickets((prev) => [newTicket, ...prev]);
    // Reload stats
    loadStats();
  };

  // Handle ticket update
  const handleTicketUpdated = (updatedTicket) => {
    // Update in list
    setTickets((prev) =>
      prev.map((ticket) =>
        ticket.id === updatedTicket.id ? updatedTicket : ticket
      )
    );
    // Reload stats
    loadStats();
  };

  if (isLoading) {
    return (
      <div className="container">
        <div className="loading-screen">
          <h1>Support Ticket System</h1>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <header className="app-header">
        <h1>Support Ticket System</h1>
        <p>Submit and manage support tickets with AI-powered classification</p>
      </header>

      {error && (
        <div className="error-banner">
          {error}
        </div>
      )}

      <TicketForm onTicketCreated={handleTicketCreated} />

      <StatsDashboard stats={stats} />

      <TicketFilters filters={filters} onFilterChange={setFilters} />

      <TicketList tickets={tickets} onTicketUpdated={handleTicketUpdated} />
    </div>
  );
}

export default App;
