"""
API views for ticket management.
"""
import logging
from datetime import timedelta
from django.db.models import Count, Q, Avg
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Ticket
from .serializers import (
    TicketSerializer,
    TicketUpdateSerializer,
    ClassifyRequestSerializer,
    ClassifyResponseSerializer,
)
from .llm_service import get_llm_service

logger = logging.getLogger(__name__)


@api_view(['GET', 'POST'])
def list_tickets(request):
    """
    List all tickets or create a new ticket.
    
    GET /api/tickets/
    Query params:
        - category: Filter by category
        - priority: Filter by priority
        - status: Filter by status
        - search: Search in title and description
    
    POST /api/tickets/
    Body: {
        "title": "string (max 200 chars, required)",
        "description": "string (required)",
        "category": "billing|technical|account|general (required)",
        "priority": "low|medium|high|critical (required)"
    }
    
    All filters can be combined.
    Returns tickets ordered by created_at (newest first).
    """
    if request.method == 'POST':
        # Create ticket
        serializer = TicketSerializer(data=request.data)
        
        if serializer.is_valid():
            ticket = serializer.save()
            logger.info(f"Created ticket #{ticket.id}: {ticket.title}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        logger.warning(f"Ticket creation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # GET - List tickets
    queryset = Ticket.objects.all()
    
    # Apply filters
    category = request.query_params.get('category')
    if category:
        queryset = queryset.filter(category=category)
    
    priority = request.query_params.get('priority')
    if priority:
        queryset = queryset.filter(priority=priority)
    
    ticket_status = request.query_params.get('status')
    if ticket_status:
        queryset = queryset.filter(status=ticket_status)
    
    search = request.query_params.get('search')
    if search:
        queryset = queryset.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    
    serializer = TicketSerializer(queryset, many=True)
    logger.info(f"Listed {len(serializer.data)} tickets")
    return Response(serializer.data)


@api_view(['PATCH'])
def update_ticket(request, pk):
    """
    Update a ticket (typically status changes).
    
    PATCH /api/tickets/<id>/
    Body: {
        "status": "open|in_progress|resolved|closed",
        "category": "billing|technical|account|general",
        "priority": "low|medium|high|critical"
    }
    
    All fields are optional, but at least one must be provided.
    """
    try:
        ticket = Ticket.objects.get(pk=pk)
    except Ticket.DoesNotExist:
        return Response(
            {"error": "Ticket not found"},
            status=status.HTTP_404_NOT_FOUND
        )
    
    serializer = TicketUpdateSerializer(ticket, data=request.data, partial=True)
    
    if serializer.is_valid():
        serializer.save()
        logger.info(f"Updated ticket #{pk}")
        # Return full ticket data
        full_serializer = TicketSerializer(ticket)
        return Response(full_serializer.data)
    
    logger.warning(f"Ticket update failed for #{pk}: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def ticket_stats(request):
    """
    Get aggregated ticket statistics.
    
    GET /api/tickets/stats/
    
    Returns:
    {
        "total_tickets": int,
        "open_tickets": int,
        "avg_tickets_per_day": float,
        "priority_breakdown": {
            "low": int,
            "medium": int,
            "high": int,
            "critical": int
        },
        "category_breakdown": {
            "billing": int,
            "technical": int,
            "account": int,
            "general": int
        }
    }
    
    CRITICAL: Uses database-level aggregation only, no Python loops.
    """
    # Total tickets
    total_tickets = Ticket.objects.count()
    
    # Open tickets (status = 'open')
    open_tickets = Ticket.objects.filter(status=Ticket.STATUS_OPEN).count()
    
    # Average tickets per day
    # Get the earliest ticket date
    earliest_ticket = Ticket.objects.order_by('created_at').first()
    
    if earliest_ticket and total_tickets > 0:
        days_since_first = (timezone.now() - earliest_ticket.created_at).days
        # Ensure at least 1 day to avoid division by zero
        days_since_first = max(days_since_first, 1)
        avg_tickets_per_day = round(total_tickets / days_since_first, 1)
    else:
        avg_tickets_per_day = 0.0
    
    # Priority breakdown - using database aggregation
    priority_breakdown = {}
    priority_counts = Ticket.objects.values('priority').annotate(count=Count('id'))
    
    # Initialize all priorities to 0
    for priority_choice in Ticket.PRIORITY_CHOICES:
        priority_breakdown[priority_choice[0]] = 0
    
    # Fill in actual counts
    for item in priority_counts:
        priority_breakdown[item['priority']] = item['count']
    
    # Category breakdown - using database aggregation
    category_breakdown = {}
    category_counts = Ticket.objects.values('category').annotate(count=Count('id'))
    
    # Initialize all categories to 0
    for category_choice in Ticket.CATEGORY_CHOICES:
        category_breakdown[category_choice[0]] = 0
    
    # Fill in actual counts
    for item in category_counts:
        category_breakdown[item['category']] = item['count']
    
    response_data = {
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'avg_tickets_per_day': avg_tickets_per_day,
        'priority_breakdown': priority_breakdown,
        'category_breakdown': category_breakdown,
    }
    
    logger.info(f"Generated stats: {response_data}")
    return Response(response_data)


@api_view(['POST'])
def classify_ticket(request):
    """
    Classify a ticket description using LLM.
    
    POST /api/tickets/classify/
    Body: {
        "description": "string (required)"
    }
    
    Returns:
    {
        "suggested_category": "billing|technical|account|general",
        "suggested_priority": "low|medium|high|critical"
    }
    
    On failure (LLM unavailable, timeout, invalid response):
    Returns 503 with error message.
    
    This allows the frontend to gracefully handle LLM failures
    and still submit tickets without suggestions.
    """
    serializer = ClassifyRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    description = serializer.validated_data['description']
    
    # Get LLM service and classify
    llm_service = get_llm_service()
    result = llm_service.classify_ticket(description)
    
    if result is None:
        logger.warning("LLM classification failed or unavailable")
        return Response(
            {
                "error": "Classification service unavailable",
                "detail": "Unable to classify ticket at this time. Please select category and priority manually."
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    # Validate response format
    response_serializer = ClassifyResponseSerializer(data=result)
    if not response_serializer.is_valid():
        logger.error(f"Invalid LLM response format: {result}")
        return Response(
            {
                "error": "Invalid classification response",
                "detail": "Classification service returned invalid data."
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
    
    logger.info(f"Successfully classified ticket: {result}")
    return Response(response_serializer.data)
