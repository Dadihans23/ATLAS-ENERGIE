"""
URLs principales – GestionProjetAgence / Atlas Énergies
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static

from core.views import serve_media, handler403, handler404, handler500

admin.site.site_header = "Atlas Énergies – Administration"
admin.site.site_title = "Atlas Énergies"
admin.site.index_title = "Tableau de bord administrateur"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('comptes/', include('allauth.urls')),
    path('tableau-de-bord/', include('dashboard.urls', namespace='dashboard')),
    path('projets/', include('projets.urls', namespace='projets')),
    path('depenses/', include('depenses.urls', namespace='depenses')),
    # Médias protégés (login requis) – avant la route racine
    re_path(r'^media/(?P<path>.+)$', serve_media, name='serve_media'),
    path('', include('core.urls', namespace='core')),
]

# Statiques en développement
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    import debug_toolbar
    urlpatterns = [path('__debug__/', include(debug_toolbar.urls))] + urlpatterns

# Handlers d'erreur globaux
handler403 = 'core.views.handler403'
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'
