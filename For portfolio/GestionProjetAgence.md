# GestionProjetAgence — Atlas Énergies

## Informations projet

| Champ | Détail |
|-------|--------|
| **Nom du projet** | GestionProjetAgence |
| **Client** | Atlas Énergies |
| **Secteur** | Énergie / Ingénierie |
| **Pays** | Côte d'Ivoire 🇨🇮 |
| **Type** | Application web interne (intranet) |
| **Statut** | En développement |
| **Année** | 2026 |

---

## Objectif

Remplacer la gestion manuelle (Excel, papier) des projets et dépenses d'une agence d'ingénierie par une application web centralisée.

L'application permet au **Chef d'Agence** de piloter les budgets en temps réel et aux **Agents de terrain** de saisir leurs dépenses depuis n'importe quel poste.

---

## Enjeux

- **Financier** : éviter les dépassements de budget non détectés sur les projets clients
- **Traçabilité** : avoir un audit complet de chaque modification (qui a changé quoi, quand)
- **Accessibilité** : permettre aux agents terrain de saisir sans formation technique
- **Sécurité** : cloisonner les accès (chef vs agent) et protéger les documents justificatifs
- **Export** : produire des rapports CSV/Excel pour la comptabilité externe

---

## Fonctionnalités clés

- Gestion de projets avec **5 lignes budgétaires** (étude, matériel, logistique, sous-traitance, frais mission)
- Suivi budgétaire **en temps réel** avec barre de progression et alerte dépassement
- **2 types de dépenses** : exploitation (impact budget projet) et frais généraux (dépenses courantes)
- Numérotation automatique : `EXP-2026-00001` / `FG-2026-00001`
- **Multi-devise** : saisie en XOF, EUR ou USD — conversion automatique au taux du jour
- Export **CSV** et **Excel** (.xlsx) avec totaux et mise en forme
- **Historique complet** de toutes les modifications (audit trail)
- **Reset password** par email avec template HTML professionnel
- Protection des pièces jointes (accès authentifié uniquement)

---

## Stack technique

### Backend
| Technologie | Version | Usage |
|-------------|---------|-------|
| Python | 3.12 | Langage principal |
| Django | 5.1.4 | Framework web |
| SQLite | — | Base de données (dev) |
| django-allauth | 0.63.6 | Authentification par email |
| django-simple-history | 3.7.0 | Audit trail automatique |
| django-cleanup | 8.1.0 | Nettoyage fichiers orphelins |
| openpyxl | 3.1.5 | Export Excel |
| django-environ | 0.11.2 | Variables d'environnement |
| whitenoise | 6.7.0 | Fichiers statiques production |

### Frontend
| Technologie | Usage |
|-------------|-------|
| Tailwind CSS (CDN) | Utilitaires CSS |
| DaisyUI 4 (CDN) | Composants UI |
| CSS custom | Glassmorphisme / Neumorphisme |
| JavaScript Vanilla | Interactions (aucun framework JS) |
| Google Fonts — Inter | Typographie |

### Outils & pratiques
- Settings splitté `base / dev / prod` avec variables d'environnement
- Signaux Django atomiques (`transaction.atomic` + `select_for_update`) pour l'intégrité budgétaire
- Rate limiting sur les endpoints d'authentification
- Headers de sécurité : CSP, Permissions-Policy, SameSite Strict
- Split requirements `base.txt / dev.txt`

---

## Architecture (vue simplifiée)

```
┌─────────────────────────────────────────────┐
│              Django Application              │
│                                             │
│  core/       → CustomUser, auth, media      │
│  projets/    → CRUD Projets + budgets        │
│  depenses/   → Dépenses + signaux budget    │
│  dashboard/  → KPIs Chef / Agent            │
│                                             │
│  Signals : DepenseExploitation.save()       │
│    → transaction.atomic()                  │
│    → Projet.depense_LIGNE += montant_xof   │
└─────────────────────────────────────────────┘
         │                    │
    SQLite DB           Media files
  (→ PostgreSQL        (protégés login
     en prod)           requis)
```

**Modèle de permissions :**
```
Chef d'Agence → CRUD complet (projets + dépenses + utilisateurs + audit)
Agent         → Création de dépenses uniquement
```

---

## Design

- **Identité visuelle** : vert Atlas (`#2d7a2f`) — couleur du logo client
- **Layout auth** : split 50/50 (formulaire blanc | panneau branding vert foncé)
- **App interne** : sidebar fixe, topbar glassmorphism, cards neumorphiques
- **Responsive** : adapté desktop et tablette

---

## Ce que ce projet démontre

- Conception d'une **application métier complète** de bout en bout
- Maîtrise de **Django avancé** : signaux, CBV, permissions, middleware custom
- Intégration de **bonnes pratiques sécurité** (audit de sécurité réalisé, 20+ fixes appliqués)
- Capacité à livrer un **design moderne et cohérent** sans framework JS
- Gestion de **contraintes métier complexes** (multi-devise, atomicité budget, audit trail)
