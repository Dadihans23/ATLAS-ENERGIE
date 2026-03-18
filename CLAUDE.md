# CLAUDE.md — Atlas Énergies / GestionProjetAgence

## Contexte du projet
Application de gestion interne de projets et dépenses pour l'agence **Atlas Énergies** (Côte d'Ivoire).
Nom logiciel : **GestionProjetAgence**
Répertoire : `C:\Users\HP I7\Desktop\git_project\PETROCI`

## Stack technique
- **Python** 3.12 (venv dans `PETROCI/venv/`)
- **Django** 5.1.4
- **Base de données** : SQLite
- **Frontend** : Tailwind CSS CDN + DaisyUI 4 + CSS custom (glassmorphism/neumorphisme)
- **Pas de HTMX** — HTML classique + JavaScript vanilla uniquement
- **Langue** : Français partout (labels, messages, admin)

## Commandes utiles
```bash
# Activer le venv (PowerShell)
.\venv\Scripts\Activate.ps1

# Lancer le serveur
python manage.py runserver 0.0.0.0:8000

# Migrations
python manage.py makemigrations
python manage.py migrate

# Créer un superuser
python manage.py createsuperuser
```

## Settings
- Module : `atlas_energies.settings.dev`
- Fichier `.env` à la racine (voir `.env.example`)
- Split : `settings/base.py`, `settings/dev.py`, `settings/prod.py`

## Architecture des apps
```
core/        → CustomUser (email comme username), mixins, templatetags, media protégée
projets/     → Modèle Projet (budgets par ligne)
depenses/    → DepenseExploitation + DepenseFraisGeneraux + signaux budget + exports
dashboard/   → Vues tableau de bord (chef vs agent) + historique audit
```

## Modèles clés
- `core.CustomUser` : AUTH_USER_MODEL, rôles `chef` / `agent`
- `projets.Projet` : 5 lignes budgétaires (étude, matériel, logistique, sous-traitance, frais mission)
- `depenses.DepenseExploitation` : déduit du budget projet via signaux, numéro auto `EXP-YYYY-XXXXX`
- `depenses.DepenseFraisGeneraux` : ne touche pas le budget projet, numéro auto `FG-YYYY-XXXXX`

## Règles métier importantes
- **Chef d'Agence** : CRUD complet projets + toutes dépenses + dashboard global + audit
- **Agent** : création de dépenses uniquement (pas de modif/suppression)
- Les budgets sont en **XOF** ; EUR et USD convertis via taux stocké sur la dépense
- `django-simple-history` trace toutes les modifications sur Projet, DepenseExploitation, DepenseFraisGeneraux

## Design System
- Palette principale : **vert Atlas** (`#2d7a2f`, `#276228`) + blanc — couleur du logo entreprise
- Pages auth (login/logout/reset) : split 50/50 — panneau gauche blanc (formulaire) + panneau droit vert foncé (branding)
- Classes CSS custom dans `base.html` : `.glass-card`, `.kpi-card`, `.btn-glass-primary`, `.btn-glass-secondary`, `.modern-table`, `.progress-modern`
- Animations : `.animate-in`, `.delay-1` à `.delay-4`
- Sidebar fixe à gauche (268px), topbar sticky glassmorphism
- Fond app : `#f1f5f9`, sidebar : `#0f172a`

## Email
- SMTP Gmail (port 465, SSL) — credentials dans `.env`
- `EMAIL_HOST_USER` : Dadihans06@gmail.com
- Templates HTML professionnels dans `templates/account/email/`
- `ACCOUNT_EMAIL_HTML = True` activé

## Ce qui est fait ✅
- [x] Structure complète du projet + requirements.txt + .env.example
- [x] Modèles + signaux budget + numérotation auto
- [x] CustomUser + groupes + permissions
- [x] admin.py complet
- [x] forms.py (ProjetForm, DepenseExploitationForm, DepenseFraisGenerauxForm)
- [x] views.py (projets, depenses, dashboard)
- [x] urls.py (toutes les apps)
- [x] base.html — design glassmorphism/neumorphisme complet (palette verte)
- [x] dashboard/chef.html + dashboard/agent.html (palette verte)
- [x] Export CSV + Excel (openpyxl) pour les deux types de dépenses
- [x] Page d'audit/historique (django-simple-history)
- [x] Pages d'erreur 403 / 404 / 500
- [x] Protection média (serve_media view, login requis)
- [x] core/templatetags/currency_tags.py (filtres `xof`, `pct`)
- [x] HTMX retiré → HTML classique + JS vanilla
- [x] Templates projets : liste, detail, form (créer/modifier), confirm_delete
- [x] Templates dépenses : liste_exploitation, liste_frais_generaux, forms, confirm_delete
- [x] account/login.html — design split gauche/droite, palette verte
- [x] account/logout.html — design split gauche/droite, palette verte
- [x] Forgot password complet (4 templates allauth) — design cohérent
- [x] Email HTML professionnel pour reset password (avec bouton CTA, fallback texte)
- [x] SMTP Gmail configuré dans .env (port 465, SSL)
- [x] Migration 0002_update_site — corrige "example.com" → "127.0.0.1:8000 / Atlas Énergies"

## Ce qui reste à faire 🔲
- [ ] Vérification cohérence views.py / templates (supprimer restes HX-Redirect)
- [ ] Test end-to-end complet (login → projet → dépense → export → reset password)
- [ ] Déploiement production (settings/prod.py, HTTPS, domaine réel dans Site#1)

## Préférences développeur
- Pas de HTMX (retiré sur demande)
- Pas de React/Vue
- Toujours utiliser le venv Python 3.12
- Labels et messages en français
- DecimalField pour tous les montants
- CBV (Class-Based Views) dans les views
- Pages auth : toujours utiliser le layout split 50/50 (blanc + vert foncé)
