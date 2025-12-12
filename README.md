# 🎓 Plateforme d'Apprentissage Web - Documentation Complète

## 📋 Vue d'Ensemble

Cette plateforme est une application web interactive pour l'apprentissage de la programmation web, avec :
- 🎯 Système de progression contrôlée par formateur
- 💻 Exercices de code avec validation automatique
- 🎮 Gamification (badges, points, classements)
- 📊 Suivi temps réel de l'activité des apprenants
- 💬 Forum communautaire
- 🚀 Architecture moderne Django + React

---

## 📚 DOCUMENTATION DISPONIBLE

### 🗺️ [01_ROADMAP.md](./01_ROADMAP.md)
**Roadmap complète du projet sur 12 semaines**
- Planning par sprints
- Livrables attendus
- Métriques de succès
- Analyse des risques

**À utiliser pour :** Planification, suivi de projet, priorisation

---

### 📖 [02_USER_STORY_MAPPING.md](./02_USER_STORY_MAPPING.md)
**User Stories détaillées et personas**
- 3 personas (Apprenant, Formateur, Admin)
- 30+ user stories avec critères d'acceptation
- Story points et estimation
- Priorisation MoSCoW

**À utiliser pour :** Développement orienté utilisateur, tests d'acceptation

---

### 🏗️ [03_DIAGRAMMES_UML.md](./03_DIAGRAMMES_UML.md)
**Diagrammes UML complets**
- Diagramme de cas d'utilisation
- Diagramme de classes (modèle de données)
- Diagrammes de séquence (authentification, WebSocket, déblocage)
- Diagrammes d'activité et d'état
- Architecture de déploiement

**À utiliser pour :** Compréhension technique, développement backend

---

### 🏛️ [04_ARCHITECTURE_TECHNIQUE.md](./04_ARCHITECTURE_TECHNIQUE.md)
**Architecture complète et détaillée**
- Stack technologique
- Structure backend Django (avec code)
- Structure frontend React (avec code)
- Schéma base de données PostgreSQL
- API REST endpoints
- Configuration WebSocket
- Sécurité et performance

**À utiliser pour :** Implémentation technique, référence code

---

### 🚀 [05_GUIDE_DEVELOPPEMENT_INITIAL.md](./05_GUIDE_DEVELOPPEMENT_INITIAL.md)
**Guide pas-à-pas pour démarrer le projet**
- Setup environnement local
- Configuration Django + PostgreSQL + Redis
- Configuration React + Redux
- Authentification JWT
- Premier test end-to-end

**À utiliser pour :** Onboarding nouveaux développeurs, setup initial

---

## 🛠️ STACK TECHNIQUE

### Backend
```
Framework: Django 5.0+
API: Django REST Framework
WebSockets: Django Channels
Async Tasks: Celery
Database: PostgreSQL 15+
Cache/Broker: Redis 7.0+
Auth: JWT (djangorestframework-simplejwt)
```

### Frontend
```
Framework: React 18+
State: Redux Toolkit
Router: React Router 6+
HTTP: Axios
WebSocket: Socket.io-client
Editor: Monaco Editor
Styling: Tailwind CSS
Build: Vite
```

### DevOps
```
Container: Docker + Docker Compose
CI/CD: GitHub Actions
Hosting: Railway / Render
Monitoring: Sentry
Storage: AWS S3 / Railway Storage
```

---

## 🚀 QUICK START

### Prérequis
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### Installation Rapide

```bash
# 1. Cloner le repository
git clone https://github.com/votre-org/learning-platform.git
cd learning-platform

# 2. Démarrer les services (PostgreSQL + Redis)
docker-compose up -d

# 3. Backend Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements/development.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver  # http://localhost:8000

# 4. Frontend Setup (nouveau terminal)
cd ../frontend
npm install
npm run dev  # http://localhost:5173
```

### Premier Test
1. Ouvrir http://localhost:5173
2. S'inscrire avec un nouveau compte
3. Se connecter
4. Vérifier le token dans localStorage (DevTools)

