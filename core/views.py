"""
Vues utilitaires :
- serve_media        : protection des fichiers uploadés (login requis)
- Gestion utilisateurs : liste, création, modification (Chef d'Agence uniquement)
- Handlers 403/404/500
"""
import logging
import mimetypes
import os
from pathlib import Path as FilePath

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView

from .forms import AgentCreationForm, AgentEditForm, EmailConfigForm
from .mixins import ChefRequiredMixin
from .models import CustomUser, EmailConfig

security_logger = logging.getLogger('security')


@login_required
def serve_media(request, path: str):
    """
    Sert les fichiers médias uniquement aux utilisateurs connectés.
    Utilise pathlib.resolve() pour une protection robuste contre le directory
    traversal (y compris sur Windows avec les backslashes).
    En production, déléguer à nginx avec X-Accel-Redirect.
    """
    media_root = FilePath(settings.MEDIA_ROOT).resolve()
    try:
        file_path = (media_root / path).resolve()
        file_path.relative_to(media_root)  # Lève ValueError si hors de MEDIA_ROOT
    except (ValueError, Exception):
        raise Http404

    if not file_path.is_file():
        raise Http404

    content_type, _ = mimetypes.guess_type(str(file_path))
    content_type = content_type or 'application/octet-stream'

    return FileResponse(
        open(file_path, 'rb'),
        content_type=content_type,
    )


# ─── Gestion des utilisateurs (Chef uniquement) ──────────────────────────────

class AgentListView(ChefRequiredMixin, ListView):
    model = CustomUser
    template_name = 'core/agents/liste.html'
    context_object_name = 'utilisateurs'
    ordering = ['last_name', 'first_name']

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.GET.get('role', '')
        statut = self.request.GET.get('statut', '')
        valid_roles = [r.value for r in CustomUser.Role]
        if role in valid_roles:
            qs = qs.filter(role=role)
        if statut == 'actif':
            qs = qs.filter(is_active=True)
        elif statut == 'inactif':
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['nb_total'] = CustomUser.objects.count()
        ctx['nb_chefs'] = CustomUser.objects.filter(role=CustomUser.Role.CHEF).count()
        ctx['nb_dt'] = CustomUser.objects.filter(role=CustomUser.Role.DIRECTEUR_TECHNIQUE).count()
        ctx['nb_df'] = CustomUser.objects.filter(role=CustomUser.Role.DIRECTEUR_FINANCIER).count()
        ctx['nb_agents'] = CustomUser.objects.filter(role=CustomUser.Role.AGENT).count()
        ctx['role_choices'] = CustomUser.Role.choices
        ctx['filter_role'] = self.request.GET.get('role', '')
        ctx['filter_statut'] = self.request.GET.get('statut', '')
        return ctx


class AgentCreateView(ChefRequiredMixin, CreateView):
    model = CustomUser
    form_class = AgentCreationForm
    template_name = 'core/agents/form.html'
    success_url = reverse_lazy('core:agent_liste')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre'] = "Créer un compte utilisateur"
        ctx['action'] = "Créer le compte"
        return ctx

    def form_valid(self, form):
        user = form.save()
        security_logger.warning(
            "USER_CREATED by=%s new_user=%s role=%s ip=%s",
            self.request.user.email, user.email, user.role,
            self.request.META.get('REMOTE_ADDR'),
        )
        messages.success(
            self.request,
            f"Compte créé avec succès pour {user.get_full_name()} ({user.email})."
        )
        return redirect(self.success_url)


class AgentUpdateView(ChefRequiredMixin, UpdateView):
    model = CustomUser
    form_class = AgentEditForm
    template_name = 'core/agents/form.html'
    success_url = reverse_lazy('core:agent_liste')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['titre'] = f"Modifier — {self.object.get_full_name()}"
        ctx['action'] = "Enregistrer les modifications"
        ctx['is_edit'] = True
        return ctx

    def form_valid(self, form):
        user = form.save()
        security_logger.warning(
            "USER_UPDATED by=%s target=%s role=%s ip=%s",
            self.request.user.email, user.email, user.role,
            self.request.META.get('REMOTE_ADDR'),
        )
        messages.success(
            self.request,
            f"Compte de {user.get_full_name()} mis à jour."
        )
        return redirect(self.success_url)


def agent_toggle_active(request, pk):
    """Active ou désactive un compte utilisateur (Chef uniquement, POST)."""
    if not request.user.is_authenticated or not request.user.is_chef:
        raise Http404
    if request.method != 'POST':
        return redirect('core:agent_liste')

    user = get_object_or_404(CustomUser, pk=pk)

    # Empêcher le chef de se désactiver lui-même
    if user == request.user:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect('core:agent_liste')

    user.is_active = not user.is_active
    user.save(update_fields=['is_active'])

    action = "activé" if user.is_active else "désactivé"
    security_logger.warning(
        "USER_TOGGLE_ACTIVE by=%s target=%s active=%s ip=%s",
        request.user.email, user.email, user.is_active,
        request.META.get('REMOTE_ADDR'),
    )
    messages.success(request, f"Compte de {user.get_full_name()} {action}.")
    return redirect('core:agent_liste')


# ─── Configuration email ─────────────────────────────────────────────────────

class EmailConfigView(ChefRequiredMixin, UpdateView):
    model = EmailConfig
    form_class = EmailConfigForm
    template_name = 'core/email_config.html'
    success_url = reverse_lazy('core:email_config')

    def get_object(self, queryset=None):
        return EmailConfig.get_solo()

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Configuration email enregistrée et appliquée.")
        return redirect(self.success_url)

    def form_invalid(self, form):
        messages.error(self.request, "Erreur dans le formulaire. Vérifiez les champs.")
        return super().form_invalid(form)


@login_required
def email_test(request):
    """Envoie un email de test au compte connecté (Chef uniquement)."""
    if not request.user.is_chef:
        raise Http404
    if request.method != 'POST':
        return redirect('core:email_config')

    destinataire = request.user.email
    try:
        send_mail(
            subject="[Atlas Énergies] Test de configuration email",
            message=(
                "Bonjour,\n\n"
                "Cet email confirme que la configuration SMTP est opérationnelle.\n\n"
                "— Atlas Énergies"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[destinataire],
            fail_silently=False,
        )
        messages.success(
            request,
            f"Email de test envoyé à {destinataire}. Vérifiez votre boîte de réception."
        )
    except Exception as exc:
        messages.error(
            request,
            f"Échec de l'envoi : {exc}"
        )

    return redirect('core:email_config')


# ─── Handlers d'erreur ────────────────────────────────────────────────────────

def handler403(request, exception=None):
    return render(request, 'errors/403.html', status=403)


def handler404(request, exception=None):
    return render(request, 'errors/404.html', status=404)


def handler500(request):
    return render(request, 'errors/500.html', status=500)
