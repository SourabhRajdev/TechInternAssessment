# Support Ticket System

A full-stack support ticket management system with AI-powered classification.

## Tech Stack

- **Backend**: Django 4.2 + Django REST Framework + PostgreSQL
- **Frontend**: React 18
- **LLM**: OpenAI GPT-3.5-turbo
- **Infrastructure**: Docker + Docker Compose

## Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key (optional, get one at https://platform.openai.com/api-keys)

### Run the Application

1. Clone the repository
2. Create `.env` file in the root directory:
   ```bash
   OPENAI_API_KEY=your_api_key_here
   ```
3. Start the application:
   ```bash
   docker-compose up --build
   ```
4. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/

The application will be fully functional after containers start. Database migrations run automatically.

## Environment Variables

### Required
- `POSTGRES_DB`: PostgreSQL database name (default: `ticketdb`)
- `POSTGRES_USER`: PostgreSQL username (default: `ticketuser`)
- `POSTGRES_PASSWORD`: PostgreSQL password (default: `ticketpass`)

### Optional
- `OPENAI_API_KEY`: OpenAI API key for LLM classification
  - If not provided, tickets can still be created with manual category/priority selection
  - LLM classification endpoint will return 503 when unavailable

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/tickets/` | Create a new ticket |
| GET | `/api/tickets/` | List all tickets (supports filtering) |
| PATCH | `/api/tickets/<id>/` | Update a ticket |
| GET | `/api/tickets/stats/` | Get aggregated statistics |
| POST | `/api/tickets/classify/` | LLM classification (optional) |

### Filtering

The `/api/tickets/` endpoint supports composable filters:
- `?category=billing` - Filter by category (billing, technical, account, general)
- `?priority=high` - Filter by priority (low, medium, high, critical)
- `?status=open` - Filter by status (open, in_progress, resolved, closed)
- `?search=login` - Search in title and description

Example: `/api/tickets/?category=technical&priority=high&status=open`

## LLM Integration

### Why OpenAI GPT-3.5-turbo?

OpenAI GPT-3.5-turbo was chosen for:
- Excellent structured output quality (reliable JSON responses)
- Fast response times for real-time classification
- Simple integration via openai library
- Proven reliability and uptime

### How It Works

1. User types a ticket description
2. Frontend debounces input (1 second delay)
3. Description sent to `/api/tickets/classify/`
4. Gemini analyzes description and returns category/priority
5. Frontend pre-fills dropdowns with suggestions
6. User can accept or override suggestions

### Graceful Degradation

The system handles LLM failures gracefully:
- Missing API key: Service disabled, manual selection works
- Timeout/error: Returns 503, frontend allows manual selection
- Invalid response: Logged and ignored, no impact on ticket creation
- LLM failure never blocks ticket submission

## Database Design

All constraints are enforced at the database level using CHECK constraints:

```python
class Ticket(models.Model):
    title = CharField(max_length=200)
    description = TextField()
    category = CharField(choices=CATEGORY_CHOICES)  # DB CHECK constraint
    priority = CharField(choices=PRIORITY_CHOICES)  # DB CHECK constraint
    status = CharField(choices=STATUS_CHOICES)      # DB CHECK constraint
    created_at = DateTimeField(auto_now_add=True)
```

Invalid values cannot be inserted even via raw SQL.

## Statistics Implementation

The `/api/tickets/stats/` endpoint uses pure database-level aggregation:
- All counting and grouping happens in PostgreSQL
- No Python loops for aggregation
- Efficient for large datasets

## Design Decisions

### Backend
- Database-level constraints ensure data integrity
- ORM aggregation leverages PostgreSQL performance
- Circuit breaker pattern for LLM (failures don't break ticket submission)
- Comprehensive logging for debugging

### Frontend
- Debouncing reduces API calls while maintaining responsiveness
- Optimistic updates provide immediate feedback
- Component composition for reusability
- Error boundaries for graceful failure handling

### Infrastructure
- Health checks ensure services start in correct order
- Auto-migrations require zero manual setup
- Volume persistence for database data
- Environment-based configuration

## Author

Sourabh Rajdev
