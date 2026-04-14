from django.urls import path
from . import views, exports

app_name = 'depenses'

urlpatterns = [
    # ── Dépenses d'exploitation ───────────────────────────────────
    path('exploitation/', views.DepenseExploitationListView.as_view(), name='exploitation_liste'),
    path('exploitation/nouvelle/', views.DepenseExploitationCreateView.as_view(), name='exploitation_creer'),
    path('exploitation/<int:pk>/', views.DepenseExploitationDetailView.as_view(), name='exploitation_detail'),
    path('exploitation/<int:pk>/modifier/', views.DepenseExploitationUpdateView.as_view(), name='exploitation_modifier'),
    path('exploitation/<int:pk>/supprimer/', views.DepenseExploitationDeleteView.as_view(), name='exploitation_supprimer'),
    # Exports
    path('exploitation/export/csv/', exports.export_exploitation_csv, name='exploitation_export_csv'),
    path('exploitation/export/excel/', exports.export_exploitation_excel, name='exploitation_export_excel'),

    # ── Frais généraux ────────────────────────────────────────────
    path('frais-generaux/', views.DepenseFraisGenerauxListView.as_view(), name='fg_liste'),
    path('frais-generaux/nouveau/', views.DepenseFraisGenerauxCreateView.as_view(), name='fg_creer'),
    path('frais-generaux/<int:pk>/', views.DepenseFraisGenerauxDetailView.as_view(), name='fg_detail'),
    path('frais-generaux/<int:pk>/modifier/', views.DepenseFraisGenerauxUpdateView.as_view(), name='fg_modifier'),
    path('frais-generaux/<int:pk>/supprimer/', views.DepenseFraisGenerauxDeleteView.as_view(), name='fg_supprimer'),
    # Exports
    path('frais-generaux/export/csv/', exports.export_frais_generaux_csv, name='fg_export_csv'),
    path('frais-generaux/export/excel/', exports.export_frais_generaux_excel, name='fg_export_excel'),

    # ── Workflow validation ───────────────────────────────────────
    path('<str:type_depense>/<int:pk>/approuver/', views.approuver_n1, name='approuver_n1'),
    path('<str:type_depense>/<int:pk>/rejeter/', views.rejeter_n1, name='rejeter_n1'),
    path('<str:type_depense>/<int:pk>/approuver-dg/', views.approuver_dg, name='approuver_dg'),
    path('<str:type_depense>/<int:pk>/rejeter-dg/', views.rejeter_dg, name='rejeter_dg'),
    path('<str:type_depense>/<int:pk>/decaisser/', views.decaisser, name='decaisser'),

    # ── Décaissements ─────────────────────────────────────────────
    path('decaissements/', views.decaissements, name='decaissements'),
]
