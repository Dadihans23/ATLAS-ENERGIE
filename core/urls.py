from django.urls import path
from django.views.generic import RedirectView

from . import views

app_name = 'core'

urlpatterns = [
    # Redirection racine vers tableau de bord
    path('', RedirectView.as_view(pattern_name='dashboard:accueil'), name='accueil'),

    # Gestion des utilisateurs (Chef d'Agence uniquement)
    path('utilisateurs/', views.AgentListView.as_view(), name='agent_liste'),
    path('utilisateurs/nouveau/', views.AgentCreateView.as_view(), name='agent_creer'),
    path('utilisateurs/<int:pk>/modifier/', views.AgentUpdateView.as_view(), name='agent_modifier'),
    path('utilisateurs/<int:pk>/toggle/', views.agent_toggle_active, name='agent_toggle'),
]
