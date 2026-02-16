"""
Serializers for the Ticket model.
"""
from rest_framework import serializers
from .models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    """
    Serializer for Ticket model with full validation.
    """
    
    class Meta:
        model = Ticket
        fields = [
            'id',
            'title',
            'description',
            'category',
            'priority',
            'status',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_title(self, value):
        """Ensure title is not empty and within length limit."""
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty.")
        if len(value) > 200:
            raise serializers.ValidationError("Title cannot exceed 200 characters.")
        return value.strip()
    
    def validate_description(self, value):
        """Ensure description is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Description cannot be empty.")
        return value.strip()


class TicketUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for partial updates to Ticket.
    """
    
    class Meta:
        model = Ticket
        fields = ['category', 'priority', 'status']
    
    def validate(self, data):
        """Ensure at least one field is being updated."""
        if not data:
            raise serializers.ValidationError("At least one field must be provided for update.")
        return data


class ClassifyRequestSerializer(serializers.Serializer):
    """
    Serializer for LLM classification request.
    """
    description = serializers.CharField(required=True, allow_blank=False)
    
    def validate_description(self, value):
        """Ensure description is not empty."""
        if not value or not value.strip():
            raise serializers.ValidationError("Description cannot be empty.")
        return value.strip()


class ClassifyResponseSerializer(serializers.Serializer):
    """
    Serializer for LLM classification response.
    """
    suggested_category = serializers.ChoiceField(
        choices=[choice[0] for choice in Ticket.CATEGORY_CHOICES]
    )
    suggested_priority = serializers.ChoiceField(
        choices=[choice[0] for choice in Ticket.PRIORITY_CHOICES]
    )