**Plus de détails :** Voir [05_GUIDE_DEVELOPPEMENT_INITIAL.md](./05_GUIDE_DEVELOPPEMENT_INITIAL.md)

---

## 📦 STRUCTURE DU PROJET

```
learning-platform/
│
├── backend/                    # Django Backend
│   ├── apps/
│   │   ├── accounts/          # Utilisateurs & Auth
│   │   ├── courses/           # Chapitres, Leçons, Exercices
│   │   ├── progression/       # Suivi progression
│   │   ├── gamification/      # Badges, Points
│   │   ├── forum/             # Forum communauté
│   │   └── validation/        # Validation code
│   ├── config/                # Settings Django
│   ├── channels/              # WebSocket consumers
│   └── requirements/
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── app/               # Redux store
│   │   ├── features/          # Features (auth, chapters, etc.)
│   │   ├── components/        # Composants réutilisables
│   │   ├── services/          # API & WebSocket services
│   │   └── hooks/             # Custom React hooks
│   └── public/
│
├── docs/                       # Documentation (ce dossier)
│   ├── 01_ROADMAP.md
│   ├── 02_USER_STORY_MAPPING.md
│   ├── 03_DIAGRAMMES_UML.md
│   ├── 04_ARCHITECTURE_TECHNIQUE.md
│   └── 05_GUIDE_DEVELOPPEMENT_INITIAL.md
│
├── docker-compose.yml
└── README.md                   # Ce fichier
```

---

## 🎯 ROADMAP SIMPLIFIÉE

### Phase 1 : Fondations (Semaines 1-3) ✅
- [x] Setup projet Django + React
- [x] Authentification JWT
- [ ] Modèles de données (Chapitres, Leçons)
- [ ] Système de progression
- [ ] Admin Django pour création contenu

### Phase 2 : Temps Réel (Semaines 4-6)
- [ ] WebSocket avec Django Channels
- [ ] Sauvegarde auto toutes les 3s
- [ ] Interface apprenant (navigation, exercices, QCM)
- [ ] Dashboard formateur avec suivi temps réel

### Phase 3 : Gamification (Semaines 7-8)
- [ ] Système de points et badges
- [ ] Leaderboard
- [ ] Validation automatique exercices
- [ ] Feedback instantané

### Phase 4 : Collaboration (Semaines 9-10)
- [ ] Projets finaux avec soumission
- [ ] Review par formateur
- [ ] Forum Q&A par chapitre

### Phase 5 : Production (Semaines 11-12)
- [ ] Optimisation performance
- [ ] Tests de charge (20+ users simultanés)
- [ ] CI/CD avec GitHub Actions
- [ ] Déploiement Railway/Render

**Détails :** [01_ROADMAP.md](./01_ROADMAP.md)

---

## 🧪 TESTS

### Backend (Pytest)
```bash
cd backend
pytest                        # Tous les tests
pytest --cov=apps            # Avec couverture
pytest apps/accounts/tests/  # Tests spécifiques
```

### Frontend (Vitest)
```bash
cd frontend
npm run test                 # Tous les tests
npm run test:coverage        # Avec couverture
```

### Tests End-to-End (Playwright)
```bash
npm run test:e2e
```

---

## 📊 MÉTRIQUES CLÉS

### Objectifs Techniques
- ✅ Temps sauvegarde < 200ms
- ✅ Support 20+ connexions WebSocket simultanées
- ✅ API response time < 300ms (p95)
- ✅ Couverture tests > 80%
- ✅ Uptime 99.5%

### Objectifs Produit
- 🎯 Taux complétion chapitre > 70%
- 🎯 Temps moyen par exercice < 15min
- 🎯 Satisfaction utilisateurs > 4/5
- 🎯 Engagement forum > 30% users actifs

---

## 🔐 SÉCURITÉ

- ✅ JWT Authentication avec refresh tokens
- ✅ HTTPS enforced en production
- ✅ Rate limiting sur API (100 req/min)
- ✅ CORS configuré strictement
- ✅ Code execution dans sandbox Docker
- ✅ Input validation côté backend
- ✅ XSS & CSRF protection

