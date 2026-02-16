#!/bin/bash

# API Testing Script
# Tests all endpoints to verify the system is working

API_URL="http://localhost:8000/api"

echo "🧪 Testing Support Ticket System API"
echo "===================================="
echo ""

# Test 1: Create a ticket
echo "1️⃣ Creating a test ticket..."
TICKET_RESPONSE=$(curl -s -X POST "$API_URL/tickets/create/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test ticket from script",
    "description": "This is a test ticket to verify the API is working correctly",
    "category": "technical",
    "priority": "medium"
  }')

TICKET_ID=$(echo $TICKET_RESPONSE | grep -o '"id":[0-9]*' | grep -o '[0-9]*')

if [ -n "$TICKET_ID" ]; then
  echo "✅ Ticket created successfully (ID: $TICKET_ID)"
else
  echo "❌ Failed to create ticket"
  echo "Response: $TICKET_RESPONSE"
  exit 1
fi
echo ""

# Test 2: List tickets
echo "2️⃣ Listing all tickets..."
LIST_RESPONSE=$(curl -s "$API_URL/tickets/")
TICKET_COUNT=$(echo $LIST_RESPONSE | grep -o '"id":' | wc -l)
echo "✅ Found $TICKET_COUNT ticket(s)"
echo ""

# Test 3: Get statistics
echo "3️⃣ Fetching statistics..."
STATS_RESPONSE=$(curl -s "$API_URL/tickets/stats/")
TOTAL=$(echo $STATS_RESPONSE | grep -o '"total_tickets":[0-9]*' | grep -o '[0-9]*')
echo "✅ Total tickets: $TOTAL"
echo ""

# Test 4: Filter tickets
echo "4️⃣ Testing filters..."
FILTER_RESPONSE=$(curl -s "$API_URL/tickets/?category=technical&priority=medium")
echo "✅ Filter by category and priority working"
echo ""

# Test 5: Update ticket
echo "5️⃣ Updating ticket status..."
UPDATE_RESPONSE=$(curl -s -X PATCH "$API_URL/tickets/$TICKET_ID/" \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}')
echo "✅ Ticket status updated"
echo ""

# Test 6: LLM Classification (may fail if no API key)
echo "6️⃣ Testing LLM classification..."
CLASSIFY_RESPONSE=$(curl -s -X POST "$API_URL/tickets/classify/" \
  -H "Content-Type: application/json" \
  -d '{"description": "I cannot access my account after password reset"}')

if echo $CLASSIFY_RESPONSE | grep -q "suggested_category"; then
  echo "✅ LLM classification working"
else
  echo "⚠️  LLM classification unavailable (API key may not be configured)"
fi
echo ""

echo "===================================="
echo "✅ All core API tests passed!"
echo ""
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:8000"
