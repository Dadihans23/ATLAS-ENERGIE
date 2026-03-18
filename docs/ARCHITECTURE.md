# Architecture — GestionProjetAgence

## Vue d'ensemble

```
PETROCI/
├── atlas_energies/          # Projet Django principal
│   ├── settings/
│   │   ├── base.py          # Settings partagés (email, allauth, DB, media...)
│   │   ├── dev.py           # Dev : debug toolbar, SQL logs
│   │   └── prod.py          # Prod : HTTPS, sécurité renforcée
│   ├── urls.py              # Routage racine + serve_media + error handlers
│   └── wsgi.py
│
├── core/                    # App transversale
│   ├── models.py            # CustomUser (email=username, rôle chef/agent)
│   ├── mixins.py            # ChefRequiredMixin (UserPassesTestMixin)
│   ├── views.py             # serve_media (login requis), handler403/404/500
│   ├── templatetags/
│   │   └── currency_tags.py # Filtres : |xof  |pct
│   └── migrations/
│       ├── 0001_initial.py
│       └── 0002_update_site.py  # Corrige example.com → 127.0.0.1:8000
│
├── projets/                 # Gestion des projets
│   ├── models.py            # Projet : 5 lignes budgétaires + champs depense_*
│   ├── views.py             # CBV : List, Detail, Create, Update, Delete
│   ├── forms.py             # ProjetForm
│   └── urls.py
│
├── depenses/                # Gestion des dépenses
│   ├── models.py            # DepenseExploitation + DepenseFraisGeneraux
│   ├── signals.py           # pre_save / post_save / post_delete → budget F()
│   ├── forms.py             # DepenseExploitationForm, DepenseFraisGenerauxForm
│   ├── exports.py           # CSV (UTF-8 BOM) + Excel (openpyxl, styled)
│   └── urls.py
│
├── dashboard/               # Tableaux de bord
│   ├── views.py             # accueil() → chef ou agent | historique() audit
│   └── urls.py
│
├── templates/
│   ├── base.html            # Layout principal : sidebar + topbar + flash messages
│   ├── account/             # Pages auth (allauth overrides)
│   │   ├── login.html
│   │   ├── logout.html
│   │   ├── password_reset.html
│   │   ├── password_reset_done.html
│   │   ├── password_reset_from_key.html
│   │   ├── password_reset_from_key_done.html
│   │   └── email/
│   │       ├── password_reset_key_subject.txt
│   │       ├── password_reset_key_message.txt   # fallback
│   │       └── password_reset_key_message.html  # email HTML pro
│   ├── dashboard/
│   │   ├── chef.html
│   │   ├── agent.html
│   │   ├── historique.html
│   │   └── _audit_table.html
│   ├── projets/
│   │   ├── liste.html
│   │   ├── detail.html
│   │   ├── form.html
│   │   └── confirm_delete.html
│   ├── depenses/
│   │   ├── liste_exploitation.html
│   │   ├── liste_frais_generaux.html
│   │   ├── form_exploitation.html
│   │   ├── form_frais_generaux.html
│   │   └── confirm_delete.html
│   └── errors/
│       ├── 403.html
│       ├── 404.html
│       └── 500.html
│
├── static/
│   └── img/                 # Logo Atlas Énergies
├── media/                   # Fichiers uploadés (protégés, login requis)
├── venv/                    # Environnement virtuel Python 3.12
├── db.sqlite3
├── manage.py
├── requirements.txt
├── .env                     # Variables sensibles (secret key, SMTP, DB...)
├── .env.example
└── CLAUDE.md
```

---

## Flux de données — Budget

```
DepenseExploitation.save()
        │
        ▼
   signals.py (pre_save)
   → stocke _old_instance
        │
        ▼
   signals.py (post_save)
   → Projet.objects.filter(pk=...).update(
         depense_LIGNE=F('depense_LIGNE') + delta_xof
     )
        │
        ▼
   Projet.budget_restant_LIGNE  (property)
   = budget_LIGNE - depense_LIGNE
```

- `BUDGET_FIELD_MAP` dans `depenses/models.py` mappe `ligne_budgetaire` → champ `depense_*` du Projet
- Toutes les mises à jour budget utilisent `F()` pour l'atomicité (thread-safe)
- `montant_xof` est calculé et stocké à la sauvegarde (EUR×655.957, USD×600)

---

## Authentification & Permissions

```
django-allauth (email uniquement, pas de username)
        │
        ├── LOGIN_URL = /comptes/login/
        ├── LOGIN_REDIRECT_URL = /tableau-de-bord/
        └── LOGOUT_REDIRECT_URL = /comptes/login/

CustomUser.role
        ├── 'chef'  → ChefRequiredMixin → accès total
        └── 'agent' → accès création dépenses uniquement
```

- `ChefRequiredMixin` : `UserPassesTestMixin` → `test_func` vérifie `user.role == 'chef'`
- Agents redirigés vers 403 sur toute vue Chef
- `django-guardian` disponible pour permissions objet-niveau si besoin futur

---

## URLs principales

| URL | Vue | Accès |
|-----|-----|-------|
| `/` | redirect → `/tableau-de-bord/` | Tous |
| `/tableau-de-bord/` | `dashboard.accueil` | Authentifié |
| `/tableau-de-bord/historique/` | `dashboard.historique` | Chef |
| `/projets/` | `ProjetListView` | Chef |
| `/projets/<pk>/` | `ProjetDetailView` | Chef |
| `/projets/nouveau/` | `ProjetCreateView` | Chef |
| `/projets/<pk>/modifier/` | `ProjetUpdateView` | Chef |
| `/projets/<pk>/supprimer/` | `ProjetDeleteView` | Chef |
| `/depenses/exploitation/` | `DepExploitationListView` | Chef |
| `/depenses/exploitation/nouvelle/` | `DepExploitationCreateView` | Tous |
| `/depenses/frais-generaux/` | `DepFraisGenenrauxListView` | Chef |
| `/depenses/frais-generaux/nouveau/` | `DepFraisGenerauxCreateView` | Tous |
| `/depenses/exploitation/export/csv/` | `export_exploitation_csv` | Chef |
| `/depenses/exploitation/export/excel/` | `export_exploitation_excel` | Chef |
| `/comptes/login/` | allauth login | Anonyme |
| `/comptes/logout/` | allauth logout | Authentifié |
| `/comptes/password/reset/` | allauth reset | Anonyme |
| `/media/<path>` | `serve_media` | Authentifié |
