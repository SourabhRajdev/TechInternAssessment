#!/bin/bash

# Docker Verification Script
# This script verifies the entire system works with docker-compose

set -e

echo "=========================================="
echo "Support Ticket System - Docker Verification"
echo "=========================================="
echo ""

# Check Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    echo "Install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed"
    exit 1
fi

echo "✅ Docker and docker-compose are installed"
echo ""

# Check .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your GOOGLE_API_KEY"
    echo ""
fi

echo "Step 1: Cleaning up any existing containers..."
docker-compose down -v 2>/dev/null || true
echo "✅ Cleanup complete"
echo ""

echo "Step 2: Building and starting containers..."
docker-compose up --build -d
echo "✅ Containers started"
echo ""

echo "Step 3: Waiting for services to be ready..."
sleep 10

# Check if containers are running
if ! docker-compose ps | grep -q "Up"; then
    echo "❌ Containers failed to start"
    echo "Logs:"
    docker-compose logs
    exit 1
fi

echo "✅ All containers are running"
echo ""

echo "Step 4: Checking backend health..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/tickets/ > /dev/null 2>&1; then
        echo "✅ Backend is responding"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Backend failed to respond after 30 seconds"
        echo "Backend logs:"
        docker-compose logs backend
        exit 1
    fi
    sleep 1
done
echo ""

echo "Step 5: Checking frontend health..."
for i in {1..30}; do
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "✅ Frontend is responding"
        break
    fi
    if [ $i -eq 30 ]; then
        echo "❌ Frontend failed to respond after 30 seconds"
        echo "Frontend logs:"
        docker-compose logs frontend
        exit 1
    fi
    sleep 1
done
echo ""

echo "Step 6: Testing API endpoints..."

# Test ticket creation
echo "Creating test ticket..."
RESPONSE=$(curl -s -X POST http://localhost:8000/api/tickets/ \
    -H "Content-Type: application/json" \
    -d '{
        "title": "Test ticket",
        "description": "This is a test ticket",
        "category": "technical",
        "priority": "medium"
    }')

if echo "$RESPONSE" | grep -q "Test ticket"; then
    echo "✅ Ticket creation works"
else
    echo "❌ Ticket creation failed"
    echo "Response: $RESPONSE"
    exit 1
fi
echo ""

# Test ticket listing
echo "Fetching tickets..."
TICKETS=$(curl -s http://localhost:8000/api/tickets/)
if echo "$TICKETS" | grep -q "Test ticket"; then
    echo "✅ Ticket listing works"
else
    echo "❌ Ticket listing failed"
    exit 1
fi
echo ""

# Test stats endpoint
echo "Fetching stats..."
STATS=$(curl -s http://localhost:8000/api/tickets/stats/)
if echo "$STATS" | grep -q "total_tickets"; then
    echo "✅ Stats endpoint works"
else
    echo "❌ Stats endpoint failed"
    exit 1
fi
echo ""

echo "=========================================="
echo "✅ ALL TESTS PASSED"
echo "=========================================="
echo ""
echo "The application is running at:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000/api/"
echo ""
echo "To stop the application:"
echo "  docker-compose down"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
