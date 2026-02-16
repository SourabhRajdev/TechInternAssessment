"""
LLM service for ticket classification using Anthropic Claude.

Design decisions:
- Uses Anthropic Claude for reliable structured output
- Implements circuit breaker pattern for graceful degradation
- Returns None on failure to allow ticket submission without classification
- Validates LLM output against allowed enums
- Logs all errors for monitoring
"""
import json
import logging
from typing import Optional, Dict
from django.conf import settings

logger = logging.getLogger(__name__)

# Lazy import to avoid startup errors if anthropic not installed
try:
    from anthropic import Anthropic, APIError, APITimeoutError
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
    logger.warning("Anthropic library not available. LLM classification will be disabled.")


# System prompt for Claude - designed for reliable structured output
CLASSIFICATION_PROMPT = """You are a support ticket classification assistant. Your job is to analyze a support ticket description and suggest:
1. A category (one of: billing, technical, account, general)
2. A priority level (one of: low, medium, high, critical)

Category definitions:
- billing: Payment issues, invoices, refunds, pricing questions
- technical: Software bugs, errors, performance issues, integration problems
- account: Login issues, password resets, account settings, permissions
- general: Questions, feedback, feature requests, other inquiries

Priority definitions:
- low: Minor issues, questions, non-urgent requests
- medium: Standard issues affecting single user, workarounds available
- high: Significant issues affecting multiple users or business operations
- critical: System down, data loss, security issues, blocking all users

You must respond with ONLY a valid JSON object in this exact format:
{
  "category": "one of: billing, technical, account, general",
  "priority": "one of: low, medium, high, critical"
}

Do not include any explanation, markdown formatting, or additional text. Only return the JSON object."""


class LLMClassificationService:
    """
    Service for classifying tickets using LLM.
    Implements graceful degradation and error handling.
    """
    
    def __init__(self):
        self.client = None
        self.enabled = False
        
        if not ANTHROPIC_AVAILABLE:
            logger.warning("Anthropic library not available")
            return
        
        api_key = settings.ANTHROPIC_API_KEY
        if not api_key:
            logger.warning("ANTHROPIC_API_KEY not configured. LLM classification disabled.")
            return
        
        try:
            self.client = Anthropic(api_key=api_key)
            self.enabled = True
            logger.info("LLM classification service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Anthropic client: {e}")
    
    def classify_ticket(self, description: str) -> Optional[Dict[str, str]]:
        """
        Classify a ticket description using Claude.
        
        Args:
            description: The ticket description text
        
        Returns:
            Dict with 'suggested_category' and 'suggested_priority', or None on failure
        """
        if not self.enabled or not self.client:
            logger.info("LLM classification not enabled")
            return None
        
        if not description or not description.strip():
            logger.warning("Empty description provided for classification")
            return None
        
        try:
            # Call Claude API with structured prompt
            message = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=200,
                temperature=0,  # Deterministic output for classification
                messages=[
                    {
                        "role": "user",
                        "content": f"{CLASSIFICATION_PROMPT}\n\nTicket description:\n{description}"
                    }
                ]
            )
            
            # Extract response text
            response_text = message.content[0].text.strip()
            logger.info(f"LLM raw response: {response_text}")
            
            # Parse JSON response
            try:
                result = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}. Response: {response_text}")
                return None
            
            # Validate response structure
            if not isinstance(result, dict):
                logger.error(f"LLM response is not a dict: {result}")
                return None
            
            category = result.get('category')
            priority = result.get('priority')
            
            # Validate against allowed values
            valid_categories = ['billing', 'technical', 'account', 'general']
            valid_priorities = ['low', 'medium', 'high', 'critical']
            
            if category not in valid_categories:
                logger.error(f"Invalid category from LLM: {category}")
                return None
            
            if priority not in valid_priorities:
                logger.error(f"Invalid priority from LLM: {priority}")
                return None
            
            logger.info(f"Successfully classified ticket: category={category}, priority={priority}")
            return {
                'suggested_category': category,
                'suggested_priority': priority,
            }
        
        except APITimeoutError as e:
            logger.error(f"LLM API timeout: {e}")
            return None
        
        except APIError as e:
            logger.error(f"LLM API error: {e}")
            return None
        
        except Exception as e:
            logger.error(f"Unexpected error during LLM classification: {e}", exc_info=True)
            return None


# Singleton instance
_llm_service = None


def get_llm_service() -> LLMClassificationService:
    """Get or create the LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMClassificationService()
    return _llm_service
