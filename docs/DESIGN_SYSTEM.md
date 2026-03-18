# Design System — GestionProjetAgence / Atlas Énergies

## Identité visuelle

| Élément | Valeur |
|---------|--------|
| Couleur primaire | `#2d7a2f` (vert Atlas) |
| Couleur primaire foncée | `#276228` |
| Couleur primaire claire | `#6ee26e` |
| Fond application | `#f1f5f9` (gris très clair) |
| Sidebar | `#0f172a` (quasi-noir) |
| Texte principal | `#0f172a` |
| Texte secondaire | `#64748b` |
| Bordures | `#e2e8f0` |
| Fond inputs | `#f8fafc` |
| Erreur | `#dc2626` |
| Succès | `#16a34a` |

---

## Pages d'authentification (login / logout / reset password)

Toutes les pages auth suivent le même **layout split 50/50** :

```
┌──────────────────────┬──────────────────────┐
│   PANNEAU GAUCHE     │   PANNEAU DROIT       │
│   fond: #fff         │   fond: gradient vert │
│   formulaire         │   logo + branding     │
│   max-width: 400px   │   feature pills       │
└──────────────────────┴──────────────────────┘
```

**Panneau droit — gradient :**
```css
background: linear-gradient(160deg, #0f2310 0%, #1a3d1b 40%, #276228 100%);
```

**Pattern SVG décoratif (panneau droit) :**
Croix blanches très légères (`fill-opacity: 0.03`) en arrière-plan.

**Cercles décoratifs :**
```html
<div class="circle-deco" style="width:400px; height:400px; top:-100px; right:-100px;"></div>
<div class="circle-deco" style="width:250px; height:250px; bottom:-60px; left:-60px;"></div>
<div class="circle-deco" style="width:150px; height:150px; top:40%; right:10%;"></div>
```

---

## Composants UI

### Boutons

```css
/* Primaire (vert) */
.btn-glass-primary / .btn-primary / .btn-login {
  background: linear-gradient(135deg, #2d7a2f 0%, #276228 100%);
  color: #fff;
  border-radius: 12px;
  padding: 13px;
  font-weight: 700;
  transition: all 0.2s ease;
}
:hover { transform: translateY(-1px); box-shadow: 0 8px 24px rgba(45,122,47,0.35); }

/* Danger (rouge) */
.btn-danger {
  background: linear-gradient(135deg, #dc2626 0%, #b91c1c 100%);
  box-shadow hover: 0 8px 24px rgba(220,38,38,0.35);
}

/* Secondaire (gris clair) */
.btn-cancel / .btn-glass-secondary {
  background: #f8fafc;
  border: 1.5px solid #e2e8f0;
  color: #475569;
}
```

### Inputs

```css
.input-field {
  border: 1.5px solid #e2e8f0;
  border-radius: 12px;
  padding: 12px 16px;
  background: #f8fafc;
  transition: all 0.2s ease;
}
:focus {
  border-color: #2d7a2f;
  background: #fff;
  box-shadow: 0 0 0 3px rgba(45,122,47,0.08);
}
```

### Cards (glassmorphisme)

```css
.glass-card {
  background: rgba(255,255,255,0.85);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.5);
  border-radius: 20px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06);
}

.kpi-card {
  background: #fff;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.05);
  border: 1px solid #f1f5f9;
}
```

### Info boxes (dans les pages auth)

```html
<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:14px; padding:16px 20px;">
  <div style="display:flex; gap:12px; align-items:flex-start;">
    <div style="width:32px; height:32px; background:rgba(45,122,47,0.1); border-radius:8px; ...">
      <!-- icône SVG ou emoji -->
    </div>
    <div>
      <p style="font-weight:600; font-size:0.82rem; color:#334155;">Titre</p>
      <p style="font-size:0.78rem; color:#64748b;">Description</p>
    </div>
  </div>
</div>
```

### Feature pills (panneau droit auth)

```html
<div style="display:flex; align-items:center; gap:14px;
            background:rgba(255,255,255,0.06);
            border:1px solid rgba(255,255,255,0.08);
            border-radius:14px; padding:14px 18px;">
  <div style="width:36px; height:36px; background:rgba(245,130,30,0.2);
              border-radius:10px; display:flex; align-items:center; justify-content:center;">
    <!-- icône SVG colorée -->
  </div>
  <div>
    <p style="font-weight:700; font-size:0.82rem; color:#fff;">Titre</p>
    <p style="font-size:0.72rem; color:rgba(255,255,255,0.4);">Sous-titre</p>
  </div>
</div>
```

---

## Animations

```css
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
.animate-up  { animation: slideUp 0.5s ease forwards; }
.delay-1     { animation-delay: 0.1s; opacity: 0; }
.delay-2     { animation-delay: 0.2s; opacity: 0; }
.delay-3     { animation-delay: 0.3s; opacity: 0; }
.delay-4     { animation-delay: 0.4s; opacity: 0; }

/* Check / succès */
@keyframes checkIn {
  0%   { opacity: 0; transform: scale(0.5); }
  70%  { transform: scale(1.1); }
  100% { opacity: 1; transform: scale(1); }
}
```

---

## Typographie

- **Police** : `Inter` (Google Fonts) — weights 400, 500, 600, 700, 800, 900
- **Titres** : `font-weight: 900`, `letter-spacing: -0.03em`
- **Labels form** : `font-size: 0.8rem`, `font-weight: 600`, `color: #334155`
- **Corps texte** : `font-size: 0.875rem`, `color: #64748b`
- **Micro texte** (footer, badges) : `font-size: 0.72rem`, `color: #94a3b8`

---

## Layout application (pages internes)

```
┌─────────────────────────────────────────────────────┐
│  TOPBAR sticky (glassmorphisme, hauteur 64px)        │
├───────────────┬─────────────────────────────────────┤
│               │                                     │
│   SIDEBAR     │   CONTENU PRINCIPAL                 │
│   fixe        │   padding: 24px                     │
│   252px       │   max-width: libre                  │
│   #0f172a     │                                     │
│               │                                     │
└───────────────┴─────────────────────────────────────┘
```

- Nav active : fond vert `#2d7a2f`, texte blanc
- Nav inactive : texte `rgba(255,255,255,0.6)`, hover fond `rgba(255,255,255,0.08)`
- Flash messages : auto-dismiss après 4 secondes (JS vanilla)

---

## Icônes

Heroicons (SVG inline) — style `outline`, stroke-width `2`.
Pas de bibliothèque d'icônes externe.

```html
<svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="..."/>
</svg>
```

---

## Tables

```css
.modern-table {
  width: 100%;
  border-collapse: collapse;
}
.modern-table th {
  background: #f8fafc;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 12px 16px;
}
.modern-table td {
  padding: 14px 16px;
  border-bottom: 1px solid #f1f5f9;
  font-size: 0.875rem;
  color: #1e293b;
}
.modern-table tr:hover td { background: #f8fafc; }
```

---

## Progress bars

```css
.progress-modern {
  height: 8px;
  background: #e2e8f0;
  border-radius: 100px;
  overflow: hidden;
}
.progress-modern .fill {
  height: 100%;
  background: linear-gradient(90deg, #2d7a2f, #6ee26e);
  border-radius: 100px;
  transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
/* Dépassement budget */
.progress-modern.over .fill {
  background: linear-gradient(90deg, #dc2626, #f87171);
}
```
