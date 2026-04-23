"""
Formulaires de gestion des utilisateurs (réservés au Chef d'Agence).
"""
from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import CustomUser, EmailConfig


class AgentCreationForm(forms.ModelForm):
    """Formulaire de création d'un compte utilisateur (agent ou chef)."""

    password1 = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input-modern input input-bordered w-full',
            'placeholder': 'Minimum 8 caractères',
            'autocomplete': 'new-password',
        }),
    )
    password2 = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input-modern input input-bordered w-full',
            'placeholder': 'Répétez le mot de passe',
            'autocomplete': 'new-password',
        }),
    )

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'role']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input-modern input input-bordered w-full',
                'placeholder': 'Prénom',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input-modern input input-bordered w-full',
                'placeholder': 'Nom de famille',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input-modern input input-bordered w-full',
                'placeholder': 'adresse@email.com',
                'autocomplete': 'off',
            }),
            'role': forms.Select(attrs={
                'class': 'form-input-modern select select-bordered w-full',
            }),
        }

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1', '')
        p2 = self.cleaned_data.get('password2', '')
        if p1 and p2 and p1 != p2:
            raise ValidationError("Les mots de passe ne correspondent pas.")
        return p2

    def clean_password1(self):
        password = self.cleaned_data.get('password1', '')
        if password:
            validate_password(password)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class AgentEditForm(forms.ModelForm):
    """Formulaire de modification d'un compte existant (sans changement de mot de passe)."""

    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'role', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-input-modern input input-bordered w-full',
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-input-modern input input-bordered w-full',
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input-modern input input-bordered w-full',
            }),
            'role': forms.Select(attrs={
                'class': 'form-input-modern select select-bordered w-full',
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'checkbox checkbox-sm',
            }),
        }
        labels = {
            'is_active': 'Compte actif',
        }


CSS_INPUT = 'form-input-modern input input-bordered w-full'
CSS_SELECT = 'form-input-modern select select-bordered w-full'


class EmailConfigForm(forms.ModelForm):
    """Formulaire de configuration SMTP (réservé au Chef d'Agence)."""

    email_host_password = forms.CharField(
        label="Mot de passe / App Password",
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': CSS_INPUT,
            'placeholder': 'Laisser vide pour ne pas modifier',
            'autocomplete': 'new-password',
        }),
    )

    class Meta:
        model = EmailConfig
        fields = [
            'email_host',
            'email_port',
            'email_use_ssl',
            'email_use_tls',
            'email_host_user',
            'email_host_password',
            'default_from_email',
        ]
        widgets = {
            'email_host': forms.TextInput(attrs={
                'class': CSS_INPUT,
                'placeholder': 'smtp.gmail.com',
            }),
            'email_port': forms.NumberInput(attrs={
                'class': CSS_INPUT,
                'placeholder': '465',
            }),
            'email_use_ssl': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-sm'}),
            'email_use_tls': forms.CheckboxInput(attrs={'class': 'checkbox checkbox-sm'}),
            'email_host_user': forms.EmailInput(attrs={
                'class': CSS_INPUT,
                'placeholder': 'expediteur@gmail.com',
                'autocomplete': 'off',
            }),
            'default_from_email': forms.TextInput(attrs={
                'class': CSS_INPUT,
                'placeholder': 'Atlas Énergies <noreply@atlas-energies.ci>',
            }),
        }

    def clean(self):
        cleaned = super().clean()
        ssl = cleaned.get('email_use_ssl')
        tls = cleaned.get('email_use_tls')
        if ssl and tls:
            raise forms.ValidationError(
                "SSL et TLS ne peuvent pas être activés en même temps. "
                "Choisissez SSL (port 465) OU TLS (port 587)."
            )
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        pwd = self.cleaned_data.get('email_host_password', '').strip()
        if not pwd:
            # Conserver l'ancien mot de passe si le champ est laissé vide
            try:
                instance.email_host_password = EmailConfig.objects.get(pk=1).email_host_password
            except EmailConfig.DoesNotExist:
                pass
        if commit:
            instance.save()
        return instance
