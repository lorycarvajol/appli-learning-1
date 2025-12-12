# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **web-based learning platform** for teaching web development, featuring:
- Controlled progression system (trainer unlocks chapters for learners)
- Interactive code exercises with automatic validation in Docker sandbox
- Gamification (badges, points, leaderboard)
- Real-time activity tracking via WebSocket
- Community forum
- Project submission and review system

**Target Users:** 3 roles - Learner (students), Trainer (instructors), Admin
**Tech Stack:** Django 5.0+ (backend), React 18+ (frontend), PostgreSQL, Redis, Celery, Django Channels

## Development Commands

### Backend (Django)

```bash
cd backend

# Environment setup
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements/development.txt

# Database operations
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser

# Run development server
python manage.py runserver  # http://localhost:8000

# Run tests
pytest                              # All tests
pytest --cov=apps                   # With coverage
pytest apps/accounts/tests/         # Specific app tests
pytest -k test_user_registration    # Single test

# Code quality
black .                             # Format code
flake8 .                            # Lint
isort .                             # Sort imports

# Celery workers (for async tasks)
celery -A config worker -l info
celery -A config beat -l info       # Scheduler
```

### Frontend (React + Vite)

```bash
cd frontend

# Setup
npm install

# Development
npm run dev                         # http://localhost:5173

# Build
npm run build
npm run preview                     # Preview production build

# Tests
npm run test                        # Unit tests (Vitest)
npm run test:coverage               # With coverage
npm run test:e2e                    # End-to-end tests (Playwright)

# Linting
npm run lint
```

### Infrastructure (Docker)

```bash
# Start PostgreSQL + Redis
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Reset everything
docker-compose down -v
```

## Architecture Overview

### Backend Structure

Django project organized by feature modules in `backend/apps/`:

