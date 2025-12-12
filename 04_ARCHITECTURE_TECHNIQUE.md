# 🏛️ ARCHITECTURE TECHNIQUE - Plateforme d'Apprentissage Web

## 📋 TABLE DES MATIÈRES
1. [Stack Technologique](#stack)
2. [Architecture Globale](#architecture)
3. [Structure Backend Django](#backend)
4. [Structure Frontend React](#frontend)
5. [Base de Données](#database)
6. [API REST Endpoints](#api)
7. [WebSocket Architecture](#websocket)
8. [Sécurité](#security)
9. [Performance & Scalabilité](#performance)
10. [DevOps & Déploiement](#devops)

---

## <a id="stack"></a>1. 📦 STACK TECHNOLOGIQUE

### Backend
```yaml
Framework: Django 5.0.3
API: Django REST Framework 3.14+
WebSockets: Django Channels 4.0+
Async Tasks: Celery 5.3+
Database: PostgreSQL 15+
Cache/Broker: Redis 7.0+
Authentication: JWT (djangorestframework-simplejwt)
```

### Frontend
```yaml
Framework: React 18.2+
State Management: Redux Toolkit 2.0+
Routing: React Router 6+
HTTP Client: Axios
WebSocket Client: Socket.io-client
Code Editor: Monaco Editor
Styling: Tailwind CSS 3.3+
Build Tool: Vite
```

### DevOps
```yaml
Containerization: Docker + Docker Compose
CI/CD: GitHub Actions
Hosting: Railway / Render
Monitoring: Sentry
Storage: AWS S3 / Railway Storage
Email: SendGrid
```

---

## <a id="architecture"></a>2. 🏗️ ARCHITECTURE GLOBALE

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                         │
├─────────────────────────────────────────────────────────────┤
│  React SPA (Vite)                                           │
│  ├─ Components (UI)                                         │
│  ├─ Redux Store (State)                                     │
│  ├─ API Services (HTTP/WS)                                  │
│  └─ Monaco Editor                                           │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   │ HTTPS / WSS
                   │
┌──────────────────┴──────────────────────────────────────────┐
│                      API GATEWAY                             │
├─────────────────────────────────────────────────────────────┤
│  Nginx (Reverse Proxy)                                      │
│  ├─ Rate Limiting                                           │
│  ├─ SSL Termination                                         │
│  ├─ Static Files Serving                                    │
│  └─ Load Balancing                                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
         ┌─────────┴─────────┐
         │                   │
┌────────┴────────┐  ┌───────┴────────┐
│  Gunicorn WSGI  │  │  Daphne ASGI   │
│  (Port 8000)    │  │  (Port 8001)   │
│  REST API       │  │  WebSockets    │
└────────┬────────┘  └───────┬────────┘
         │                   │
         │    ┌──────────────┴──────────────┐
         │    │                             │
┌────────┴────┴──────────────────────────┐  │
│         DJANGO APPLICATION              │  │
├─────────────────────────────────────────┤  │
│                                         │  │
│  ┌───────────────────────────────────┐ │  │
│  │         Core Apps                 │ │  │
│  ├───────────────────────────────────┤ │  │
│  │  accounts/      (Users, Auth)    │ │  │
│  │  courses/       (Content)        │ │  │
│  │  progression/   (Tracking)       │ │  │
│  │  gamification/  (Badges, Points) │ │  │
│  │  forum/         (Community)      │ │  │
│  │  validation/    (Code Exec)      │ │  │
│  └───────────────────────────────────┘ │  │
│                                         │  │
│  ┌───────────────────────────────────┐ │  │
│  │      Middleware Stack             │ │  │
│  ├───────────────────────────────────┤ │  │
│  │  - CORS                           │ │  │
│  │  - JWT Authentication             │ │  │
│  │  - Rate Limiting                  │ │  │
│  │  - Request Logging                │ │  │
│  │  - Exception Handling             │ │  │
│  └───────────────────────────────────┘ │  │
│                                         │  │
└─────────────────────────────────────────┘  │
                   │                         │
                   │                         │
         ┌─────────┴─────────┐               │
         │                   │               │
┌────────┴────────┐  ┌───────┴──────┐  ┌────┴─────────┐
│  PostgreSQL     │  │    Redis     │  │   Celery     │
│  (Primary DB)   │  │  (Cache/MQ)  │  │   Workers    │
└─────────────────┘  └──────────────┘  └──────────────┘
```

### Request Flow Examples

#### REST API Request
```
User Action → React Component → Axios (apiService.js)
                                     ↓
                              POST /api/chapters/
                              Header: Bearer {JWT}
                                     ↓
                              Nginx (Rate Check)
                                     ↓
                              Gunicorn
                                     ↓
                              Django Middleware Stack
                                     ↓
                              JWT Authentication
                                     ↓
                              Permission Check
                                     ↓
                              ViewSet (courses/views.py)
                                     ↓
                              Serializer Validation
                                     ↓
                              Business Logic (services/)
                                     ↓
                              Database Query
                                     ↓
                              Response Serialization
                                     ↓
                              JSON Response
                                     ↓
                              React State Update
                                     ↓
                              UI Re-render
```

#### WebSocket Flow
```
Component Mount → wsService.connect()
                         ↓
                  WebSocket Handshake
                         ↓
                  Daphne ASGI Server
                         ↓
                  Django Channels Routing
                         ↓
                  Consumer.connect()
                         ↓
                  JWT Validation
                         ↓
                  Join Channel Group
                         ↓
                  Redis SUBSCRIBE
                         ↓
              [Connection Established]
                         ↓
    User Types → Debounced Auto-save (3s)
                         ↓
                  wsService.send({type: "save", data})
                         ↓
                  Consumer.receive()
                         ↓
                  Save to Redis (cache)
                         ↓
                  Async DB Write (debounced)
                         ↓
                  Broadcast to Group (formateur)
                         ↓
                  wsService.onmessage (React)
                         ↓
                  Redux Action Dispatch
                         ↓
                  UI Update (progress bar)
```

---

## <a id="backend"></a>3. 🐍 STRUCTURE BACKEND DJANGO

### Projet Structure
```
learning_platform/
│
├── config/                      # Configuration principale
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py             # Settings communs
│   │   ├── development.py      # Dev overrides
│   │   └── production.py       # Prod overrides
│   ├── urls.py                 # URL root
│   ├── asgi.py                 # ASGI config (Channels)
│   └── wsgi.py                 # WSGI config (Gunicorn)
│
├── apps/
│   │
│   ├── accounts/               # Gestion utilisateurs
│   │   ├── models.py           # User, Profile
│   │   ├── views.py            # Auth endpoints
│   │   ├── serializers.py
│   │   ├── permissions.py
│   │   ├── services.py         # Business logic
│   │   └── tests/
│   │
│   ├── courses/                # Contenu pédagogique
│   │   ├── models.py
│   │   │   ├── Chapter
│   │   │   ├── Lesson
│   │   │   ├── Exercise
│   │   │   ├── Quiz
│   │   │   └── Project
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── admin.py            # Django Admin custom
│   │   ├── services.py
│   │   └── tests/
│   │
│   ├── progression/            # Suivi progression
│   │   ├── models.py
│   │   │   ├── UserProgress
│   │   │   ├── ChapterAccess
│   │   │   └── ActivityLog
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   │   └── progress_tracker.py
│   │   └── tests/
│   │
│   ├── gamification/           # Badges & Points
│   │   ├── models.py
│   │   │   ├── Badge
│   │   │   ├── UserBadge
│   │   │   ├── PointTransaction
│   │   │   └── Leaderboard
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── services.py
│   │   │   ├── badge_service.py
│   │   │   └── points_service.py
│   │   └── tests/
│   │
│   ├── forum/                  # Forum communauté
│   │   ├── models.py
│   │   │   ├── ForumPost
│   │   │   ├── ForumReply
│   │   │   └── Vote
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── tests/
│   │
│   └── validation/             # Validation code
│       ├── models.py
│       ├── services.py
│       │   ├── code_runner.py
│       │   ├── sandbox.py
│       │   └── test_executor.py
│       ├── tasks.py            # Celery tasks
│       └── tests/
│
├── channels/                   # WebSocket Consumers
│   ├── consumers/
│   │   ├── progress_consumer.py
│   │   ├── activity_consumer.py
│   │   └── notification_consumer.py
│   ├── middleware.py
│   └── routing.py
│
├── core/                       # Utilities partagées
│   ├── mixins.py
│   ├── exceptions.py
│   ├── validators.py
│   ├── pagination.py
│   └── permissions.py
│
├── static/
├── media/
├── templates/
│
├── requirements/
│   ├── base.txt
│   ├── development.txt
│   └── production.txt
│
├── docker/
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── nginx.conf
│
├── .env.example
├── manage.py
├── pytest.ini
└── README.md
```

### Settings Architecture

**base.py**
```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third party
    'rest_framework',
    'rest_framework_simplejwt',
    'channels',
    'corsheaders',
    'django_filters',
    
    # Local apps
    'apps.accounts',
    'apps.courses',
    'apps.progression',
    'apps.gamification',
    'apps.forum',
    'apps.validation',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTH_USER_MODEL = 'accounts.User'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'core.pagination.StandardPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}

# Channels
ASGI_APPLICATION = 'config.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(os.getenv('REDIS_HOST', 'localhost'), 6379)],
        },
    },
}

# Celery
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/2')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://localhost:6379/2')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

**production.py**
```python
from .base import *

DEBUG = False

ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT', '5432'),
        'CONN_MAX_AGE': 600,
    }
}

# Static files
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files (S3)
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME')

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
```

---

## <a id="frontend"></a>4. ⚛️ STRUCTURE FRONTEND REACT

### Projet Structure
```
frontend/
│
├── public/
│   ├── index.html
│   └── assets/
│
├── src/
│   │
│   ├── app/
│   │   ├── store.js              # Redux store configuration
│   │   └── rootReducer.js
│   │
│   ├── features/                 # Feature-based organization
│   │   │
│   │   ├── auth/
│   │   │   ├── authSlice.js      # Redux slice
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   └── PrivateRoute.jsx
│   │   │
│   │   ├── chapters/
│   │   │   ├── chaptersSlice.js
│   │   │   ├── ChapterList.jsx
│   │   │   ├── ChapterCard.jsx
│   │   │   └── ChapterProgress.jsx
│   │   │
│   │   ├── lessons/
│   │   │   ├── lessonsSlice.js
│   │   │   ├── LessonViewer.jsx
│   │   │   ├── LessonNavigation.jsx
│   │   │   └── MarkdownRenderer.jsx
│   │   │
│   │   ├── exercises/
│   │   │   ├── exercisesSlice.js
│   │   │   ├── CodeEditor.jsx     # Monaco Editor wrapper
│   │   │   ├── CodePreview.jsx
│   │   │   ├── TestResults.jsx
│   │   │   └── HintPanel.jsx
│   │   │
│   │   ├── quizzes/
│   │   │   ├── quizzesSlice.js
│   │   │   ├── QuizInterface.jsx
│   │   │   ├── Question.jsx
│   │   │   └── QuizResults.jsx
│   │   │
│   │   ├── progression/
│   │   │   ├── progressionSlice.js
│   │   │   ├── ProgressDashboard.jsx
│   │   │   ├── ProgressChart.jsx
│   │   │   └── ActivityTimeline.jsx
│   │   │
│   │   ├── gamification/
│   │   │   ├── gamificationSlice.js
│   │   │   ├── BadgeGallery.jsx
│   │   │   ├── Leaderboard.jsx
│   │   │   └── PointsDisplay.jsx
│   │   │
│   │   ├── forum/
│   │   │   ├── forumSlice.js
│   │   │   ├── ForumList.jsx
│   │   │   ├── PostDetail.jsx
│   │   │   └── ReplyForm.jsx
│   │   │
│   │   └── trainer/
│   │       ├── trainerSlice.js
│   │       ├── StudentList.jsx
│   │       ├── StudentDetail.jsx
│   │       ├── LiveActivity.jsx
│   │       └── ProjectReview.jsx
│   │
│   ├── components/               # Shared components
│   │   ├── layout/
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   └── Footer.jsx
│   │   ├── ui/
│   │   │   ├── Button.jsx
│   │   │   ├── Modal.jsx
│   │   │   ├── Toast.jsx
│   │   │   ├── Spinner.jsx
│   │   │   └── ProgressBar.jsx
│   │   └── common/
│   │       ├── ErrorBoundary.jsx
│   │       └── LazyLoad.jsx
│   │
│   ├── services/                 # API & External services
│   │   ├── api/
│   │   │   ├── apiService.js     # Axios instance & interceptors
│   │   │   ├── authApi.js
│   │   │   ├── chaptersApi.js
│   │   │   ├── exercisesApi.js
│   │   │   └── progressApi.js
│   │   │
│   │   ├── websocket/
│   │   │   ├── wsService.js      # WebSocket manager
│   │   │   └── wsMiddleware.js   # Redux middleware for WS
│   │   │
│   │   └── storage/
│   │       └── localStorageService.js
│   │
│   ├── hooks/                    # Custom React hooks
│   │   ├── useAuth.js
│   │   ├── useWebSocket.js
│   │   ├── useDebounce.js
│   │   ├── useAutosave.js
│   │   └── useProgress.js
│   │
│   ├── utils/                    # Utility functions
│   │   ├── validators.js
│   │   ├── formatters.js
│   │   ├── constants.js
│   │   └── helpers.js
│   │
│   ├── styles/
│   │   ├── index.css             # Tailwind imports
│   │   └── themes/
│   │
│   ├── App.jsx
│   ├── main.jsx
│   └── routes.jsx
│
├── .env.example
├── .eslintrc.js
├── .prettierrc
├── vite.config.js
├── tailwind.config.js
├── package.json
└── README.md
```

### Redux Store Configuration

**store.js**
```javascript
import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice';
import chaptersReducer from '../features/chapters/chaptersSlice';
import progressionReducer from '../features/progression/progressionSlice';
import gamificationReducer from '../features/gamification/gamificationSlice';
import wsMiddleware from '../services/websocket/wsMiddleware';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    chapters: chaptersReducer,
    progression: progressionReducer,
    gamification: gamificationReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(wsMiddleware),
});
```

**Example Slice: progressionSlice.js**
```javascript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { progressApi } from '../../services/api/progressApi';

export const fetchUserProgress = createAsyncThunk(
  'progression/fetchUserProgress',
  async (_, { rejectWithValue }) => {
    try {
      const response = await progressApi.getUserProgress();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response.data);
    }
  }
);

const progressionSlice = createSlice({
  name: 'progression',
  initialState: {
    currentProgress: null,
    chapters: [],
    loading: false,
    error: null,
    realTimeUpdates: [],
  },
  reducers: {
    updateProgressRealtime: (state, action) => {
      // WebSocket update
      state.realTimeUpdates.push(action.payload);
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchUserProgress.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchUserProgress.fulfilled, (state, action) => {
        state.loading = false;
        state.currentProgress = action.payload;
      })
      .addCase(fetchUserProgress.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});

export const { updateProgressRealtime, clearError } = progressionSlice.actions;
export default progressionSlice.reducer;
```

**WebSocket Service: wsService.js**
```javascript
import io from 'socket.io-client';
import { store } from '../../app/store';
import { updateProgressRealtime } from '../../features/progression/progressionSlice';

class WebSocketService {
  constructor() {
    this.socket = null;
    this.connected = false;
  }

  connect(token) {
    const wsUrl = import.meta.env.VITE_WS_URL;
    
    this.socket = io(wsUrl, {
      auth: { token },
      transports: ['websocket'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    this.socket.on('connect', () => {
      console.log('WebSocket connected');
      this.connected = true;
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected');
      this.connected = false;
    });

    this.socket.on('progress_update', (data) => {
      store.dispatch(updateProgressRealtime(data));
    });

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error);
    });
  }

  saveProgress(exerciseId, code) {
    if (!this.connected) {
      console.warn('WebSocket not connected');
      return;
    }
    
    this.socket.emit('save_progress', {
      exercise_id: exerciseId,
      code: code,
      timestamp: Date.now(),
    });
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.connected = false;
    }
  }
}

export default new WebSocketService();
```

**Auto-save Hook: useAutosave.js**
```javascript
import { useEffect, useRef } from 'use';
import { useDebounce } from './useDebounce';
import wsService from '../services/websocket/wsService';

export function useAutosave(exerciseId, code, delay = 3000) {
  const debouncedCode = useDebounce(code, delay);
  const savedRef = useRef(false);

  useEffect(() => {
    if (debouncedCode && exerciseId) {
      wsService.saveProgress(exerciseId, debouncedCode);
      savedRef.current = true;
      
      // Reset after showing "Saved" indicator
      setTimeout(() => {
        savedRef.current = false;
      }, 1000);
    }
  }, [debouncedCode, exerciseId]);

  return savedRef.current;
}
```

---

## <a id="database"></a>5. 🗄️ BASE DE DONNÉES

### Schéma PostgreSQL Détaillé

```sql
-- ============================================
-- TABLE: accounts_user (Custom User Model)
-- ============================================
CREATE TABLE accounts_user (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(150),
    last_name VARCHAR(150),
    role VARCHAR(20) NOT NULL CHECK (role IN ('LEARNER', 'TRAINER', 'ADMIN')),
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    date_joined TIMESTAMP DEFAULT NOW(),
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_email ON accounts_user(email);
CREATE INDEX idx_user_role ON accounts_user(role);

-- ============================================
-- TABLE: accounts_profile
-- ============================================
CREATE TABLE accounts_profile (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID UNIQUE NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    bio TEXT,
    avatar VARCHAR(255),
    total_points INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    timezone VARCHAR(50) DEFAULT 'UTC',
    github_username VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_profile_user ON accounts_profile(user_id);

-- ============================================
-- TABLE: courses_chapter
-- ============================================
CREATE TABLE courses_chapter (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    order_index INTEGER NOT NULL,
    estimated_duration INTEGER, -- minutes
    is_published BOOLEAN DEFAULT FALSE,
    created_by_id UUID REFERENCES accounts_user(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(order_index)
);

CREATE INDEX idx_chapter_order ON courses_chapter(order_index);
CREATE INDEX idx_chapter_published ON courses_chapter(is_published);

-- ============================================
-- TABLE: courses_lesson
-- ============================================
CREATE TABLE courses_lesson (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id UUID NOT NULL REFERENCES courses_chapter(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT, -- Markdown
    type VARCHAR(20) NOT NULL CHECK (type IN ('THEORY', 'EXERCISE', 'QUIZ')),
    order_index INTEGER NOT NULL,
    estimated_time INTEGER, -- minutes
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(chapter_id, order_index)
);

CREATE INDEX idx_lesson_chapter ON courses_lesson(chapter_id);
CREATE INDEX idx_lesson_type ON courses_lesson(type);

-- ============================================
-- TABLE: courses_exercise
-- ============================================
CREATE TABLE courses_exercise (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID UNIQUE NOT NULL REFERENCES courses_lesson(id) ON DELETE CASCADE,
    instructions TEXT NOT NULL,
    starter_code TEXT,
    solution_code TEXT,
    tests JSONB NOT NULL, -- Test cases structure
    max_attempts INTEGER DEFAULT 10,
    points INTEGER DEFAULT 50,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_exercise_lesson ON courses_exercise(lesson_id);

-- ============================================
-- TABLE: courses_quiz
-- ============================================
CREATE TABLE courses_quiz (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    lesson_id UUID UNIQUE NOT NULL REFERENCES courses_lesson(id) ON DELETE CASCADE,
    questions JSONB NOT NULL, -- Array of question objects
    passing_score INTEGER DEFAULT 70, -- percentage
    time_limit INTEGER, -- seconds, NULL = no limit
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_quiz_lesson ON courses_quiz(lesson_id);

-- ============================================
-- TABLE: progression_userprogress
-- ============================================
CREATE TABLE progression_userprogress (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    lesson_id UUID NOT NULL REFERENCES courses_lesson(id) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL CHECK (status IN ('NOT_STARTED', 'IN_PROGRESS', 'COMPLETED')),
    attempts INTEGER DEFAULT 0,
    score INTEGER,
    time_spent INTEGER DEFAULT 0, -- seconds
    last_code TEXT, -- For exercises
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, lesson_id)
);

CREATE INDEX idx_progress_user ON progression_userprogress(user_id);
CREATE INDEX idx_progress_lesson ON progression_userprogress(lesson_id);
CREATE INDEX idx_progress_status ON progression_userprogress(status);

-- ============================================
-- TABLE: progression_chapteraccess
-- ============================================
CREATE TABLE progression_chapteraccess (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    chapter_id UUID NOT NULL REFERENCES courses_chapter(id) ON DELETE CASCADE,
    is_unlocked BOOLEAN DEFAULT FALSE,
    unlocked_by_id UUID REFERENCES accounts_user(id),
    unlocked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, chapter_id)
);

CREATE INDEX idx_access_user ON progression_chapteraccess(user_id);
CREATE INDEX idx_access_chapter ON progression_chapteraccess(chapter_id);

-- ============================================
-- TABLE: progression_activitylog
-- ============================================
CREATE TABLE progression_activitylog (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    metadata JSONB,
    ip_address INET,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_activity_user ON progression_activitylog(user_id);
CREATE INDEX idx_activity_created ON progression_activitylog(created_at);

-- ============================================
-- TABLE: courses_project
-- ============================================
CREATE TABLE courses_project (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id UUID NOT NULL REFERENCES courses_chapter(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    files VARCHAR(255), -- S3 URL
    status VARCHAR(20) NOT NULL CHECK (status IN ('PENDING', 'REVIEWING', 'APPROVED', 'REJECTED')),
    submitted_at TIMESTAMP,
    reviewed_at TIMESTAMP,
    reviewed_by_id UUID REFERENCES accounts_user(id),
    feedback TEXT,
    grade INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_project_user ON courses_project(user_id);
CREATE INDEX idx_project_chapter ON courses_project(chapter_id);
CREATE INDEX idx_project_status ON courses_project(status);

-- ============================================
-- TABLE: gamification_badge
-- ============================================
CREATE TABLE gamification_badge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    icon VARCHAR(255), -- URL to icon
    criteria JSONB NOT NULL, -- Badge earning criteria
    points_reward INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- ============================================
-- TABLE: gamification_userbadge
-- ============================================
CREATE TABLE gamification_userbadge (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    badge_id UUID NOT NULL REFERENCES gamification_badge(id) ON DELETE CASCADE,
    earned_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(user_id, badge_id)
);

CREATE INDEX idx_userbadge_user ON gamification_userbadge(user_id);

-- ============================================
-- TABLE: gamification_pointtransaction
-- ============================================
CREATE TABLE gamification_pointtransaction (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    points INTEGER NOT NULL,
    reason VARCHAR(255),
    reference_type VARCHAR(50),
    reference_id UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_points_user ON gamification_pointtransaction(user_id);
CREATE INDEX idx_points_created ON gamification_pointtransaction(created_at);

-- ============================================
-- TABLE: forum_post
-- ============================================
CREATE TABLE forum_post (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chapter_id UUID REFERENCES courses_chapter(id) ON DELETE SET NULL,
    author_id UUID NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    is_solved BOOLEAN DEFAULT FALSE,
    votes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_post_chapter ON forum_post(chapter_id);
CREATE INDEX idx_post_author ON forum_post(author_id);
CREATE INDEX idx_post_created ON forum_post(created_at DESC);

-- ============================================
-- TABLE: forum_reply
-- ============================================
CREATE TABLE forum_reply (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    post_id UUID NOT NULL REFERENCES forum_post(id) ON DELETE CASCADE,
    author_id UUID NOT NULL REFERENCES accounts_user(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    is_solution BOOLEAN DEFAULT FALSE,
    votes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reply_post ON forum_reply(post_id);
CREATE INDEX idx_reply_author ON forum_reply(author_id);

-- ============================================
-- FUNCTIONS & TRIGGERS
-- ============================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply to all tables with updated_at
CREATE TRIGGER update_user_updated_at BEFORE UPDATE ON accounts_user
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chapter_updated_at BEFORE UPDATE ON courses_chapter
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ... (apply to all relevant tables)

-- ============================================
-- VIEWS (for common queries)
-- ============================================

-- View: User's chapter completion rate
CREATE VIEW v_user_chapter_progress AS
SELECT 
    u.id AS user_id,
    c.id AS chapter_id,
    c.title AS chapter_title,
    COUNT(l.id) AS total_lessons,
    COUNT(CASE WHEN up.status = 'COMPLETED' THEN 1 END) AS completed_lessons,
    ROUND(
        COUNT(CASE WHEN up.status = 'COMPLETED' THEN 1 END)::NUMERIC / 
        COUNT(l.id)::NUMERIC * 100, 
        2
    ) AS completion_percentage
FROM accounts_user u
CROSS JOIN courses_chapter c
LEFT JOIN courses_lesson l ON l.chapter_id = c.id
LEFT JOIN progression_userprogress up ON up.lesson_id = l.id AND up.user_id = u.id
WHERE u.role = 'LEARNER'
GROUP BY u.id, c.id, c.title;

-- View: Leaderboard
CREATE VIEW v_leaderboard AS
SELECT 
    u.id,
    u.first_name,
    u.last_name,
    p.total_points,
    p.level,
    COUNT(DISTINCT ub.badge_id) AS badges_count,
    ROW_NUMBER() OVER (ORDER BY p.total_points DESC) AS rank
FROM accounts_user u
JOIN accounts_profile p ON p.user_id = u.id
LEFT JOIN gamification_userbadge ub ON ub.user_id = u.id
WHERE u.role = 'LEARNER' AND u.is_active = TRUE
GROUP BY u.id, u.first_name, u.last_name, p.total_points, p.level
ORDER BY p.total_points DESC;
```

### Redis Data Structures

```
# User sessions (db0)
session:{user_id}:token → JWT token data (TTL: 24h)
session:{user_id}:active → boolean (TTL: 5min, updated on activity)

# Progress cache (db1)
progress:{user_id}:{lesson_id} → JSON (lesson progress snapshot)
cache:chapter:{id} → JSON (chapter data, TTL: 1h)
cache:lesson:{id} → JSON (lesson content, TTL: 30min)

# WebSocket channels (db0)
channel:chapter:{id}:users → Set of user_ids
channel:chapter:{id}:activity → JSON (recent activity)

# Celery task queue (db2)
celery:default → Task queue
celery:results:{task_id} → Task result (TTL: 1h)

# Rate limiting (db3)
ratelimit:api:{user_id}:{endpoint} → Counter (TTL: 1min)
ratelimit:ws:{user_id} → Counter (TTL: 1sec)
```

---

## <a id="api"></a>6. 🔌 API REST ENDPOINTS

### Authentication
```
POST   /api/auth/register/          # Register new user
POST   /api/auth/login/             # Login
POST   /api/auth/refresh/           # Refresh JWT token
POST   /api/auth/logout/            # Logout
POST   /api/auth/password-reset/    # Request password reset
POST   /api/auth/password-reset-confirm/ # Confirm password reset
GET    /api/auth/me/                # Get current user
PUT    /api/auth/me/                # Update current user
```

### Chapters & Lessons
```
GET    /api/chapters/                         # List all chapters
GET    /api/chapters/{id}/                    # Get chapter detail
POST   /api/chapters/                         # Create chapter (trainer only)
PUT    /api/chapters/{id}/                    # Update chapter
DELETE /api/chapters/{id}/                    # Delete chapter
GET    /api/chapters/{id}/lessons/            # Get chapter lessons
GET    /api/chapters/{id}/progress/           # Get user progress in chapter

GET    /api/lessons/{id}/                     # Get lesson detail
POST   /api/lessons/                          # Create lesson
PUT    /api/lessons/{id}/                     # Update lesson
DELETE /api/lessons/{id}/                     # Delete lesson
GET    /api/lessons/{id}/next/                # Get next lesson
```

### Exercises
```
GET    /api/exercises/{id}/                   # Get exercise detail
POST   /api/exercises/{id}/submit/            # Submit solution
POST   /api/exercises/{id}/validate/          # Validate code (async)
GET    /api/exercises/{id}/hints/             # Get hints
GET    /api/exercises/{id}/solution/          # Get solution (after attempts)
```

### Quizzes
```
GET    /api/quizzes/{id}/                     # Get quiz detail
POST   /api/quizzes/{id}/submit/              # Submit answers
GET    /api/quizzes/{id}/results/             # Get quiz results
```

### Progression
```
GET    /api/progression/                      # Get user overall progress
GET    /api/progression/chapters/{id}/        # Get chapter progress
POST   /api/progression/save/                 # Manual save (backup for WS)
GET    /api/progression/activity/             # Get recent activity
GET    /api/progression/stats/                # Get stats (time spent, etc.)
```

### Chapter Access (Trainer)
```
POST   /api/trainer/unlock/                   # Unlock chapter for user
GET    /api/trainer/students/                 # List students
GET    /api/trainer/students/{id}/            # Get student detail
GET    /api/trainer/students/{id}/progress/   # Get student progress
GET    /api/trainer/activity/                 # Real-time activity (polling fallback)
```

### Projects
```
GET    /api/projects/                         # List user's projects
GET    /api/projects/{id}/                    # Get project detail
POST   /api/projects/                         # Submit project
PUT    /api/projects/{id}/                    # Update project
GET    /api/projects/{id}/download/           # Download project files
POST   /api/projects/{id}/review/             # Review project (trainer)
```

### Gamification
```
GET    /api/badges/                           # List all badges
GET    /api/badges/earned/                    # Get user's earned badges
GET    /api/points/history/                   # Get points history
GET    /api/leaderboard/                      # Get leaderboard
GET    /api/leaderboard/weekly/               # Get weekly leaderboard
```

### Forum
```
GET    /api/forum/posts/                      # List posts
POST   /api/forum/posts/                      # Create post
GET    /api/forum/posts/{id}/                 # Get post detail
PUT    /api/forum/posts/{id}/                 # Update post
DELETE /api/forum/posts/{id}/                 # Delete post
POST   /api/forum/posts/{id}/replies/         # Reply to post
POST   /api/forum/posts/{id}/vote/            # Vote on post
POST   /api/forum/replies/{id}/vote/          # Vote on reply
POST   /api/forum/replies/{id}/mark-solution/ # Mark as solution
```

### Common Query Parameters
```
?page=1                    # Pagination
?page_size=20              # Items per page
?search=keyword            # Full-text search
?ordering=-created_at      # Sorting
?chapter=uuid              # Filter by chapter
?status=COMPLETED          # Filter by status
```

### Response Format
```json
// Success (200, 201)
{
  "data": { ... },
  "meta": {
    "timestamp": "2025-01-15T10:30:00Z"
  }
}

// List with pagination (200)
{
  "count": 42,
  "next": "http://api/resource/?page=2",
  "previous": null,
  "results": [ ... ]
}

// Error (400, 401, 403, 404, 500)
{
  "error": {
    "code": "INVALID_INPUT",
    "message": "Email is required",
    "details": {
      "email": ["This field is required"]
    }
  }
}
```

---

## <a id="websocket"></a>7. 📡 WEBSOCKET ARCHITECTURE

### WebSocket Endpoints
```
ws://api.example.com/ws/progress/{exercise_id}/
ws://api.example.com/ws/activity/chapter/{chapter_id}/
ws://api.example.com/ws/notifications/
```

### Message Format

**Client → Server**
```json
{
  "type": "save_progress",
  "data": {
    "exercise_id": "uuid",
    "code": "const x = 42;",
    "timestamp": 1705320600
  }
}

{
  "type": "join_chapter",
  "data": {
    "chapter_id": "uuid"
  }
}
```

**Server → Client**
```json
{
  "type": "progress_saved",
  "data": {
    "exercise_id": "uuid",
    "saved_at": "2025-01-15T10:30:00Z",
    "version": 5
  }
}

{
  "type": "user_activity",
  "data": {
    "user_id": "uuid",
    "user_name": "Alex",
    "action": "started_lesson",
    "lesson_id": "uuid",
    "timestamp": "2025-01-15T10:30:00Z"
  }
}

{
  "type": "chapter_unlocked",
  "data": {
    "chapter_id": "uuid",
    "chapter_title": "JavaScript Basics",
    "unlocked_by": "Sophie (Trainer)"
  }
}

{
  "type": "badge_earned",
  "data": {
    "badge_id": "uuid",
    "badge_name": "First Steps",
    "badge_icon": "url",
    "points": 100
  }
}
```

### Django Channels Consumer Example

```python
# channels/consumers/progress_consumer.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.cache import cache

class ProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.exercise_id = self.scope['url_route']['kwargs']['exercise_id']
        self.user = self.scope['user']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Join exercise group
        self.room_group_name = f'exercise_{self.exercise_id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        # Join user's personal channel (for notifications)
        self.user_group_name = f'user_{self.user.id}'
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'exercise_id': str(self.exercise_id)
        }))
    
    async def disconnect(self, close_code):
        # Leave groups
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'save_progress':
            await self.save_progress(data['data'])
        elif message_type == 'submit_solution':
            await self.submit_solution(data['data'])
    
    async def save_progress(self, data):
        """Save progress to Redis cache, batch write to DB"""
        code = data.get('code')
        timestamp = data.get('timestamp')
        
        # Cache in Redis immediately
        cache_key = f'progress:{self.user.id}:{self.exercise_id}'
        cache.set(cache_key, {
            'code': code,
            'timestamp': timestamp,
            'saved': True
        }, timeout=3600)  # 1 hour
        
        # Queue DB write (debounced)
        from apps.progression.tasks import save_progress_to_db
        save_progress_to_db.apply_async(
            args=[self.user.id, self.exercise_id, code],
            countdown=10  # Batch writes every 10 seconds
        )
        
        # Send confirmation
        await self.send(text_data=json.dumps({
            'type': 'progress_saved',
            'data': {
                'exercise_id': str(self.exercise_id),
                'saved_at': timestamp,
            }
        }))
    
    async def submit_solution(self, data):
        """Trigger validation task"""
        code = data.get('code')
        
        from apps.validation.tasks import validate_exercise_solution
        task = validate_exercise_solution.delay(
            str(self.user.id),
            str(self.exercise_id),
            code
        )
        
        await self.send(text_data=json.dumps({
            'type': 'validation_queued',
            'data': {
                'task_id': task.id
            }
        }))
    
    # Event handlers (called by channel layer)
    async def validation_result(self, event):
        """Send validation result to client"""
        await self.send(text_data=json.dumps({
            'type': 'validation_result',
            'data': event['data']
        }))
    
    async def badge_earned(self, event):
        """Notify user of earned badge"""
        await self.send(text_data=json.dumps({
            'type': 'badge_earned',
            'data': event['data']
        }))
```

---

## <a id="security"></a>8. 🔒 SÉCURITÉ

### Authentication & Authorization

**JWT Configuration**
```python
# settings.py

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
}
```

**Custom Permissions**
```python
# core/permissions.py

from rest_framework import permissions

class IsTrainerOrReadOnly(permissions.BasePermission):
    """
    Only trainers can modify content.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.role == 'TRAINER'

class IsOwnerOrTrainer(permissions.BasePermission):
    """
    Object-level permission.
    """
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'TRAINER':
            return True
        return obj.user == request.user
```

### Input Validation & Sanitization

**Django Serializers**
```python
# apps/courses/serializers.py

from rest_framework import serializers
from .models import Exercise

class ExerciseSubmissionSerializer(serializers.Serializer):
    code = serializers.CharField(
        max_length=50000,  # 50KB limit
        trim_whitespace=False,
        required=True
    )
    
    def validate_code(self, value):
        # Check for potentially dangerous code
        dangerous_patterns = [
            'eval(', 'exec(', '__import__',
            'os.system', 'subprocess', 'open('
        ]
        
        for pattern in dangerous_patterns:
            if pattern in value:
                raise serializers.ValidationError(
                    f"Dangerous code pattern detected: {pattern}"
                )
        
        return value
```

### Code Execution Sandbox

**Docker Sandbox**
```python
# apps/validation/services/sandbox.py

import docker
import tempfile
import os

class CodeSandbox:
    def __init__(self):
        self.client = docker.from_env()
        self.image = 'python:3.11-alpine'
        
    def execute(self, code, tests, timeout=5):
        """Execute code in isolated Docker container"""
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Write code to temp file
            code_file = os.path.join(tmpdir, 'solution.py')
            with open(code_file, 'w') as f:
                f.write(code)
            
            # Write tests
            test_file = os.path.join(tmpdir, 'test.py')
            with open(test_file, 'w') as f:
                f.write(tests)
            
            try:
                # Run container
                result = self.client.containers.run(
                    self.image,
                    command='python test.py',
                    volumes={tmpdir: {'bind': '/code', 'mode': 'ro'}},
                    working_dir='/code',
                    network_mode='none',  # No network access
                    mem_limit='128m',     # 128MB memory limit
                    cpu_period=100000,
                    cpu_quota=50000,      # 50% CPU
                    remove=True,
                    timeout=timeout,
                    stdout=True,
                    stderr=True
                )
                
                return {
                    'success': True,
                    'output': result.decode('utf-8')
                }
                
            except docker.errors.ContainerError as e:
                return {
                    'success': False,
                    'error': e.stderr.decode('utf-8')
                }
            except Exception as e:
                return {
                    'success': False,
                    'error': str(e)
                }
```

### Rate Limiting

**DRF Throttling**
```python
# settings.py

REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'submit': '10/minute',  # Custom rate for submissions
    }
}
```

**Custom Throttle**
```python
# core/throttling.py

from rest_framework.throttling import UserRateThrottle

class SubmissionRateThrottle(UserRateThrottle):
    scope = 'submit'
    
    def allow_request(self, request, view):
        # More strict for expensive operations
        if request.method == 'POST':
            return super().allow_request(request, view)
        return True
```

### CSRF & CORS

```python
# settings.py

# CORS
CORS_ALLOWED_ORIGINS = [
    'https://app.example.com',
    'http://localhost:5173',  # Dev
]
CORS_ALLOW_CREDENTIALS = True

# CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://app.example.com',
]
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SECURE = True
```

### SQL Injection Prevention
- **Always use Django ORM** (parameterized queries)
- Never use raw SQL with user input
- If raw SQL needed: use `params` parameter

```python
# ❌ WRONG
Chapter.objects.raw(f"SELECT * FROM chapters WHERE id = {user_input}")

# ✅ CORRECT
Chapter.objects.raw("SELECT * FROM chapters WHERE id = %s", [user_input])
```

### XSS Prevention
- Django templates auto-escape by default
- React also escapes by default
- Markdown content: use `bleach` library

```python
# apps/courses/serializers.py

import bleach

ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'code', 'pre', 'h1', 'h2', 'h3']

class LessonSerializer(serializers.ModelSerializer):
    def validate_content(self, value):
        # Sanitize HTML/Markdown
        cleaned = bleach.clean(value, tags=ALLOWED_TAGS)
        return cleaned
```

---

## <a id="performance"></a>9. ⚡ PERFORMANCE & SCALABILITÉ

### Database Optimization

**Query Optimization**
```python
# ❌ N+1 Query Problem
chapters = Chapter.objects.all()
for chapter in chapters:
    print(chapter.lessons.count())  # Query per chapter!

# ✅ Optimized with select_related / prefetch_related
chapters = Chapter.objects.prefetch_related('lessons').all()
for chapter in chapters:
    print(chapter.lessons.count())  # No extra queries
```

**Indexes**
```sql
-- Already covered in database section
CREATE INDEX idx_progress_user_lesson ON progression_userprogress(user_id, lesson_id);
CREATE INDEX idx_activity_created ON progression_activitylog(created_at DESC);
```

**Connection Pooling**
```python
# Use PgBouncer in production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_MAX_AGE': 600,  # Keep connections alive
        'OPTIONS': {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000',  # 30s query timeout
        },
    }
}
```

### Caching Strategy

**Multi-Level Caching**
```python
# apps/courses/services.py

from django.core.cache import cache
from django.views.decorators.cache import cache_page

class ChapterService:
    @staticmethod
    def get_chapter_with_lessons(chapter_id):
        cache_key = f'chapter:{chapter_id}:full'
        
        # Try L1 cache (Redis)
        cached = cache.get(cache_key)
        if cached:
            return cached
        
        # Query DB with optimization
        chapter = Chapter.objects.prefetch_related(
            'lessons__exercise',
            'lessons__quiz'
        ).get(id=chapter_id)
        
        # Serialize and cache
        from .serializers import ChapterDetailSerializer
        data = ChapterDetailSerializer(chapter).data
        
        # Cache for 30 minutes
        cache.set(cache_key, data, timeout=1800)
        
        return data
```

**Cache Invalidation**
```python
# apps/courses/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

@receiver(post_save, sender=Chapter)
@receiver(post_delete, sender=Chapter)
def invalidate_chapter_cache(sender, instance, **kwargs):
    cache_key = f'chapter:{instance.id}:full'
    cache.delete(cache_key)
    
    # Also invalidate chapter list
    cache.delete('chapters:list:all')
```

### Celery Task Optimization

**Task Configuration**
```python
# config/celery.py

from celery import Celery

app = Celery('learning_platform')

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    
    # Task routing
    task_routes={
        'apps.validation.tasks.*': {'queue': 'validation'},
        'apps.gamification.tasks.*': {'queue': 'gamification'},
    },
    
    # Retry policy
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    
    # Result backend
    result_backend_transport_options={
        'global_keyprefix': 'celery_results_',
    },
    result_expires=3600,  # 1 hour
)
```

**Task Example with Retry**
```python
# apps/validation/tasks.py

from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1 minute
    time_limit=30,  # Hard limit 30s
    soft_time_limit=25  # Soft limit 25s
)
def validate_exercise_solution(self, user_id, exercise_id, code):
    try:
        from apps.validation.services import CodeValidator
        validator = CodeValidator()
        
        result = validator.validate(exercise_id, code)
        
        # Notify user via WebSocket
        from channels.layers import get_channel_layer
        from asgiref.sync import async_to_sync
        
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{user_id}',
            {
                'type': 'validation_result',
                'data': result
            }
        )
        
        return result
        
    except Exception as exc:
        logger.error(f"Validation failed: {exc}")
        raise self.retry(exc=exc)
```

### Frontend Performance

**Code Splitting**
```javascript
// routes.jsx

import { lazy, Suspense } from 'react';

const ChapterList = lazy(() => import('./features/chapters/ChapterList'));
const CodeEditor = lazy(() => import('./features/exercises/CodeEditor'));

export const routes = [
  {
    path: '/chapters',
    element: (
      <Suspense fallback={<Spinner />}>
        <ChapterList />
      </Suspense>
    ),
  },
  // ...
];
```

**Memoization**
```javascript
// components/ChapterCard.jsx

import { memo } from 'react';

const ChapterCard = memo(({ chapter, onSelect }) => {
  // Component only re-renders if chapter or onSelect changes
  return (
    <div onClick={() => onSelect(chapter.id)}>
      <h3>{chapter.title}</h3>
      <ProgressBar value={chapter.completion} />
    </div>
  );
});
```

**Debouncing & Throttling**
```javascript
// hooks/useDebounce.js

import { useState, useEffect } from 'react';

export function useDebounce(value, delay = 500) {
  const [debouncedValue, setDebouncedValue] = useState(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}
```

### Load Testing

**Locust Configuration**
```python
# locustfile.py

from locust import HttpUser, task, between
import json

class LearningPlatformUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post('/api/auth/login/', json={
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.token = response.json()['access']
        self.headers = {'Authorization': f'Bearer {self.token}'}
    
    @task(3)
    def view_chapters(self):
        self.client.get('/api/chapters/', headers=self.headers)
    
    @task(2)
    def view_lesson(self):
        self.client.get('/api/lessons/uuid/', headers=self.headers)
    
    @task(1)
    def submit_exercise(self):
        self.client.post(
            '/api/exercises/uuid/submit/',
            headers=self.headers,
            json={'code': 'console.log("hello");'}
        )

# Run: locust -f locustfile.py --host=http://localhost:8000
```

---

## <a id="devops"></a>10. 🚀 DEVOPS & DÉPLOIEMENT

### Docker Configuration

**Dockerfile (Backend)**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements/production.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput

# Run migrations and start server
CMD ["sh", "-c", "python manage.py migrate && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4"]
```

**docker-compose.yml**
```yaml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: learning_platform
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
      - redis

  daphne:
    build:
      context: .
      dockerfile: Dockerfile
    command: daphne -b 0.0.0.0 -p 8001 config.asgi:application
    ports:
      - "8001:8001"
    env_file:
      - .env
    depends_on:
      - db
      - redis

  celery:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A config worker -l info -Q default,validation
    env_file:
      - .env
    depends_on:
      - db
      - redis

  celery-beat:
    build:
      context: .
      dockerfile: Dockerfile
    command: celery -A config beat -l info
    env_file:
      - .env
    depends_on:
      - redis

  nginx:
    image: nginx:alpine
    volumes:
      - ./docker/nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/static
      - media_volume:/media
    ports:
      - "80:80"
    depends_on:
      - backend
      - daphne

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:
```

### CI/CD Pipeline

**GitHub Actions (.github/workflows/deploy.yml)**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements/development.txt
      
      - name: Run linting
        run: |
          flake8 .
          black --check .
      
      - name: Run tests
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost/test_db
        run: |
          pytest --cov=apps --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: docker build -t learning-platform:${{ github.sha }} .
      
      - name: Push to Registry
        run: |
          echo ${{ secrets.REGISTRY_PASSWORD }} | docker login -u ${{ secrets.REGISTRY_USERNAME }} --password-stdin
          docker tag learning-platform:${{ github.sha }} registry.example.com/learning-platform:latest
          docker push registry.example.com/learning-platform:latest

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - name: Deploy to Railway
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
        run: |
          npm install -g @railway/cli
          railway up
```

### Environment Variables

**.env.example**
```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=api.example.com,www.example.com

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/learning_platform

# Redis
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/2
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=learning-platform-media
AWS_S3_REGION_NAME=eu-west-3

# Email
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your-sendgrid-api-key

# Sentry
SENTRY_DSN=https://xxx@sentry.io/xxx

# Frontend
VITE_API_URL=https://api.example.com
VITE_WS_URL=wss://api.example.com
```

### Monitoring & Logging

**Sentry Integration**
```python
# config/settings/production.py

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration

sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[
        DjangoIntegration(),
        CeleryIntegration(),
    ],
    traces_sample_rate=0.1,  # 10% of transactions
    send_default_pii=False,
    environment=os.getenv('ENVIRONMENT', 'production'),
)
```

**Custom Logging**
```python
# config/settings/base.py

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/django.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
```

---

## ✅ CHECKLIST AVANT DÉPLOIEMENT

### Sécurité
- [ ] `DEBUG = False` en production
- [ ] `SECRET_KEY` unique et sécurisé
- [ ] HTTPS activé (certificat SSL)
- [ ] CORS configuré correctement
- [ ] Rate limiting actif
- [ ] Permissions Django configurées
- [ ] JWT tokens sécurisés
- [ ] Sandbox code execution testé

### Performance
- [ ] Indexes DB créés
- [ ] Caching configuré (Redis)
- [ ] Static files optimisés
- [ ] Celery workers dimensionnés
- [ ] Connection pooling actif
- [ ] Load testing effectué

### Monitoring
- [ ] Sentry configuré
- [ ] Logs centralisés
- [ ] Alertes configurées
- [ ] Backup automatique DB
- [ ] Health checks actifs

### Documentation
- [ ] API documentée (Swagger)
- [ ] README à jour
- [ ] Variables d'environnement documentées
- [ ] Guide de déploiement écrit

---

Ce document fournit une base solide pour l'architecture technique. Il sera mis à jour au fur et à mesure de l'évolution du projet.
