"""
Managers personnalisés pour le modèle CustomUser.
"""
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    """
    Manager utilisateur avec email comme identifiant principal.
    """

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        if not email:
            raise ValueError(_("L'adresse email est obligatoire."))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'chef')

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_("Le superutilisateur doit avoir is_staff=True."))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_("Le superutilisateur doit avoir is_superuser=True."))

        return self.create_user(email, password, **extra_fields)

    def chefs_agence(self):
        return self.filter(role='chef', is_active=True)

    def agents(self):
        return self.filter(role='agent', is_active=True)
