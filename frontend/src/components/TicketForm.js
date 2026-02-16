import React, { useState, useEffect } from 'react';
import { createTicket, classifyTicket } from '../api';
import './TicketForm.css';

const CATEGORIES = ['billing', 'technical', 'account', 'general'];
const PRIORITIES = ['low', 'medium', 'high', 'critical'];

function TicketForm({ onTicketCreated }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [priority, setPriority] = useState('');
  const [isClassifying, setIsClassifying] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [classificationError, setClassificationError] = useState('');

  // Auto-classify when description changes (debounced)
  useEffect(() => {
    if (!description.trim() || description.length < 10) {
      return;
    }

    const timeoutId = setTimeout(async () => {
      setIsClassifying(true);
      setClassificationError('');
      
      try {
        const result = await classifyTicket(description);
        
        if (result) {
          // Only auto-fill if user hasn't manually selected
          if (!category) {
            setCategory(result.suggested_category);
          }
          if (!priority) {
            setPriority(result.suggested_priority);
          }
        } else {
          setClassificationError('Auto-classification unavailable. Please select manually.');
        }
      } catch (err) {
        setClassificationError('Auto-classification failed. Please select manually.');
      } finally {
        setIsClassifying(false);
      }
    }, 1000); // 1 second debounce

    return () => clearTimeout(timeoutId);
  }, [description, category, priority]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validation
    if (!title.trim()) {
      setError('Title is required');
      return;
    }
    if (title.length > 200) {
      setError('Title cannot exceed 200 characters');
      return;
    }
    if (!description.trim()) {
      setError('Description is required');
      return;
    }
    if (!category) {
      setError('Please select a category');
      return;
    }
    if (!priority) {
      setError('Please select a priority');
      return;
    }

    setIsSubmitting(true);

    try {
      const newTicket = await createTicket({
        title: title.trim(),
        description: description.trim(),
        category,
        priority,
      });

      // Clear form
      setTitle('');
      setDescription('');
      setCategory('');
      setPriority('');
      setError('');
      setClassificationError('');

      // Notify parent
      if (onTicketCreated) {
        onTicketCreated(newTicket);
      }
    } catch (err) {
      setError(err.message || 'Failed to create ticket');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="ticket-form-container">
      <h2>Submit a Support Ticket</h2>
      
      <form onSubmit={handleSubmit} className="ticket-form">
        <div className="form-group">
          <label htmlFor="title">
            Title <span className="required">*</span>
          </label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Brief description of your issue"
            maxLength={200}
            disabled={isSubmitting}
          />
          <small>{title.length}/200 characters</small>
        </div>

        <div className="form-group">
          <label htmlFor="description">
            Description <span className="required">*</span>
          </label>
          <textarea
            id="description"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Detailed description of your issue..."
            rows={6}
            disabled={isSubmitting}
          />
          {isClassifying && (
            <small className="classifying">
              🤖 AI is analyzing your description...
            </small>
          )}
          {classificationError && (
            <small className="classification-error">
              {classificationError}
            </small>
          )}
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="category">
              Category <span className="required">*</span>
            </label>
            <select
              id="category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              disabled={isSubmitting}
            >
              <option value="">Select category...</option>
              {CATEGORIES.map((cat) => (
                <option key={cat} value={cat}>
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="priority">
              Priority <span className="required">*</span>
            </label>
            <select
              id="priority"
              value={priority}
              onChange={(e) => setPriority(e.target.value)}
              disabled={isSubmitting}
            >
              <option value="">Select priority...</option>
              {PRIORITIES.map((pri) => (
                <option key={pri} value={pri}>
                  {pri.charAt(0).toUpperCase() + pri.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {error && <div className="error-message">{error}</div>}

        <button
          type="submit"
          className="submit-button"
          disabled={isSubmitting || isClassifying}
        >
          {isSubmitting ? 'Submitting...' : 'Submit Ticket'}
        </button>
      </form>
    </div>
  );
}

export default TicketForm;
