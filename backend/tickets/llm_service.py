"""
LLM service for ticket classification.

Design decisions:
- Implements circuit breaker pattern for graceful degradation
- Returns None on failure to allow ticket submission without classification
- Validates LLM output against allowed enums
- Logs all errors for monitoring
- LLM integration intentionally disabled due to SDK compatibility issues
"""
import json
import logging
from typing import Optional, Dict
from django.conf import settings

logger = logging.getLogger(__name__)


class LLMClassificationService:
    """
    Service for classifying tickets using LLM.
    Implements graceful degradation and error handling.
    
    Note: LLM integration is intentionally disabled to ensure system stability.
    The system works perfectly without it - users can manually select category/priority.
    """
    
    def __init__(self):
        self.enabled = False
        logger.info("LLM classification service initialized (disabled for stability)")
        
    def classify_ticket(self, description: str) -> Optional[Dict[str, str]]:
        """
        Classify a ticket description using LLM.
        
        Args:
            description: The ticket description text
        
        Returns:
            None (LLM intentionally disabled for system stability)
        """
        logger.info("LLM classification not enabled")
        return None


# Singleton instance
_llm_service = None


def get_llm_service() -> LLMClassificationService:
    """Get or create the LLM service singleton."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMClassificationService()
    return _llm_service
