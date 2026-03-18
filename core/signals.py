"""
Signaux core – création automatique des groupes et affectation des permissions
lors de la sauvegarde d'un utilisateur.
"""
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save, post_migrate
from django.dispatch import receiver

from core.models import CustomUser


# ── Création des groupes au démarrage ─────────────────────────────────────────

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    """
    Crée les groupes 'ChefAgence' et 'Agent' avec leurs permissions
    après chaque migrate.
    """
    chef_group, _ = Group.objects.get_or_create(name='ChefAgence')
    agent_group, _ = Group.objects.get_or_create(name='Agent')

    # Permissions pour les agents : seulement ajouter des dépenses
    agent_permissions_codenames = [
        'add_depenseexploitation',
        'add_depensefraisgeneraux',
        'view_depenseexploitation',
        'view_depensefraisgeneraux',
        'view_projet',
    ]

    for codename in agent_permissions_codenames:
        try:
            perm = Permission.objects.get(codename=codename)
            agent_group.permissions.add(perm)
        except Permission.DoesNotExist:
            pass  # Les permissions seront disponibles après makemigrations

    # Le ChefAgence reçoit toutes les permissions via is_staff ou manuellement
    # (géré dans l'admin et les vues via @user_passes_test)


# ── Affectation automatique du groupe selon le rôle ───────────────────────────

@receiver(post_save, sender=CustomUser)
def assign_user_to_group(sender, instance: CustomUser, created: bool, **kwargs):
    """
    Ajoute l'utilisateur au groupe correspondant à son rôle.
    """
    chef_group, _ = Group.objects.get_or_create(name='ChefAgence')
    agent_group, _ = Group.objects.get_or_create(name='Agent')

    # Retirer des deux groupes d'abord
    instance.groups.remove(chef_group)
    instance.groups.remove(agent_group)

    # Assigner selon le rôle
    if instance.role == CustomUser.Role.CHEF:
        instance.groups.add(chef_group)
        # Le chef a accès à l'admin Django
        if not instance.is_staff:
            CustomUser.objects.filter(pk=instance.pk).update(is_staff=True)
    else:
        instance.groups.add(agent_group)
