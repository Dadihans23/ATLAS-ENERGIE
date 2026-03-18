from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('historique/', views.historique, name='historique'),
]
