/**
 * API client for backend communication.
 * Centralizes all API calls with consistent error handling.
 */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Generic fetch wrapper with error handling.
 */
async function apiFetch(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };
  
  try {
    const response = await fetch(url, config);
    
    // Handle non-JSON responses
    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      throw new Error(`Server returned non-JSON response: ${response.statusText}`);
    }
    
    const data = await response.json();
    
    if (!response.ok) {
      throw new Error(data.error || data.detail || `HTTP ${response.status}`);
    }
    
    return data;
  } catch (error) {
    console.error(`API Error [${endpoint}]:`, error);
    throw error;
  }
}

/**
 * Fetch all tickets with optional filters.
 */
export async function fetchTickets(filters = {}) {
  const params = new URLSearchParams();
  
  if (filters.category) params.append('category', filters.category);
  if (filters.priority) params.append('priority', filters.priority);
  if (filters.status) params.append('status', filters.status);
  if (filters.search) params.append('search', filters.search);
  
  const queryString = params.toString();
  const endpoint = `/api/tickets/${queryString ? `?${queryString}` : ''}`;
  
  return apiFetch(endpoint);
}

/**
 * Create a new ticket.
 */
export async function createTicket(ticketData) {
  return apiFetch('/api/tickets/', {
    method: 'POST',
    body: JSON.stringify(ticketData),
  });
}

/**
 * Update a ticket (typically status changes).
 */
export async function updateTicket(ticketId, updates) {
  return apiFetch(`/api/tickets/${ticketId}/`, {
    method: 'PATCH',
    body: JSON.stringify(updates),
  });
}

/**
 * Fetch ticket statistics.
 */
export async function fetchStats() {
  return apiFetch('/api/tickets/stats/');
}

/**
 * Classify a ticket description using LLM.
 * Returns null on failure (graceful degradation).
 */
export async function classifyTicket(description) {
  try {
    return await apiFetch('/api/tickets/classify/', {
      method: 'POST',
      body: JSON.stringify({ description }),
    });
  } catch (error) {
    // LLM service unavailable - return null for graceful degradation
    console.warn('LLM classification unavailable:', error.message);
    return null;
  }
}
