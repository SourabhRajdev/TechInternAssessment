"""
URL routing for tickets API.
"""
from django.urls import path
from . import views

urlpatterns = [
    path('tickets/', views.list_tickets, name='list_tickets'),
    path('tickets/create/', views.create_ticket, name='create_ticket'),
    path('tickets/stats/', views.ticket_stats, name='ticket_stats'),
    path('tickets/classify/', views.classify_ticket, name='classify_ticket'),
    path('tickets/<int:pk>/', views.update_ticket, name='update_ticket'),
]
