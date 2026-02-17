# Support Ticket System

A production-grade support ticket management system with AI-powered classification, built with Django, React, and PostgreSQL.

## 🎯 Overview

This system allows users to submit support tickets, browse and filter them, and view aggregated metrics. The key differentiator is **LLM-powered auto-classification**: when a user writes a ticket description, the system automatically suggests a category and priority level using Anthropic's Claude AI.

## 🏗️ Architecture

### Backend
- **Framework**: Django 4.2 + Django REST Framework
- **Database**: PostgreSQL 15 with database-level constraint enforcement
- **LLM**: Google Gemini Pro
- **Key Features**:
  - RESTful API with comprehensive filtering
  - Database-level aggregation for statistics (no Python loops)
  - Circuit breaker pattern for LLM integration
  - Graceful degradation when LLM is unavailable

### Frontend
- **Framework**: React 18 with functional components and hooks
- **State Management**: React hooks (useState, useEffect, useCallback)
- **Key Features**:
  - Real-time LLM classification with debouncing
  - Optimistic UI updates
  - Comprehensive filtering and search
  - Auto-refreshing statistics dashboard

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Services**: PostgreSQL, Django backend, React frontend
- **Orchestration**: Automatic migrations, health checks, proper service dependencies

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Google Gemini API key (get one at https://makersuite.google.com/app/apikey)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd support-ticket-system
   ```

2. **Set your API key**
   
   Create a `.env` file in the root directory:
   ```bash
   GOOGLE_API_KEY=your_api_key_here
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/
   - Django Admin: http://localhost:8000/admin/

The application will be fully functional after the containers start. Migrations run automatically.

## 📊 API Endpoints

### Tickets

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tickets/create/` | Create a new ticket |
| GET | `/api/tickets/` | List all tickets (supports filtering) |
| PATCH | `/api/tickets/<id>/` | Update a ticket |
| GET | `/api/tickets/stats/` | Get aggregated statistics |
| POST | `/api/tickets/classify/` | LLM classification endpoint |

### Filtering

The `/api/tickets/` endpoint supports composable filters:
- `?category=billing` - Filter by category
- `?priority=high` - Filter by priority
- `?status=open` - Filter by status
- `?search=login` - Search in title and description

Example: `/api/tickets/?category=technical&priority=high&status=open`

### Statistics Response

```json
{
  "total_tickets": 124,
  "open_tickets": 67,
  "avg_tickets_per_day": 8.3,
  "priority_breakdown": {
    "low": 30,
    "medium": 52,
    "high": 31,
    "critical": 11
  },
  "category_breakdown": {
    "billing": 28,
    "technical": 55,
    "account": 22,
    "general": 19
  }
}
```

## 🤖 LLM Integration

### Why Google Gemini?

I chose **Google Gemini Pro** for several production-critical reasons:

1. **Free Tier Availability**: Gemini offers a generous free tier, making it accessible for development and testing without immediate costs.

2. **Structured Output Quality**: Gemini Pro excels at following precise instructions and returning well-formatted JSON, crucial for our classification task.

3. **Fast Response Times**: Gemini's response times are excellent for real-time user interactions with proper debouncing.

4. **Google Infrastructure**: Built on Google's proven infrastructure with high reliability and uptime.

5. **Easy Integration**: The google-generativeai Python library provides a clean, simple API for integration.

6. **Cost Effective**: For production workloads, Gemini offers competitive pricing compared to other LLM providers.

### How It Works

1. **User Input**: User types a ticket description
2. **Debouncing**: Frontend waits 1 second after typing stops
3. **API Call**: Description sent to `/api/tickets/classify/`
4. **LLM Processing**: Gemini analyzes the description using a carefully crafted prompt
5. **Validation**: Backend validates the response against allowed enums
6. **Auto-fill**: Frontend pre-fills category and priority dropdowns
7. **User Override**: User can accept or change the suggestions

### Prompt Design

The prompt is designed for reliability:
- Clear category and priority definitions
- Explicit output format requirements (JSON only)
- No markdown or explanatory text allowed
- Temperature set to 0 for deterministic output

See `backend/tickets/llm_service.py` for the full prompt.

### Graceful Degradation

The system handles LLM failures gracefully:
- **Timeout**: Returns 503, frontend allows manual selection
- **Invalid Response**: Logged and ignored, user selects manually
- **API Key Missing**: Service disabled, tickets still work
- **Network Error**: Caught and logged, no impact on ticket submission

## 🗄️ Database Design

### Ticket Model

All constraints are enforced at the database level:

```python
class Ticket(models.Model):
    title = CharField(max_length=200, blank=False, null=False)
    description = TextField(blank=False, null=False)
    category = CharField(choices=CATEGORY_CHOICES, blank=False, null=False)
    priority = CharField(choices=PRIORITY_CHOICES, blank=False, null=False)
    status = CharField(choices=STATUS_CHOICES, default='open', blank=False, null=False)
    created_at = DateTimeField(auto_now_add=True)
```

**Indexes**:
- Primary index on `created_at` (descending) for efficient newest-first queries
- Composite index on `(status, priority)` for filtered queries
- Individual indexes on `category`, `priority`, `status` for filter performance

**Constraints**:
- All choice fields use database-level CHECK constraints
- NOT NULL constraints on all required fields
- Max length enforced on title (200 characters)

## 📈 Statistics Implementation

The `/api/tickets/stats/` endpoint uses **pure database-level aggregation**:

```python
# Priority breakdown using Django ORM
priority_counts = Ticket.objects.values('priority').annotate(count=Count('id'))

# Category breakdown using Django ORM
category_counts = Ticket.objects.values('category').annotate(count=Count('id'))
```

**No Python loops** are used for aggregation. All counting and grouping happens in PostgreSQL.

## 🎨 Frontend Architecture

### Component Structure

```
src/
├── App.js                      # Main application container
├── api.js                      # Centralized API client
├── components/
│   ├── TicketForm.js          # Ticket submission with LLM integration
│   ├── TicketList.js          # Ticket display with status updates
│   ├── TicketFilters.js       # Filter controls
│   └── StatsDashboard.js      # Statistics visualization
```

### State Management

- **Local State**: Component-specific UI state (forms, modals)
- **Lifted State**: Shared state in App.js (tickets, filters, stats)
- **Optimistic Updates**: UI updates immediately, then syncs with backend

### Key Features

1. **Debounced LLM Calls**: 1-second delay after typing stops
2. **Loading States**: Visual feedback during async operations
3. **Error Handling**: User-friendly error messages
4. **Responsive Design**: Works on desktop and mobile
5. **Accessibility**: Semantic HTML, proper labels, keyboard navigation

## 🔒 Security Considerations

1. **API Key Management**: Never hardcoded, passed via environment variables
2. **CORS Configuration**: Configured for development (should be restricted in production)
3. **Input Validation**: Both frontend and backend validation
4. **SQL Injection**: Protected by Django ORM parameterization
5. **XSS Protection**: React's built-in escaping

## 🧪 Testing the Application

### Manual Testing Checklist

1. **Create Ticket**:
   - Fill out form with description
   - Verify LLM auto-suggests category and priority
   - Override suggestions if desired
   - Submit and verify ticket appears in list

2. **Filter Tickets**:
   - Test each filter individually
   - Test combined filters
   - Test search functionality

3. **Update Status**:
   - Click a ticket
   - Change status in modal
   - Verify update reflects immediately

4. **Statistics**:
   - Verify counts are accurate
   - Create new ticket and verify stats update

5. **LLM Failure**:
   - Stop backend or use invalid API key
   - Verify tickets can still be created manually

## 🐳 Docker Configuration

### Services

1. **db** (PostgreSQL):
   - Image: postgres:15-alpine
   - Health check ensures backend waits for DB
   - Persistent volume for data

2. **backend** (Django):
   - Auto-runs migrations on startup
   - Depends on healthy database
   - Exposes port 8000

3. **frontend** (React):
   - Development server with hot reload
   - Depends on backend
   - Exposes port 3000

### Environment Variables

- `GOOGLE_API_KEY`: Your Google Gemini API key
- `DATABASE_URL`: PostgreSQL connection string (auto-configured)
- `DEBUG`: Django debug mode (True in development)

## 📝 Design Decisions

### Backend

1. **Database-Level Constraints**: Ensures data integrity even if application logic fails
2. **ORM Aggregation**: Leverages PostgreSQL's performance for statistics
3. **Circuit Breaker Pattern**: LLM failures don't break ticket submission
4. **Logging**: Comprehensive logging for debugging and monitoring
5. **Serializer Validation**: Multiple serializers for different use cases

### Frontend

1. **Debouncing**: Reduces API calls while maintaining responsiveness
2. **Optimistic Updates**: Better UX with immediate feedback
3. **Component Composition**: Reusable, testable components
4. **Error Boundaries**: Graceful handling of component failures
5. **CSS Modules**: Scoped styling to prevent conflicts

### Infrastructure

1. **Health Checks**: Ensures services start in correct order
2. **Auto-Migrations**: Zero manual setup required
3. **Volume Persistence**: Database survives container restarts
4. **Environment-Based Config**: Easy to adapt for different environments

## 🔄 Development Workflow

The Git history shows incremental development:

1. Initial Django setup with PostgreSQL
2. Ticket model with database constraints
3. Serializers and validation
4. API views with filtering and aggregation
5. LLM integration service
6. React frontend structure
7. Component implementation
8. Docker configuration
9. Documentation

Each commit represents a logical unit of work.

## 🚀 Production Considerations

Before deploying to production:

1. **Security**:
   - Change SECRET_KEY
   - Set DEBUG=False
   - Configure ALLOWED_HOSTS
   - Restrict CORS_ALLOWED_ORIGINS
   - Use HTTPS

2. **Database**:
   - Use managed PostgreSQL service
   - Configure backups
   - Set up connection pooling

3. **LLM**:
   - Implement rate limiting
   - Add caching for common descriptions
   - Monitor API costs

4. **Frontend**:
   - Build production bundle
   - Serve via CDN
   - Enable compression

5. **Monitoring**:
   - Set up error tracking (Sentry)
   - Configure logging aggregation
   - Add performance monitoring

## 📄 License

This project is for evaluation purposes.

## 👤 Author

Built as a technical assessment demonstrating production-grade software engineering practices.