- **accounts/** - User authentication (custom User model), JWT tokens, profiles
- **courses/** - Content management (Chapter, Lesson, Exercise, Quiz, Project models)
- **progression/** - User progress tracking (UserProgress, ChapterAccess, ActivityLog)
- **gamification/** - Badges, points, leaderboard system
- **forum/** - Community Q&A forum (posts, replies, votes)
- **validation/** - Code execution sandbox (Docker-based, runs user submissions)

**Key patterns:**
- Custom User model: `accounts.User` with UUID primary keys and role-based access (LEARNER/TRAINER/ADMIN)
- Service layer: Business logic in `services.py` files (e.g., `badge_service.py`, `code_runner.py`)
- Settings split: `config/settings/` has `base.py`, `development.py`, `production.py`
- API: Django REST Framework with JWT authentication
- WebSocket: Django Channels with Redis channel layer for real-time updates
- Async tasks: Celery for code validation, badge awards, batch operations

### Frontend Structure

React app organized by features in `frontend/src/features/`:

- **auth/** - Login, Register, JWT token management
- **chapters/** - Chapter list, cards, progress display
- **lessons/** - Lesson viewer, navigation, Markdown rendering
- **exercises/** - Monaco code editor, test results, hints
- **quizzes/** - Quiz interface, questions, results
- **progression/** - Progress dashboard, charts, activity timeline
- **gamification/** - Badge gallery, leaderboard, points display
- **forum/** - Forum posts, replies, voting
- **trainer/** - Trainer dashboard, student tracking, live activity, project reviews

**Key patterns:**
- Redux Toolkit for state management with slices per feature
- Axios interceptors for JWT token refresh on 401
- WebSocket service (`wsService.js`) for real-time updates with auto-reconnect
- Custom hooks: `useAutosave` (3-second debounce), `useDebounce`, `useWebSocket`
- Code splitting with React.lazy for performance
- Tailwind CSS for styling

### Database Schema

PostgreSQL with UUID primary keys throughout:

**Core tables:**
- `accounts_user` - Custom user model with email-based auth, role field
- `accounts_profile` - User profile with points, level, avatar
- `courses_chapter` - Chapters with order_index, estimated_duration
- `courses_lesson` - Lessons (type: THEORY/EXERCISE/QUIZ)
- `courses_exercise` - Exercises with starter_code, tests (JSONB), solution
- `courses_quiz` - Quizzes with questions (JSONB), passing_score
- `progression_userprogress` - Per-user/lesson progress (status, attempts, time_spent, last_code)
- `progression_chapteraccess` - Chapter unlock tracking (is_unlocked, unlocked_by_id)
- `gamification_badge` - Badge definitions with criteria (JSONB)
- `gamification_userbadge` - User-earned badges
- `gamification_pointtransaction` - Points history
- `forum_post` and `forum_reply` - Forum content with votes

**Important indexes:**
- User lookups: `idx_user_email`, `idx_user_role`
- Progress queries: `idx_progress_user_lesson`, `idx_progress_status`
- Activity logs: `idx_activity_created` (DESC for recent activity)

### WebSocket Architecture

Real-time communication via Django Channels:

**Endpoints:**
- `ws://api/ws/progress/{exercise_id}/` - Auto-save code every 3 seconds
- `ws://api/ws/activity/chapter/{chapter_id}/` - Trainer sees student activity
- `ws://api/ws/notifications/` - Badge awards, chapter unlocks

**Message types (server → client):**
- `progress_saved` - Confirmation of saved code
- `user_activity` - Student started/completed lesson
- `chapter_unlocked` - Trainer unlocked new chapter
- `badge_earned` - New badge awarded
- `validation_result` - Code validation completed

**Implementation notes:**
- Redis channel layer for pub/sub between server instances
- Auto-save: Client debounces 3s → WebSocket → Redis cache → Async DB write (batched every 10s)
- JWT authentication in WebSocket handshake via `scope['user']`

### Security Considerations

**Code execution sandbox:**
- User code runs in isolated Docker containers
- Network disabled (`network_mode='none'`)
- Resource limits: 128MB RAM, 50% CPU quota, 5s timeout
- Dangerous patterns blocked: `eval`, `exec`, `__import__`, `os.system`, `subprocess`
- Validation: Serializer checks before sandbox execution

**Authentication:**
- JWT tokens: 1-hour access token, 7-day refresh token with rotation
- Token blacklist after refresh (requires `rest_framework_simplejwt.token_blacklist` in INSTALLED_APPS)
- CORS configured for specific origins only
- Rate limiting: 100 req/hour (anon), 1000 req/hour (authenticated), 10/min (submissions)

**Data protection:**
- All user input validated via DRF serializers
- HTML/Markdown sanitized with `bleach` library (whitelist tags)
- Django ORM used exclusively (parameterized queries)
- HTTPS enforced in production
- Passwords hashed with Django's default (PBKDF2)

## Development Workflow

### Creating a New Feature Module

When adding a new Django app (e.g., `notifications`):

```bash
cd backend/apps
mkdir notifications
cd notifications
touch __init__.py models.py views.py serializers.py urls.py admin.py services.py tests.py
```

1. Define models in `models.py` with UUID primary keys
2. Create serializers in `serializers.py` for API validation
3. Implement business logic in `services.py` (not in views)
4. Create API endpoints in `views.py` using DRF ViewSets
5. Register URLs in `urls.py`, then include in `config/urls.py`
6. Register admin interface in `admin.py`
7. Write tests in `tests/` directory
8. Add app to `INSTALLED_APPS` in `config/settings/base.py`
9. Run migrations: `python manage.py makemigrations notifications`

### Adding a React Feature

When adding a new frontend feature (e.g., `notifications`):

1. Create feature directory: `frontend/src/features/notifications/`
2. Create Redux slice: `notificationsSlice.js` with async thunks
3. Add reducer to store: `frontend/src/app/store.js`
4. Create components: `NotificationList.jsx`, `NotificationItem.jsx`
5. Add API service: `frontend/src/services/api/notificationsApi.js`
6. Add routes in `frontend/src/App.jsx`
7. Style with Tailwind utility classes

### Working with WebSocket

To add real-time functionality:

**Backend (Django Channels consumer):**
```python
# backend/channels/consumers/your_consumer.py
from channels.generic.websocket import AsyncWebsocketConsumer

class YourConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Join channel group
        await self.channel_layer.group_add("group_name", self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        # Handle incoming messages
        # Broadcast: await self.channel_layer.group_send("group_name", {...})
```

**Frontend (React hook):**
```javascript
// Use existing wsService or create custom hook
import wsService from '@/services/websocket/wsService';

useEffect(() => {
  wsService.connect(token);

  wsService.socket.on('your_event', (data) => {
    dispatch(updateState(data));
  });

  return () => wsService.disconnect();
}, []);
```

### Code Validation System

When adding new exercise types:

1. Define test structure in `Exercise.tests` JSONB field:
```json
{
  "tests": [
    {
      "name": "Test 1",
      "code": "assert solution(2, 3) == 5",
      "points": 10
    }
  ]
}
```

2. Validation happens in `apps/validation/services/code_runner.py`
3. Docker sandbox limits are configurable in `sandbox.py`
4. Results sent via WebSocket to user's channel

## Important Patterns and Conventions

### Django Models
- Always use UUID for primary keys: `id = models.UUIDField(primary_key=True, default=uuid.uuid4)`
- Add timestamps: `created_at`, `updated_at` with auto triggers
- Use explicit `db_table` names: `class Meta: db_table = 'app_model'`
- Complex data in JSONB fields (PostgreSQL): `tests = models.JSONField()`

### API Endpoints
- Follow REST conventions: `/api/{resource}/` for list, `/api/{resource}/{id}/` for detail
- Custom actions: `/api/exercises/{id}/submit/`, `/api/chapters/{id}/unlock/`
- Use DRF ViewSets for CRUD, APIView for custom logic
- Permissions: Combine `IsAuthenticated`, `IsOwnerOrTrainer`, `IsTrainerOrReadOnly`
- Pagination: Default 20 items per page
- Query params: `?search=`, `?ordering=`, `?chapter=`, `?status=`

### Frontend State Management
- Redux slices per feature with createAsyncThunk for API calls
- Loading states: `{ loading: false, error: null, data: null }`
- Optimistic updates for better UX (e.g., auto-save indicator)
- WebSocket updates dispatched as Redux actions

### Performance Optimization
- **Backend:** Use `select_related()` / `prefetch_related()` to avoid N+1 queries
- **Backend:** Cache frequently accessed data in Redis (TTL: 30min-1h)
- **Backend:** Celery for slow operations (code validation, email, badge calculations)
- **Frontend:** React.memo for expensive components
- **Frontend:** Code splitting with lazy() for large features
- **Frontend:** Debounce user input (search, auto-save) with custom hooks

### Testing Strategy
- **Backend:** pytest-django for models, views, services
- **Backend:** factory_boy for test fixtures
- **Backend:** Target 80%+ code coverage
- **Frontend:** Vitest for component/hook tests
- **Frontend:** Playwright for E2E critical flows (register → login → complete exercise)

## Project Phases (from Roadmap)

This project follows a 12-week roadmap:

**Phase 1 (Weeks 1-3) - Foundations:** User auth, content models, progression system, Django admin
**Phase 2 (Weeks 4-6) - Real-time:** WebSocket integration, auto-save, trainer dashboard with live activity
**Phase 3 (Weeks 7-8) - Gamification:** Badges, points, leaderboard, code validation
**Phase 4 (Weeks 9-10) - Collaboration:** Final projects, trainer review, forum
**Phase 5 (Weeks 11-12) - Production:** Performance optimization, CI/CD, deployment

Current focus should align with the roadmap phase. Check `01_ROADMAP.md` for sprint breakdown.

## Common Issues and Solutions

**"Module not found: apps.accounts"**
- Ensure `apps/` directory has `__init__.py`
- Check `INSTALLED_APPS` includes `'apps.accounts'` (full path)

**Database migration conflicts:**
```bash
# Reset migrations (development only!)
python manage.py migrate {app} zero
rm apps/{app}/migrations/000*.py
python manage.py makemigrations {app}
python manage.py migrate
```

**CORS errors in development:**
- Verify `corsheaders` in `INSTALLED_APPS` and first in `MIDDLEWARE`
- Check `CORS_ALLOWED_ORIGINS` includes `http://localhost:5173`
- Ensure `CORS_ALLOW_CREDENTIALS = True` for JWT cookies

**WebSocket connection failed:**
- Ensure Redis is running: `docker-compose ps`
- Check Daphne ASGI server is running on port 8001 (separate from Django WSGI)
- Verify JWT token is passed in connection auth headers

**Code validation timeout:**
- Default timeout is 5 seconds (configurable in `sandbox.py`)
- Check Docker daemon is running and accessible
- Review sandbox resource limits if needed

## Reference Documentation

All detailed documentation is in the root directory:

- **01_ROADMAP.md** - 12-week project roadmap with sprints and deliverables
- **02_USER_STORY_MAPPING.md** - User stories for all 3 personas with acceptance criteria
- **03_DIAGRAMMES_UML.md** - UML diagrams (use cases, class, sequence, deployment)
- **04_ARCHITECTURE_TECHNIQUE.md** - Complete technical architecture with code examples
- **05_GUIDE_DEVELOPPEMENT_INITIAL.md** - Step-by-step initial setup guide
- **README.md** - Project overview and quick start

When implementing features, cross-reference these documents for requirements and design decisions.
