"""
LLM service for ticket classification using OpenAI.

Design decisions:
- Uses OpenAI GPT for reliable structured output
- Implements circuit breaker pattern for graceful degradation
- Returns None on failure to allow ticket submission without classification
- Validates LLM output against allowed enums
- Logs all errors for monitoring
- Lazy imports to avoid startup errors
"""
import json
import logging
from typing import Optional, Dict
from django.conf import settings

logger = logging.getLogger(__name__)


# System prompt for OpenAI - designed for reliable structured output
CLASSIFICATION_PROMPT = """You are an automated support ticket classifier for a customer support system.

Your task:
Given a user's support ticket description, you must determine:
1. The most appropriate category
2. The most appropriate priority

You MUST follow these rules strictly.

ALLOWED CATEGORIES (choose exactly one):
- billing
- technical
- account
- general

ALLOWED PRIORITIES (choose exactly one):
- low
- medium
- high
- critical

CATEGORY DEFINITIONS:
- billing: payment issues, refunds, invoices, charges, subscriptions
- technical: bugs, errors, crashes, system not working, performance issues
- account: login problems, password reset, account access, account settings
- general: questions, feedback, or issues that do not fit above categories

PRIORITY GUIDELINES:
- low: minor inconvenience, no urgency
- medium: user impacted but workaround exists
- high: core functionality broken, user blocked
- critical: system down, data loss, security risk, business-critical failure

OUTPUT FORMAT RULES (VERY IMPORTANT):
- Respond with VALID JSON ONLY
- Do NOT include explanations
- Do NOT include markdown code blocks
- Do NOT include extra text
- Do NOT include trailing commas

Required JSON format:
{
  "category": "<one of the allowed categories>",
  "priority": "<one of the allowed priorities>"
}

If the description is empty, unclear, or meaningless:
- Return category = "general"
- Return priority = "low"
"""


class LLMClassificationService:
    """
    Service for classifying tickets using LLM.
    Implements graceful degradation and error handling.
    Uses lazy loading to avoid import errors at startup.
    """
    
    def __init__(self):
        self.client = None
        self.enabled = False
        self.openai = None
        self._initialization_attempted = False
        
    def _lazy_init(self):
        """Lazy initialization of OpenAI - only called when actually needed."""
        if self._initialization_attempted:
            return self.enabled
            
        self._initialization_attempted = True
        
        # Try to import openai only when needed
        try:
            import openai
            self.openai = openai
        except (ImportError, TypeError) as e:
            logger.warning(f"OpenAI library not available: {e}. LLM classification disabled.")
            return False
        
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            logger.warning("OPENAI_API_KEY not configured. LLM classification disabled.")
            return False
        
        try:
            self.client = self.openai.OpenAI(api_key=api_key)
            self.enabled = True
            logger.info("LLM classification service initialized successfully with OpenAI")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {e}")
            return False
    
    def classify_ticket(self, description: str) -> Optional[Dict[str, str]]:
        """
        Classify a ticket description using OpenAI.
        
        Args:
            description: The ticket description text
        
        Returns:
            Dict with 'suggested_category' and 'suggested_priority', or None on failure
        """
        # Lazy initialization on first use
        if not self._initialization_attempted:
            self._lazy_init()
            
        if not self.enabled or not self.client:
            logger.info("LLM classification not enabled")
            return None
        
        if not description or not description.strip():
            logger.warning("Empty description provided for classification")
            return None
        
        try:
            # Construct the full prompt with user description
            full_prompt = f'{CLASSIFICATION_PROMPT}\n\nNow classify the following support ticket description:\n"""\n{description}\n"""'
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a support ticket classifier. Respond only with valid JSON."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0,  # Deterministic output
                max_tokens=200,
            )
            
            # Extract response text
            response_text = response.choices[0].message.content.strip()
            logger.info(f"LLM raw response: {response_text}")
            
            # Clean up response - remove markdown code blocks if present
            if response_text.startswith('```'):
                # Remove markdown code blocks
                lines = response_text.split('\n')
                cleaned_lines = [line for line in lines if not line.startswith('```')]
                response_text = '\n'.join(cleaned_lines).strip()
            
            # Remove 'json' prefix if present
            if response_text.lower().startswith('json'):
                response_text = response_text[4:].strip()
            
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
