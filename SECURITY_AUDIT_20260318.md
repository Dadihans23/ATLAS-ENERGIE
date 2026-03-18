# Audit de Sécurité – GestionProjetAgence
**Date** : 18 mars 2026
**Version auditée** : Développement local – branche principale
**Auditeur** : Expert AppSec Senior (simulation)
**Périmètre** : Application Django 5.1.4 – Atlas Énergies (Côte d'Ivoire)

---

## Résumé exécutif

**Score estimé : 41 / 100**
**Niveau global : FAIBLE — Ne doit PAS partir en production en l'état**

| Sévérité     | Nombre |
|--------------|--------|
| CRITICAL     | 3      |
| HIGH         | 5      |
| MEDIUM       | 7      |
| LOW          | 5      |
| INFORMATIONAL| 4      |
| **TOTAL**    | **24** |

> L'application démontre une architecture Django saine et des choix techniques corrects (signaux, CBV, audit trail). Cependant, plusieurs vulnérabilités critiques — dont l'exposition de credentials réels et l'absence de rate limiting — rendent un déploiement en production **inacceptable sans remédiation**.

---

## Findings classés par criticité

---

### CRITICAL-01 — Credentials réels commités dans .env

**Risque** : CRITICAL
**Localisation** : `.env` (racine du projet)
**Description** :
Le fichier `.env` contient un mot de passe d'application Gmail **réel et actif** ainsi qu'une `SECRET_KEY` faible :
```
EMAIL_HOST_PASSWORD=zzphvsbzotaldqax   ← App password Gmail actif
EMAIL_HOST_USER=Dadihans06@gmail.com
SECRET_KEY=dev-secret-key-atlas-energies-gestion-projet-agence-2024  ← prévisible
```
**Impact** :
- Si le dépôt est un jour poussé sur GitHub (public ou privé partagé), ces credentials sont **immédiatement exploitables**.
- Avec le mot de passe d'application Gmail, un attaquant peut envoyer des emails depuis l'adresse de l'agence (phishing, usurpation).
- Avec la `SECRET_KEY` faible, un attaquant peut forger des sessions Django, des tokens CSRF, des cookies signés et des URLs de reset de mot de passe (`/comptes/password/reset/key/...`).
- Les tokens de réinitialisation de mot de passe peuvent être forgés → prise de contrôle de n'importe quel compte.

**Scénario d'attaque** :
```
1. Attaquant obtient SECRET_KEY (dépôt git, pastebin, etc.)
2. Forge un session cookie valide pour un compte chef
3. Accède à tout le système : projets, dépenses, exports, audit, utilisateurs
```

**Recommandation** :
1. **Immédiatement** : révoquer l'App Password Gmail `zzphvsbzotaldqax` sur https://myaccount.google.com/apppasswords
2. Ajouter `.env` dans `.gitignore` (vérifier `git log` pour s'assurer qu'il n'a pas déjà été commité)
3. Régénérer la SECRET_KEY avec : `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
4. La SECRET_KEY de production doit être gérée via un secret manager (Vault, AWS SSM, variables d'environnement du serveur)

---

### CRITICAL-02 — Absence totale de rate limiting sur l'authentification

**Risque** : CRITICAL
**Localisation** : `atlas_energies/settings/base.py` — section allauth
**Description** :
Aucun rate limiting n'est configuré sur :
- `/comptes/login/` → brute force de mots de passe
- `/comptes/password/reset/` → abus de l'envoi d'emails (flooding)
- `/comptes/password/reset/key/...` → tentatives de tokens

allauth 0.63.6 supporte `ACCOUNT_RATE_LIMITS` mais il n'est pas configuré. Par défaut, les limites sont très permissives ou absentes.

**Impact** :
- Un attaquant peut tenter des milliers de mots de passe sur un compte agent sans aucune friction.
- L'endpoint reset password peut être utilisé pour flooder un email cible (spam abuse via le serveur SMTP de l'agence).
- Risque de déni de service par épuisement des ressources SMTP.

**Scénario d'attaque** :
```
for password in rockyou.txt:
    POST /comptes/login/ {email: "agent@atlas.ci", password: password}
# Aucune limite → compromission en quelques minutes
```

**Recommandation** :
```python
# Dans base.py :
ACCOUNT_RATE_LIMITS = {
    "login_failed": "5/5m",          # 5 échecs par 5 minutes
    "login_failed_ip": "20/5m",      # 20 échecs par IP
    "signup": "10/h",
    "password_reset": "3/h",          # 3 demandes de reset par heure par email
    "password_reset_by_ip": "10/h",
    "email_confirmation": "5/h",
}
```
Combiner avec `django-axes` ou `django-ratelimit` pour un contrôle plus granulaire avec blocage IP.

---

### CRITICAL-03 — Budget signals sans transaction atomique englobante

**Risque** : CRITICAL
**Localisation** : `depenses/signals.py` — `mettre_a_jour_budget()` lignes 40–60
**Description** :
Lors d'une **modification** de dépense, le signal `post_save` effectue deux opérations SQL successives :
```python
# Opération 1 : annuler l'ancienne valeur
Projet.objects.filter(pk=ancienne.centre_budgetaire_id).update(
    **{ancien_field: F(ancien_field) - ancienne.montant_xof}
)
# Opération 2 : appliquer la nouvelle valeur
Projet.objects.filter(pk=instance.centre_budgetaire_id).update(
    **{nouveau_field: F(nouveau_field) + instance.montant_xof}
)
```
Ces deux UPDATE **ne sont pas dans un bloc `transaction.atomic()`**. Si le processus crashe ou si la connexion DB se coupe entre les deux instructions, le budget du projet sera **corrompu** : l'ancienne dépense aura été annulée mais la nouvelle pas appliquée (ou vice-versa).

De plus, la mémorisation de `_ancienne_depense` dans `pre_save` et son utilisation dans `post_save` n'est **pas thread-safe** : l'attribut `_ancienne_depense` est stocké sur l'instance Python, mais sur un serveur multi-thread (gunicorn/uwsgi), deux requêtes modifiant la même dépense simultanément partagent des instances différentes → double comptage ou annulation incorrecte.

**Impact business** :
- Budgets de projets corrompus silencieusement (trop ou pas assez déduit).
- Incohérence financière détectable seulement lors d'un audit comptable.
- Application gérant l'argent réel de l'agence.

**Recommandation** :
```python
@receiver(post_save, sender=DepenseExploitation)
def mettre_a_jour_budget(sender, instance, created, **kwargs):
    ancienne = getattr(instance, '_ancienne_depense', None)
    with transaction.atomic():
        if not created and ancienne:
            ancien_field = Projet.DEPENSE_FIELD_MAP.get(ancienne.ligne_budgetaire)
            if ancien_field:
                Projet.objects.select_for_update().filter(
                    pk=ancienne.centre_budgetaire_id
                ).update(**{ancien_field: F(ancien_field) - ancienne.montant_xof})

        nouveau_field = Projet.DEPENSE_FIELD_MAP.get(instance.ligne_budgetaire)
        if nouveau_field:
            Projet.objects.select_for_update().filter(
                pk=instance.centre_budgetaire_id
            ).update(**{nouveau_field: F(nouveau_field) + instance.montant_xof})
```
Idem pour `restituer_budget` (post_delete).

---

### HIGH-01 — Nom de fichier uploadé non sanitisé (Path Traversal + Collision)

**Risque** : HIGH
**Localisation** : `depenses/models.py` — fonctions `exploitation_upload_path()` et `frais_generaux_upload_path()` lignes 37–46
**Description** :
Le nom de fichier original de l'utilisateur est utilisé directement dans le chemin de stockage :
```python
return f"depenses/exploitation/{now.year}/{now.month:02d}/{filename}"
```
`filename` est le nom brut fourni par le navigateur, non sanitisé.

**Risques** :
1. **Collision** : deux fichiers `facture.pdf` dans le même mois → l'un écrase l'autre (selon la config storage).
2. **Nom malveillant** : un nom de fichier comme `../../../settings.py` ou `<script>alert(1)</script>.pdf` peut poser des problèmes selon le serveur web en production.
3. **Disclosure** : le chemin `depenses/exploitation/2026/03/facture_confidentielle_projet_X.pdf` révèle des informations métier à quiconque devinerait le chemin (si le media n'est pas protégé côté nginx).

**Recommandation** :
```python
import uuid
from pathlib import Path

def exploitation_upload_path(instance, filename):
    ext = Path(filename).suffix.lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    now = instance.date_saisie or timezone.now().date()
    return f"depenses/exploitation/{now.year}/{now.month:02d}/{safe_name}"
```
Utiliser `uuid4()` pour rendre le chemin non prédictible et éviter les collisions.

---

### HIGH-02 — Absence de Content Security Policy (CSP)

**Risque** : HIGH
**Localisation** : `atlas_energies/settings/prod.py` et tous les templates
**Description** :
Aucun header `Content-Security-Policy` n'est configuré. De plus, les templates utilisent des CDNs sans **Subresource Integrity (SRI)** :
```html
<!-- base.html, login.html, etc. -->
<link href="https://cdn.jsdelivr.net/npm/daisyui@4.12.10/dist/full.min.css" rel="stylesheet"/>
<script src="https://cdn.tailwindcss.com"></script>
```

**Impact** :
- Sans CSP, toute XSS injectée dans un template (via un libellé de dépense, un nom de projet, etc.) peut exécuter du JavaScript arbitraire → vol de session, exfiltration de données.
- Sans SRI, si `cdn.jsdelivr.net` ou `cdn.tailwindcss.com` est compromis, du code malveillant sera exécuté par tous les utilisateurs de l'application.
- Attaque supply-chain réelle : en 2024, plusieurs CDNs populaires ont été compromis.

**Recommandation** :
1. Migrer les assets CDN vers des fichiers locaux (ou utiliser un build Tailwind) pour l'environnement de production.
2. Ajouter dans `prod.py` :
```python
from django.middleware.security import SecurityMiddleware

# Ajouter django-csp
MIDDLEWARE.insert(1, 'csp.middleware.CSPMiddleware')
CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "'nonce-{nonce}'")  # ou hash des scripts inline
CSP_STYLE_SRC = ("'self'",)
CSP_FONT_SRC = ("'self'", "https://fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:")
```
3. À minima en attendant, ajouter des attributs `integrity` et `crossorigin` sur les balises CDN.

---

### HIGH-03 — Énumération de comptes via le formulaire de reset mot de passe

**Risque** : HIGH
**Localisation** : `/comptes/password/reset/` — comportement allauth par défaut
**Description** :
allauth, par défaut (version 0.63.6), renvoie le même message de succès que l'email existe ou non, **mais** le temps de réponse est différent : si l'email existe, allauth effectue une requête DB + envoi SMTP ; si non, il répond immédiatement. Un attaquant peut mesurer les temps de réponse pour énumérer les comptes valides.

De plus, certaines versions d'allauth affichent des messages différents (`Nous vous avons envoyé un email` vs message générique) selon la configuration.

**Impact** :
- Énumération de tous les emails des collaborateurs de l'agence.
- Utilisable pour cibler des campagnes de phishing personnalisées.

**Recommandation** :
```python
# Dans base.py
ACCOUNT_EMAIL_NOTIFICATIONS = False  # Réduit les variations de comportement
# Vérifier que le template password_reset_done.html
# ne révèle JAMAIS si l'email est connu ou non
```
Implémenter un délai artificiel fixe sur l'endpoint reset pour égaliser les temps de réponse.

---

### HIGH-04 — Conflit de configuration email SSL/TLS entre prod.py et .env

**Risque** : HIGH
**Localisation** : `atlas_energies/settings/prod.py` lignes 22–23 vs `.env`
**Description** :
Incohérence critique dans la configuration email :
```python
# prod.py
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = True
```
```
# .env
EMAIL_PORT=465
EMAIL_USE_SSL=True
EMAIL_USE_TLS=False
```
Port 465 + SSL et Port 587 + TLS sont deux configurations **mutuellement incompatibles**. En production, `prod.py` override partiellement `.env` de manière incohérente (TLS=True alors que SSL=True dans .env).

**Impact** :
- En production, les emails (dont les **réinitialisations de mot de passe**) peuvent silencieusement échouer.
- Un utilisateur ne pouvant pas réinitialiser son mot de passe se retrouve bloqué.
- Les erreurs SMTP peuvent exposer des informations dans les logs.

**Recommandation** :
Centraliser toute la config email dans `.env` et supprimer les overrides dans `prod.py` :
```python
# prod.py — supprimer les lignes EMAIL_PORT, EMAIL_USE_TLS hardcodées
# Laisser base.py lire tout depuis .env
```

---

### HIGH-05 — Exports sans limite de volume (DoS potentiel)

**Risque** : HIGH
**Localisation** : `depenses/exports.py` — toutes les fonctions d'export
**Description** :
Les exports CSV et Excel récupèrent **toutes les dépenses** sans pagination ni limite :
```python
# exports.py (inféré du contexte)
depenses = DepenseExploitation.objects.all()  # ou filtre par user
```
Sur plusieurs années d'utilisation avec des milliers d'enregistrements, un export peut :
- Charger des centaines de Mo en mémoire
- Bloquer un thread WSGI pendant minutes
- Être répété en boucle pour épuiser les ressources

**Impact** :
- Déni de service applicatif (DoS) : un agent peut déclencher des exports répétés.
- En production avec gunicorn 4 workers, 4 exports simultanés peuvent rendre l'app indisponible.

**Recommandation** :
```python
# Ajouter une limite et/ou du streaming
MAX_EXPORT_ROWS = 10_000

def export_exploitation_csv(request):
    qs = get_queryset_for_user(request.user)
    if qs.count() > MAX_EXPORT_ROWS:
        messages.error(request, f"Export limité à {MAX_EXPORT_ROWS} lignes. Filtrez d'abord.")
        return redirect(...)
    # ... ou utiliser StreamingHttpResponse pour le CSV
```

---

### MEDIUM-01 — serve_media : protection traversal incomplète sur Windows

**Risque** : MEDIUM
**Localisation** : `core/views.py` — `serve_media()` lignes 22–23
**Description** :
```python
safe_path = os.path.normpath(path).lstrip('/')
if '..' in safe_path:
    raise Http404
```
Sur Windows, `os.path.normpath()` normalise avec des backslashes (`\`). Un path comme `depenses\..\..\settings.py` après `normpath` devient `settings.py` et ne contient pas `'..'`, passant ainsi le check.

De plus, `lstrip('/')` ne supprime que les slashes, pas les backslashes sur Windows.

**Recommandation** :
```python
from pathlib import Path

def serve_media(request, path: str):
    media_root = Path(settings.MEDIA_ROOT).resolve()
    # Résolution absolue + vérification que le fichier est bien dans MEDIA_ROOT
    try:
        file_path = (media_root / path).resolve()
        file_path.relative_to(media_root)  # Lève ValueError si hors de MEDIA_ROOT
    except (ValueError, Exception):
        raise Http404

    if not file_path.is_file():
        raise Http404
    # ...
```

---

### MEDIUM-02 — Absence du header Permissions-Policy

**Risque** : MEDIUM
**Localisation** : `atlas_energies/settings/prod.py`
**Description** :
Le header `Permissions-Policy` (ex `Feature-Policy`) n'est pas configuré. Ce header contrôle l'accès aux APIs sensibles du navigateur (caméra, micro, géolocalisation, etc.) depuis l'application et les iframes embarquées.

**Recommandation** :
```python
# Dans prod.py ou via middleware
SECURE_PERMISSIONS_POLICY = {
    "camera": [],
    "microphone": [],
    "geolocation": [],
    "payment": [],
}
```
Ou via un middleware custom qui ajoute le header sur chaque réponse.

---

### MEDIUM-03 — SESSION_COOKIE_AGE non configuré (session perpétuelle)

**Risque** : MEDIUM
**Localisation** : `atlas_energies/settings/base.py`
**Description** :
`SESSION_COOKIE_AGE` n'est pas configuré. La valeur par défaut Django est **1 209 600 secondes (14 jours)**. Avec `ACCOUNT_SESSION_REMEMBER = True`, la session peut être encore plus longue.

Pour une application financière, une session de 14 jours sans activité est excessive.

**Impact** :
- Vol de cookie de session (XSS, réseau non sécurisé) → accès maintenu 14 jours.
- Poste partagé non verrouillé → accès non autorisé longtemps après départ de l'utilisateur.

**Recommandation** :
```python
# base.py
SESSION_COOKIE_AGE = 28800        # 8 heures (journée de travail)
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Expire à fermeture navigateur
SESSION_SAVE_EVERY_REQUEST = True  # Renouvelle à chaque requête (activité = maintien)
```

---

### MEDIUM-04 — django-extensions dans les requirements de production

**Risque** : MEDIUM
**Localisation** : `requirements.txt` ligne 19
**Description** :
`django-extensions==3.2.3` est listé dans `requirements.txt` (principal, pas un fichier `-dev`). Cette bibliothèque fournit des commandes de management potentiellement dangereuses en production :
- `shell_plus` : shell interactif avec accès complet aux modèles
- `export_emails` : export de tous les emails
- `runserver_plus` : serveur de développement avec debugger Werkzeug (si mal configuré)

**Recommandation** :
Séparer en `requirements/base.txt`, `requirements/dev.txt`, `requirements/prod.txt`.
`django-extensions` doit être dans `dev.txt` uniquement.

---

### MEDIUM-05 — Pas de header ACCOUNT_DEFAULT_HTTP_PROTOCOL pour les emails

**Risque** : MEDIUM
**Localisation** : `atlas_energies/settings/base.py` et `prod.py`
**Description** :
Sans `ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'`, allauth génère des liens de réinitialisation de mot de passe en `http://` même en production.

Un lien comme `http://atlas-energies.ci/comptes/password/reset/key/...` envoyé par email sera :
- Visible en clair sur les réseaux non chiffrés
- Loggé par les proxies / pare-feux d'entreprise
- Potentiellement sniffable sur un réseau WiFi partagé

**Recommandation** :
```python
# prod.py
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'
```

---

### MEDIUM-06 — Recherche textuelle sans protection contre les injections de filtres

**Risque** : MEDIUM
**Localisation** : `depenses/views.py` lignes 37–48 et 131–137
**Description** :
Le paramètre `q` de recherche est passé directement dans `__icontains` et `projet_id` dans `filter(centre_budgetaire_id=projet_id)` sans validation de type :
```python
projet_id = self.request.GET.get('projet', '')
if projet_id:
    qs = qs.filter(centre_budgetaire_id=projet_id)
```
Si `projet_id` contient une valeur non numérique, Django lève une `ValueError` non gérée → page 500. Pire, une valeur comme `0 OR 1=1` ne fonctionne pas avec l'ORM Django (protégé contre SQLi), mais la non-validation peut causer des comportements inattendus.

**Impact** : Information disclosure via pages d'erreur 500 si DEBUG=True accidentellement actif.

**Recommandation** :
```python
projet_id = self.request.GET.get('projet', '')
try:
    projet_id = int(projet_id)
    qs = qs.filter(centre_budgetaire_id=projet_id)
except (ValueError, TypeError):
    pass  # Ignorer silencieusement les valeurs invalides
```

---

### MEDIUM-07 — Absence d'audit log pour les actions sécurité critiques

**Risque** : MEDIUM
**Localisation** : `core/views.py` — `agent_toggle_active()`, `AgentCreateView`, `AgentUpdateView`
**Description** :
Les actions critiques suivantes ne sont pas tracées dans un log de sécurité dédié :
- Création d'un compte utilisateur
- Changement de rôle (agent → chef)
- Activation/désactivation d'un compte

`django-simple-history` trace les modifications de modèle, mais ces traces ne sont pas **alertes sécurité** et ne permettent pas une réponse à incident rapide.

**Impact** :
- En cas de compromission du compte chef, les actions malveillantes (création de compte fantôme, élévation de privilège) ne sont pas détectées en temps réel.

**Recommandation** :
```python
# Dans agent_toggle_active et les views de création/modification :
import logging
security_logger = logging.getLogger('security')

security_logger.warning(
    "ROLE_CHANGE user=%s target=%s new_role=%s ip=%s",
    request.user.email, user.email, user.role,
    request.META.get('REMOTE_ADDR')
)
```
Configurer un handler séparé pour les logs de sécurité dans `LOGGING`.

---

### LOW-01 — SECURE_BROWSER_XSS_FILTER : header obsolète et trompeur

**Risque** : LOW
**Localisation** : `atlas_energies/settings/prod.py` ligne 15
**Description** :
```python
SECURE_BROWSER_XSS_FILTER = True  # Envoie X-XSS-Protection: 1; mode=block
```
Ce header (`X-XSS-Protection`) est **déprécié depuis Chrome 78 (2019)** et peut en réalité **créer des vulnérabilités XSS** dans certains navigateurs plus anciens (IE). Il a été retiré des recommandations OWASP et MDN.

**Recommandation** : Le désactiver et le remplacer par une politique CSP robuste (voir HIGH-02).
```python
SECURE_BROWSER_XSS_FILTER = False  # Ou supprimer la ligne
```

---

### LOW-02 — SESSION_COOKIE_SAMESITE non configuré

**Risque** : LOW
**Localisation** : `atlas_energies/settings/base.py` et `prod.py`
**Description** :
`SESSION_COOKIE_SAMESITE` n'est pas défini explicitement. La valeur par défaut Django est `'Lax'`, ce qui protège contre la majorité des attaques CSRF. Mais pour une application interne sans authentification cross-origin légitime, `'Strict'` est préférable.

**Recommandation** :
```python
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SAMESITE = 'Strict'
```

---

### LOW-03 — django-guardian installé mais son utilisation est incertaine

**Risque** : LOW
**Localisation** : `requirements.txt` + `settings/base.py` INSTALLED_APPS
**Description** :
`django-guardian` est installé et le backend `guardian.backends.ObjectPermissionBackend` est dans `AUTHENTICATION_BACKENDS`. Cependant, aucune vue ou décorateur utilisant des permissions objet (`get_objects_for_user`, `@permission_required`) n'est visible dans le code audité.

Chaque bibliothèque installée = surface d'attaque supplémentaire. guardian ajoute une table `UserObjectPermission` et `GroupObjectPermission` dans la base de données.

**Recommandation** :
Si guardian n'est pas utilisé, le supprimer de `INSTALLED_APPS` et `AUTHENTICATION_BACKENDS` ainsi que de `requirements.txt`.

---

### LOW-04 — allauth.socialaccount installé sans provider configuré

**Risque** : LOW
**Localisation** : `settings/base.py` INSTALLED_APPS
**Description** :
`allauth.socialaccount` est dans `INSTALLED_APPS` mais aucun provider social (Google, GitHub, etc.) n'est configuré. Cela expose des endpoints OAuth non nécessaires (`/comptes/social/...`) qui augmentent la surface d'attaque.

**Recommandation** :
```python
THIRD_PARTY_APPS = [
    'allauth',
    'allauth.account',
    # 'allauth.socialaccount',  # Supprimer si non utilisé
]
```

---

### LOW-05 — Nom de fichier uploadé révélé dans les exports Excel/CSV

**Risque** : LOW
**Localisation** : `depenses/exports.py`
**Description** :
Les exports incluent probablement le chemin complet ou le nom de fichier des pièces jointes. Ces informations révèlent l'arborescence interne du serveur (`depenses/exploitation/2026/03/...`) et potentiellement des noms de fichiers confidentiels.

**Recommandation** :
Dans les exports, n'inclure que le nom de fichier (`os.path.basename()`), pas le chemin complet. Mieux : n'inclure qu'un indicateur booléen `Oui/Non` dans les exports partagés.

---

### INFORMATIONAL-01 — Absence d'authentification multifacteur (MFA/2FA)

**Risque** : INFORMATIONAL
**Localisation** : Configuration allauth globale
**Description** :
Pour une application de gestion financière (budgets, dépenses, exports), l'absence de MFA est un risque acceptable en MVP mais inacceptable en production à terme. allauth 0.63.6 supporte les OTP via `allauth.mfa`.

**Recommandation** :
Activer `allauth.mfa` et rendre le TOTP obligatoire pour le rôle `chef` au minimum.

---

### INFORMATIONAL-02 — Validation MIME des fichiers uploadés non vérifiable

**Risque** : INFORMATIONAL
**Localisation** : `depenses/validators.py` (non lu — référencé depuis models.py)
**Description** :
Le module `filetype==1.2.0` est dans `requirements.txt`, ce qui est une bonne pratique. Cependant, sans accès au code de `validators.py`, il est impossible de confirmer que :
1. La validation MIME est effectuée en plus de la validation par extension
2. Les fichiers `.docx`/`.xlsx` (qui sont des ZIP) sont correctement filtrés (risque de zip bombs)
3. La taille max est vérifiée **avant** l'écriture sur disque (pas seulement après)

**Recommandation** :
S'assurer que `validate_file_extension` utilise `filetype.guess()` et non seulement `filename.split('.')[-1]`.

---

### INFORMATIONAL-03 — django-debug-toolbar dans requirements principal

**Risque** : INFORMATIONAL
**Localisation** : `requirements.txt` ligne 46
**Description** :
`django-debug-toolbar` est dans `requirements.txt` (global). S'il est accidentellement activé en production avec `DEBUG=True`, il expose des informations critiques : requêtes SQL, variables d'environnement, configuration Django complète, profiling.

**Recommandation** :
Le déplacer dans un fichier `requirements/dev.txt` séparé.

---

### INFORMATIONAL-04 — Pas de ACCOUNT_UNIQUE_EMAIL explicite dans allauth

**Risque** : INFORMATIONAL
**Localisation** : `atlas_energies/settings/base.py`
**Description** :
`ACCOUNT_UNIQUE_EMAIL` n'est pas explicitement défini. Bien que le modèle `CustomUser` ait `email = models.EmailField(unique=True)`, allauth effectue sa propre vérification séparément. Si `ACCOUNT_UNIQUE_EMAIL = False`, allauth pourrait tenter de créer un doublon (qui sera bloqué par la contrainte DB mais avec une erreur 500 non gérée).

**Recommandation** :
```python
ACCOUNT_UNIQUE_EMAIL = True  # Explicite vaut mieux qu'implicite
```

---

## Récapitulatif et recommandations stratégiques

### Les 5 points les plus graves

| Priorité | Finding | Action requise |
|----------|---------|----------------|
| 🔴 1 | **CRITICAL-01** — Credentials exposés dans .env | **Révoquer le mot de passe Gmail maintenant, régénérer la SECRET_KEY** |
| 🔴 2 | **CRITICAL-02** — Aucun rate limiting sur login/reset | Configurer `ACCOUNT_RATE_LIMITS` + `django-axes` |
| 🔴 3 | **CRITICAL-03** — Signaux budget sans transaction atomique | Encapsuler dans `transaction.atomic()` + `select_for_update()` |
| 🟠 4 | **HIGH-02** — Absence de CSP + CDN sans SRI | Migrer assets en local, implémenter `django-csp` |
| 🟠 5 | **HIGH-04** — Conflit config email SSL/TLS | Unifier la config email dans `.env` uniquement |

### Recommandation globale

> **⛔ NO-GO — Déploiement en production INTERDIT en l'état**

L'application ne peut pas être déployée en production tant que les 3 findings CRITICAL ne sont pas résolus. Les 5 findings HIGH doivent être résolus avant la mise en production. Les MEDIUM peuvent être traités en sprint post-launch si les CRITICAL et HIGH sont couverts.

### Prochaines étapes suggérées (ordre de priorité)

**Sprint immédiat (< 48h) :**
1. Révoquer les credentials Gmail compromis
2. Régénérer la SECRET_KEY et la stocker hors du code source
3. Ajouter `.env` dans `.gitignore` + vérifier l'historique git (`git log --all -- .env`)
4. Corriger les signaux budget avec `transaction.atomic()`
5. Configurer `ACCOUNT_RATE_LIMITS`

**Sprint 1 (< 1 semaine) :**
6. Randomiser les noms de fichiers uploadés (uuid4)
7. Corriger `serve_media` avec `pathlib.Path.resolve()`
8. Unifier la configuration email
9. Ajouter `SESSION_COOKIE_AGE = 28800`
10. Valider les paramètres de filtre (`projet_id` → cast int)

**Sprint 2 (avant mise en production) :**
11. Implémenter `django-csp` + migrer assets CDN en local
12. Supprimer `allauth.socialaccount`, `django-guardian` si non utilisés
13. Déplacer `django-extensions` et `django-debug-toolbar` en requirements dev
14. Ajouter `ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https'`
15. Configurer les logs de sécurité (création/modification utilisateurs)

**Recommandation long terme :**
- Implémenter MFA (TOTP) obligatoire pour le rôle Chef d'Agence
- Audit des validators de fichiers uploadés (`validators.py`)
- Mettre en place un WAF (Web Application Firewall) devant nginx en production
- Pentesting complet avec un outil automatisé (OWASP ZAP, Nuclei) avant go-live

---

*Document généré lors de l'audit de sécurité du 18/03/2026 — Atlas Énergies / GestionProjetAgence*
*Ce rapport est CONFIDENTIEL — usage interne uniquement*
