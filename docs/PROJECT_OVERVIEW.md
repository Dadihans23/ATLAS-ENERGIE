# Project Overview — GestionProjetAgence

> Ce fichier est réutilisable comme référence pour tout projet similaire de gestion interne.

---

## Résumé du projet

| Champ | Valeur |
|-------|--------|
| **Nom** | GestionProjetAgence |
| **Client** | Atlas Énergies |
| **Pays** | Côte d'Ivoire |
| **Type** | Application web interne (intranet) |
| **Objectif** | Suivre les projets, budgets et dépenses en temps réel |
| **Devise** | XOF (Franc CFA) avec conversion EUR et USD |
| **Démarré** | Mars 2026 |

---

## Problème résolu

Atlas Énergies gérait ses projets et dépenses sur Excel/papier, sans visibilité centralisée sur :
- L'état d'avancement budgétaire par projet
- Les dépenses d'exploitation vs frais généraux
- L'historique des modifications (audit trail)
- Les droits d'accès par rôle (chef vs agent de terrain)

---

## Fonctionnalités principales

### Gestion de projets
- Créer / modifier / supprimer des projets
- 5 lignes budgétaires par projet : Étude, Matériel, Logistique, Sous-traitance, Frais de mission
- Suivi en temps réel : budget alloué vs dépensé vs restant
- Alerte visuelle si dépassement de budget
- Barre de progression par ligne budgétaire

### Gestion des dépenses
**Dépenses d'exploitation** (`EXP-YYYY-XXXXX`)
- Liées à un projet et une ligne budgétaire
- Déduisent automatiquement le budget du projet
- Pièces justificatives jointes (PDF, images)

**Frais généraux** (`FG-YYYY-XXXXX`)
- Non liés à un projet (loyer, salaires, etc.)
- N'impactent pas les budgets projets

### Exports
- CSV (UTF-8 BOM, séparateur `;`, compatible Excel FR)
- Excel (.xlsx) avec headers stylés, totaux, colonnes gelées

### Audit / Historique
- Toutes les modifications tracées via `django-simple-history`
- Vue historique réservée au Chef d'Agence
- Affiche : qui a modifié quoi et quand

### Authentification
- Login par email (pas de username)
- Mot de passe oublié avec email de réinitialisation
- 2 rôles : Chef d'Agence / Agent

---

## Stack technique recommandée (projet similaire)

```
Backend      : Django 5.1+ / Python 3.12
Auth         : django-allauth (email login, reset password)
Permissions  : django-guardian (objet-niveau si besoin)
Audit        : django-simple-history
DB           : SQLite (dev) → PostgreSQL (prod)
Frontend     : Tailwind CSS CDN + DaisyUI 4 CDN
JS           : Vanilla JS uniquement (pas de React/Vue/HTMX)
Emails       : SMTP Gmail (port 465, SSL) ou SendGrid en prod
Exports      : openpyxl (Excel) + csv stdlib (CSV)
Media        : Servie par Django avec protection login (développement)
Static prod  : WhiteNoise
```

### Packages Python clés
```
Django==5.1.4
django-allauth==0.63.6
django-guardian
django-simple-history
django-environ
django-cleanup
openpyxl
whitenoise
widget_tweaks
django-debug-toolbar (dev uniquement)
```

---

## Modèle de données — Schéma simplifié

```
CustomUser
├── email (USERNAME_FIELD)
├── role: chef | agent
└── ...champs profil

Projet
├── nom, client, description
├── date_debut, date_fin_prevue
├── budget_etude, budget_materiel, budget_logistique
├── budget_sous_traitance, budget_frais_mission
├── depense_etude, depense_materiel, ...  ← mis à jour par signaux
└── statut: en_cours | termine | suspendu

DepenseExploitation
├── projet FK → Projet
├── ligne_budgetaire: etude | materiel | logistique | sous_traitance | frais_mission
├── montant + devise (XOF/EUR/USD)
├── montant_xof (calculé et stocké)
├── taux_change_utilise
├── numero_saisie: EXP-YYYY-XXXXX (auto)
├── justificatif (fichier)
└── created_by FK → CustomUser

DepenseFraisGeneraux
├── categorie, description
├── montant + devise
├── montant_xof
├── numero_saisie: FG-YYYY-XXXXX (auto)
├── justificatif (fichier)
└── created_by FK → CustomUser
```

---

## Patterns réutilisables

### Numérotation automatique
```python
# Dans models.py — pre_save signal
last = Model.objects.filter(
    numero_saisie__startswith=f'PREFIX-{year}-'
).order_by('-numero_saisie').first()
next_num = int(last.numero_saisie.split('-')[-1]) + 1 if last else 1
instance.numero_saisie = f'PREFIX-{year}-{next_num:05d}'
```

### Mise à jour budget atomique
```python
# Dans signals.py — post_save
from django.db.models import F
Projet.objects.filter(pk=projet_pk).update(
    depense_LIGNE=F('depense_LIGNE') + delta_xof
)
```

### Protection des fichiers media (login requis)
```python
# Dans core/views.py
@login_required
def serve_media(request, path):
    path = os.path.normpath(path)  # protection directory traversal
    full_path = os.path.join(settings.MEDIA_ROOT, path)
    return FileResponse(open(full_path, 'rb'))
```

### Mixin rôle Chef
```python
class ChefRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.role == 'chef'
    def handle_no_permission(self):
        raise PermissionDenied
```

---

## Variables d'environnement nécessaires

```env
SECRET_KEY=
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=sqlite:///db.sqlite3

# Email SMTP
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_SSL=True
EMAIL_USE_TLS=False
DEFAULT_FROM_EMAIL=NomApp <email@domaine.com>

# Taux de change (ajuster selon marché)
TAUX_EUR_XOF=655.957
TAUX_USD_XOF=605.00

# Media / Static
MEDIA_ROOT=media
MEDIA_URL=/media/
STATIC_ROOT=staticfiles
STATIC_URL=/static/
```

---

## Checklist déploiement production

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` changée (longue, aléatoire)
- [ ] `ALLOWED_HOSTS` = domaine réel
- [ ] PostgreSQL configuré (remplacer SQLite)
- [ ] `python manage.py collectstatic`
- [ ] WhiteNoise activé pour les statics
- [ ] Serveur media sécurisé (Nginx X-Accel-Redirect ou S3)
- [ ] HTTPS activé (certificat SSL)
- [ ] Mettre à jour `django_site` : domaine = domaine réel
- [ ] `ACCOUNT_EMAIL_VERIFICATION = 'mandatory'` si inscription ouverte
- [ ] Variables `.env` injectées via système secrets (pas commitées)
- [ ] Sauvegardes base de données automatisées
