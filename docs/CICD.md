# CI/CD — Déploiement automatique via GitHub Actions

## Vue d'ensemble

À chaque push sur la branche `prod`, GitHub Actions se connecte automatiquement au VPS via SSH et déploie la nouvelle version.

```
Push → branche prod → GitHub Actions → SSH VPS → git pull → migrate → collectstatic → restart
```

---

## Workflow de travail quotidien

### Développer sur main
```bash
# Travailler normalement sur main
git add .
git commit -m "feat: nouvelle fonctionnalité"
git push origin main
```

### Déployer en production
```bash
# Basculer sur prod et merger main
git checkout prod
git merge main
git push origin prod
# → GitHub Actions se déclenche automatiquement
```

### Vérifier le déploiement
- Aller sur GitHub → onglet **Actions**
- Le workflow **Deploy to VPS** doit passer au vert ✅

---

## Configuration initiale (déjà en place)

### 1. Clé SSH dédiée au déploiement

Générer sur le VPS :
```bash
ssh-keygen -t ed25519 -C "github-deploy" -f ~/.ssh/github_deploy
cat ~/.ssh/github_deploy.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

### 2. Secrets GitHub

Dans GitHub → **Settings → Secrets and variables → Actions** :

| Secret | Valeur |
|--------|--------|
| `VPS_SSH_KEY` | Contenu de `~/.ssh/github_deploy` (clé privée) |
| `VPS_HOST` | `79.143.190.190` |
| `VPS_USER` | `hans` |

### 3. Permission sudo sans mot de passe

Sur le VPS :
```bash
sudo visudo
```
Ajouter à la fin :
```
hans ALL=(ALL) NOPASSWD: /bin/systemctl restart atlas
```

### 4. Fichier workflow

Fichier : `.github/workflows/deploy.yml`

```yaml
name: Deploy to VPS

on:
  push:
    branches:
      - prod

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
      - name: Deploy via SSH
        uses: appleboy/ssh-action@v1.0.3
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          script: |
            cd ~/ATLAS-ENERGIE
            git pull origin prod
            source venv/bin/activate
            pip install -r requirements/base.txt --quiet
            DJANGO_SETTINGS_MODULE=atlas_energies.settings.prod python manage.py migrate --noinput
            DJANGO_SETTINGS_MODULE=atlas_energies.settings.prod python manage.py collectstatic --noinput
            sudo systemctl restart atlas
```

---

## Dépannage

### Le workflow échoue — erreur SSH
- Vérifier que le secret `VPS_SSH_KEY` contient bien toute la clé privée (de `-----BEGIN` à `-----END`)
- Vérifier que la clé publique est dans `~/.ssh/authorized_keys` sur le VPS

### Le workflow échoue — erreur git pull
```bash
# Sur le VPS, vérifier l'état du repo
cd ~/ATLAS-ENERGIE
git status
git log --oneline -5
```

### Le workflow passe au vert mais le site ne se met pas à jour
```bash
# Vérifier que Gunicorn a bien redémarré
sudo systemctl status atlas
sudo journalctl -u atlas -f
```

### Relancer le déploiement manuellement
```bash
# Depuis ton PC — commit vide pour déclencher le workflow
git commit --allow-empty -m "ci: redéploiement"
git push origin prod
```