**Détails :** [04_ARCHITECTURE_TECHNIQUE.md](./04_ARCHITECTURE_TECHNIQUE.md) - Section Sécurité

---

## 🚀 DÉPLOIEMENT

### Environnements
- **Development :** http://localhost:8000 (backend) + http://localhost:5173 (frontend)
- **Staging :** https://staging.learning-platform.com (auto-deploy on PR)
- **Production :** https://learning-platform.com (manual approval)

### Déploiement Production

```bash
# 1. Build Docker images
docker build -t learning-platform-backend:latest ./backend
docker build -t learning-platform-frontend:latest ./frontend

# 2. Push to registry
docker push registry.example.com/learning-platform-backend:latest
docker push registry.example.com/learning-platform-frontend:latest

# 3. Deploy via Railway CLI
railway up

# Ou via GitHub Actions (auto sur push main)
```

**Configuration complète :** [04_ARCHITECTURE_TECHNIQUE.md](./04_ARCHITECTURE_TECHNIQUE.md) - Section DevOps

---

## 👥 CONTRIBUTION

### Workflow Git

```bash
# 1. Créer branche feature
git checkout -b feature/US-013-code-editor

# 2. Développer et commiter
git add .
git commit -m "feat(exercises): add Monaco code editor component"

# 3. Push et créer PR
git push origin feature/US-013-code-editor

# 4. Review et merge sur main
```

### Convention Commits
```
feat: Nouvelle fonctionnalité
fix: Correction bug
docs: Documentation
style: Formatage code
refactor: Refactoring
test: Ajout tests
chore: Maintenance
```

### Code Review Checklist
- [ ] Tests passent
- [ ] Couverture tests maintenue
- [ ] Documentation à jour
- [ ] Pas de secrets hardcodés
- [ ] Respect des conventions

---

## 📞 RESSOURCES & LIENS

### Documentation Externe
- [Django Docs](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Docs](https://react.dev/)
- [Redux Toolkit](https://redux-toolkit.js.org/)
- [Tailwind CSS](https://tailwindcss.com/)

### Outils
- **Sentry :** https://sentry.io (monitoring)
- **Railway :** https://railway.app (hosting)
- **Figma :** [Design mockups] (à créer)

### Communication
- **Slack :** #learning-platform
- **Jira :** [Board du projet]
- **Notion :** [Wiki technique]

---

## ❓ FAQ

### Q: Quelle technologie dois-je choisir pour le front ?
**R:** React est recommandé pour cette plateforme car nous avons besoin de beaucoup d'interactivité (éditeur de code, WebSockets, temps réel).

### Q: Pourquoi Django Channels plutôt que Flask-SocketIO ?
**R:** Django Channels s'intègre nativement avec Django, gère mieux la scalabilité avec Redis, et offre une meilleure séparation entre HTTP et WebSocket.

### Q: Comment gérer 20+ utilisateurs simultanés ?
**R:** Combinaison de Redis (cache + channel layer), connection pooling PostgreSQL, et async workers Celery. Tests de charge avec Locust.

### Q: Le code des exercices est-il exécuté sur le serveur ?
**R:** Oui, dans un sandbox Docker isolé avec limitations CPU/RAM pour éviter abus.

### Q: Comment sont validés les exercices ?
**R:** Chaque exercice a une suite de tests unitaires prédéfinis. Le code soumis est exécuté contre ces tests dans le sandbox.

---

## 📄 LICENCE

[MIT License](LICENSE) - Libre d'utilisation

---

## 🙏 REMERCIEMENTS

Merci à tous les contributeurs et à la communauté open-source pour les outils utilisés dans ce projet.

---

## 📧 CONTACT

- **Email :** contact@learning-platform.com
- **GitHub :** https://github.com/votre-org/learning-platform
- **Issues :** https://github.com/votre-org/learning-platform/issues

---

**Dernière mise à jour :** 12 décembre 2024  
**Version :** 1.0.0  
**Status :** 🚧 En développement actif
