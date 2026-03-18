from django.urls import path
from . import views

app_name = 'projets'

urlpatterns = [
    path('', views.ProjetListView.as_view(), name='liste'),
    path('nouveau/', views.ProjetCreateView.as_view(), name='creer'),
    path('<int:pk>/', views.ProjetDetailView.as_view(), name='detail'),
    path('<int:pk>/modifier/', views.ProjetUpdateView.as_view(), name='modifier'),
    path('<int:pk>/supprimer/', views.ProjetDeleteView.as_view(), name='supprimer'),
]
