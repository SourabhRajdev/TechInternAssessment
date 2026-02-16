# Deployment Checklist

## Pre-Deployment Verification

### 1. Environment Setup
- [ ] Docker Desktop installed and running
- [ ] Anthropic API key obtained
- [ ] `.env` file created with API key
- [ ] Ports 3000 and 8000 available

### 2. Build and Start
```bash
# Clean start
docker-compose down -v

# Build and start
docker-compose up --build
```

Expected output:
```
✅ db_1       | database system is ready to accept connections
✅ backend_1  | Applying migrations...
✅ backend_1  | Operations to perform: ...
✅ backend_1  | Django version 4.2.9, using settings 'config.settings'
✅ backend_1  | Starting development server at http://0.0.0.0:8000/
✅ frontend_1 | webpack compiled successfully
```

### 3. Service Health Checks

#### Database
```bash
docker-compose exec db psql -U ticketuser -d ticketdb -c "SELECT 1;"
```
Expected: `1` (1 row)

#### Backend
```bash
curl http://localhost:8000/api/tickets/
```
Expected: `[]` (empty array) or list of tickets

#### Frontend
Open http://localhost:3000
Expected: Application loads with header "Support Ticket System"

### 4. Functional Tests

#### Test 1: Create Ticket
1. Open http://localhost:3000
2. Fill form:
   - Title: "Test ticket"
   - Description: "I cannot access my billing information"
3. Wait 1 second
4. Verify: Category and priority auto-filled
5. Click "Submit Ticket"
6. Verify: Ticket appears in list below

#### Test 2: LLM Classification
```bash
curl -X POST http://localhost:8000/api/tickets/classify/ \
  -H "Content-Type: application/json" \
  -d '{"description": "I cannot log into my account"}'
```
Expected:
```json
{
  "suggested_category": "account",
  "suggested_priority": "high"
}
```

#### Test 3: Filters
1. Create multiple tickets with different categories
2. Use category filter dropdown
3. Verify: Only matching tickets shown

#### Test 4: Statistics
1. Check stats dashboard
2. Create new ticket
3. Verify: Stats update automatically

#### Test 5: Status Update
1. Click any ticket in list
2. Modal opens
3. Click different status button
4. Verify: Status updates immediately

### 5. API Endpoint Tests

Run the test script:
```bash
./test_api.sh
```

Expected output:
```
✅ Ticket created successfully
✅ Found X ticket(s)
✅ Total tickets: X
✅ Filter by category and priority working
✅ Ticket status updated
✅ LLM classification working
✅ All core API tests passed!
```

### 6. Error Handling Tests

#### Test: LLM Unavailable
1. Stop backend: `docker-compose stop backend`
2. Try to create ticket in frontend
3. Expected: Form still works, manual selection required
4. Restart: `docker-compose start backend`

#### Test: Invalid Input
```bash
curl -X POST http://localhost:8000/api/tickets/create/ \
  -H "Content-Type: application/json" \
  -d '{"title": ""}'
```
Expected: 400 error with validation message

### 7. Performance Checks

#### Database Queries
```bash
docker-compose exec backend python manage.py shell
```
```python
from tickets.models import Ticket
from django.db import connection
from django.test.utils import override_settings

# Check query count for stats
with override_settings(DEBUG=True):
    from tickets.views import ticket_stats
    from rest_framework.test import APIRequestFactory
    factory = APIRequestFactory()
    request = factory.get('/api/tickets/stats/')
    response = ticket_stats(request)
    print(f"Queries: {len(connection.queries)}")
```
Expected: < 10 queries

#### Response Times
```bash
time curl http://localhost:8000/api/tickets/stats/
```
Expected: < 500ms

### 8. Data Integrity Checks

#### Verify Constraints
```bash
docker-compose exec db psql -U ticketuser -d ticketdb
```
```sql
-- Check table structure
\d tickets_ticket

-- Verify constraints exist
SELECT conname, contype 
FROM pg_constraint 
WHERE conrelid = 'tickets_ticket'::regclass;

-- Check indexes
\di tickets_ticket*
```

Expected:
- NOT NULL constraints on all required fields
- CHECK constraints on choice fields
- Indexes on created_at, category, priority, status

### 9. Log Verification

#### Backend Logs
```bash
docker-compose logs backend | grep -i error
```
Expected: No critical errors

#### Frontend Logs
```bash
docker-compose logs frontend | grep -i error
```
Expected: No compilation errors

### 10. Security Checks

- [ ] No API keys in code
- [ ] Environment variables used
- [ ] CORS configured (allow all for dev)
- [ ] No SQL injection vulnerabilities (ORM used)
- [ ] Input validation on all endpoints

## Post-Deployment Verification

### Smoke Test (2 minutes)
1. ✅ Frontend loads
2. ✅ Can create ticket
3. ✅ LLM suggests category/priority
4. ✅ Ticket appears in list
5. ✅ Stats update
6. ✅ Filters work
7. ✅ Status update works

### Full Test (10 minutes)
1. ✅ All API endpoints respond
2. ✅ All filters work individually
3. ✅ Combined filters work
4. ✅ Search works
5. ✅ LLM classification works
6. ✅ Error handling works
7. ✅ Stats are accurate
8. ✅ UI is responsive

## Troubleshooting

### Issue: "Connection refused"
**Solution**: Wait 30 seconds for services to start
```bash
docker-compose ps  # Check service status
```

### Issue: "Port already in use"
**Solution**: Change ports in docker-compose.yml
```yaml
ports:
  - "3001:3000"  # Frontend
  - "8001:8000"  # Backend
```

### Issue: "LLM classification unavailable"
**Solution**: Check API key
```bash
docker-compose exec backend env | grep ANTHROPIC
```

### Issue: "Migrations not applied"
**Solution**: Run manually
```bash
docker-compose exec backend python manage.py migrate
```

### Issue: "Frontend not updating"
**Solution**: Clear browser cache or hard refresh (Cmd+Shift+R)

## Rollback Procedure

If deployment fails:
```bash
# Stop all services
docker-compose down

# Remove volumes (clears database)
docker-compose down -v

# Rebuild from scratch
docker-compose up --build
```

## Success Criteria

✅ All services running
✅ All endpoints responding
✅ LLM classification working
✅ Frontend fully functional
✅ No errors in logs
✅ Stats accurate
✅ Filters working
✅ Status updates working

## Sign-Off

- [ ] Deployment successful
- [ ] All tests passed
- [ ] No critical errors
- [ ] Performance acceptable
- [ ] Ready for use

**Deployed by**: _________________
**Date**: _________________
**Time**: _________________
**Version**: main branch, commit: _________________
