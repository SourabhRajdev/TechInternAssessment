# Quick Setup Guide

## Prerequisites
- Docker Desktop installed and running
- Google Gemini API key (free tier available at https://makersuite.google.com/app/apikey)

## Setup Steps

1. **Get an API Key**
   - Visit https://makersuite.google.com/app/apikey
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the key (save it securely)

2. **Configure Environment**
   ```bash
   # Create .env file in project root
   echo "GOOGLE_API_KEY=your_actual_key_here" > .env
   ```

3. **Start the Application**
   ```bash
   docker-compose up --build
   ```
   
   This will:
   - Pull PostgreSQL image
   - Build Django backend
   - Build React frontend
   - Run database migrations automatically
   - Start all services

4. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/
   - Admin Panel: http://localhost:8000/admin/

## First Time Usage

1. Open http://localhost:3000
2. Fill out the ticket form
3. Type a description (e.g., "I can't log into my account")
4. Wait 1 second - the AI will auto-suggest category and priority
5. Review/modify the suggestions
6. Submit the ticket
7. See it appear in the list below

## Troubleshooting

### "Connection refused" errors
- Ensure Docker Desktop is running
- Wait 30 seconds for all services to start
- Check logs: `docker-compose logs backend`

### LLM classification not working
- Verify your API key is correct in `.env`
- Check backend logs: `docker-compose logs backend | grep LLM`
- The system will still work - you'll just select category/priority manually

### Port already in use
- Change ports in `docker-compose.yml`:
  ```yaml
  ports:
    - "3001:3000"  # Frontend
    - "8001:8000"  # Backend
  ```

## Stopping the Application

```bash
# Stop containers
docker-compose down

# Stop and remove volumes (clears database)
docker-compose down -v
```

## Development Mode

To make code changes:

1. Edit files in `backend/` or `frontend/`
2. Changes are automatically reflected (hot reload)
3. For backend changes, restart: `docker-compose restart backend`

## Creating Admin User

```bash
docker-compose exec backend python manage.py createsuperuser
```

Then access http://localhost:8000/admin/
