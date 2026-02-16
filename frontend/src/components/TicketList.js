import React, { useState } from 'react';
import { updateTicket } from '../api';
import './TicketList.css';

const STATUSES = ['open', 'in_progress', 'resolved', 'closed'];

function TicketList({ tickets, onTicketUpdated }) {
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [isUpdating, setIsUpdating] = useState(false);

  const handleStatusChange = async (ticketId, newStatus) => {
    setIsUpdating(true);
    try {
      const updatedTicket = await updateTicket(ticketId, { status: newStatus });
      if (onTicketUpdated) {
        onTicketUpdated(updatedTicket);
      }
      setSelectedTicket(null);
    } catch (error) {
      console.error('Failed to update ticket:', error);
      alert('Failed to update ticket status');
    } finally {
      setIsUpdating(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const truncateText = (text, maxLength = 100) => {
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
  };

  const getPriorityClass = (priority) => {
    return `priority-${priority}`;
  };

  const getStatusClass = (status) => {
    return `status-${status.replace('_', '-')}`;
  };

  if (tickets.length === 0) {
    return (
      <div className="ticket-list-container">
        <h2>All Tickets</h2>
        <div className="no-tickets">
          No tickets found. Create your first ticket above!
        </div>
      </div>
    );
  }

  return (
    <div className="ticket-list-container">
      <h2>All Tickets ({tickets.length})</h2>
      
      <div className="ticket-list">
        {tickets.map((ticket) => (
          <div
            key={ticket.id}
            className={`ticket-card ${selectedTicket?.id === ticket.id ? 'selected' : ''}`}
            onClick={() => setSelectedTicket(ticket)}
          >
            <div className="ticket-header">
              <h3 className="ticket-title">{ticket.title}</h3>
              <span className={`ticket-id`}>#{ticket.id}</span>
            </div>
            
            <p className="ticket-description">
              {truncateText(ticket.description)}
            </p>
            
            <div className="ticket-meta">
              <span className={`badge ${getPriorityClass(ticket.priority)}`}>
                {ticket.priority}
              </span>
              <span className="badge category">
                {ticket.category}
              </span>
              <span className={`badge ${getStatusClass(ticket.status)}`}>
                {ticket.status.replace('_', ' ')}
              </span>
            </div>
            
            <div className="ticket-footer">
              <small className="ticket-date">{formatDate(ticket.created_at)}</small>
            </div>
          </div>
        ))}
      </div>

      {/* Status Update Modal */}
      {selectedTicket && (
        <div className="modal-overlay" onClick={() => setSelectedTicket(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Update Ticket #{selectedTicket.id}</h3>
              <button
                className="close-button"
                onClick={() => setSelectedTicket(null)}
              >
                ×
              </button>
            </div>
            
            <div className="modal-body">
              <h4>{selectedTicket.title}</h4>
              <p>{selectedTicket.description}</p>
              
              <div className="status-selector">
                <label>Change Status:</label>
                <div className="status-buttons">
                  {STATUSES.map((status) => (
                    <button
                      key={status}
                      className={`status-button ${getStatusClass(status)} ${
                        selectedTicket.status === status ? 'active' : ''
                      }`}
                      onClick={() => handleStatusChange(selectedTicket.id, status)}
                      disabled={isUpdating || selectedTicket.status === status}
                    >
                      {status.replace('_', ' ')}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default TicketList;
