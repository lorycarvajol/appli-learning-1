# 🚀 GUIDE DE DÉVELOPPEMENT INITIAL

## 📋 RÉSUMÉ EXÉCUTIF

Ce guide vous accompagne pas à pas dans la mise en place de la plateforme d'apprentissage web, du setup initial jusqu'au premier déploiement. Suivez les étapes dans l'ordre pour un démarrage optimal.

**Durée estimée du setup complet :** 2-3 jours  
**Prérequis :** Connaissance de base en Django, React, et Docker

---

## 🎯 OBJECTIFS DU SPRINT 0

Avant de commencer le développement des fonctionnalités, nous devons :
1. ✅ Configurer l'environnement de développement
2. ✅ Mettre en place l'infrastructure de base (Django + PostgreSQL + Redis)
3. ✅ Créer le modèle User custom
4. ✅ Configurer l'authentification JWT
5. ✅ Initialiser le projet React avec Redux
6. ✅ Établir la communication API REST
7. ✅ Tester l'ensemble avec un endpoint simple

---

## 📦 ÉTAPE 1 : SETUP ENVIRONNEMENT LOCAL

### 1.1 Prérequis Système

Vérifiez que vous avez installé :
```bash
# Python 3.11+
python --version

# Node.js 18+ et npm
node --version
npm --version

# Docker et Docker Compose
docker --version
docker-compose --version

# Git
git --version

# PostgreSQL client (optionnel, pour debug)
psql --version
```

Si manquant, installez :
- **Python :** https://www.python.org/downloads/
- **Node.js :** https://nodejs.org/
- **Docker :** https://www.docker.com/get-started
- **Git :** https://git-scm.com/downloads

### 1.2 Cloner le Repository

```bash
# Créer le dossier projet
mkdir learning-platform
cd learning-platform

# Initialiser Git
git init
git remote add origin https://github.com/votre-org/learning-platform.git

# Créer structure
mkdir backend frontend docs

# Créer .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/

# Django
*.log
db.sqlite3
media/
staticfiles/

# Environment
.env
.env.local

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
dist/
build/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Celery
celerybeat-schedule
EOF

git add .
git commit -m "Initial commit: project structure"
```

---

## 🐍 ÉTAPE 2 : CONFIGURATION BACKEND DJANGO

### 2.1 Créer Environnement Virtuel Python

```bash
cd backend

# Créer venv
python -m venv venv

# Activer venv
# Sur macOS/Linux :
source venv/bin/activate
# Sur Windows :
venv\Scripts\activate

# Vérifier activation
which python  # Devrait pointer vers venv/bin/python
```

### 2.2 Installer Django et Dépendances

```bash
# Créer fichier requirements
mkdir requirements
```

**requirements/base.txt**
```
Django==5.0.3
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.1
django-cors-headers==4.3.1
django-filter==23.5
psycopg2-binary==2.9.9
python-decouple==3.8
channels==4.0.0
channels-redis==4.2.0
redis==5.0.1
celery==5.3.6
celery[redis]
Pillow==10.2.0
bleach==6.1.0
markdown==3.5.2
```

**requirements/development.txt**
```
-r base.txt

# Dev tools
django-debug-toolbar==4.3.0
pytest==8.0.0
pytest-django==4.7.0
pytest-cov==4.1.0
factory-boy==3.3.0
faker==22.6.0
black==24.1.1
flake8==7.0.0
isort==5.13.2
ipython==8.21.0
```

```bash
# Installer
pip install -r requirements/development.txt

# Figer versions exactes
pip freeze > requirements/freeze.txt
```

### 2.3 Créer Projet Django

```bash
# Créer projet
django-admin startproject config .

# Structure obtenue :
# backend/
# ├── config/
# │   ├── __init__.py
# │   ├── settings.py
# │   ├── urls.py
# │   ├── asgi.py
# │   └── wsgi.py
# ├── manage.py
# └── venv/
```

### 2.4 Restructurer Settings

```bash
# Créer structure settings modulaire
cd config
mkdir settings
mv settings.py settings/base.py
```

**config/settings/__init__.py**
```python
from decouple import config

ENVIRONMENT = config('ENVIRONMENT', default='development')

if ENVIRONMENT == 'production':
    from .production import *
else:
    from .development import *
```

**config/settings/base.py**
```python
from pathlib import Path
from decouple import config
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config('SECRET_KEY', default='django-insecure-temporary-key-change-in-production')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'channels',
    
    # Local apps (à créer)
    # 'apps.accounts',
    # 'apps.courses',
    # etc.
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

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database (sera override en development.py et production.py)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='learning_platform'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='postgres'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Internationalization
LANGUAGE_CODE = 'fr-fr'
TIME_ZONE = 'Europe/Paris'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

# JWT Settings
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# Channels
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(config('REDIS_HOST', default='localhost'), 6379)],
        },
    },
}

# Celery
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/2')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/2')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

**config/settings/development.py**
```python
from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# CORS for local React dev server
CORS_ALLOWED_ORIGINS = [
    'http://localhost:5173',
    'http://127.0.0.1:5173',
]
CORS_ALLOW_CREDENTIALS = True

# Debug toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
INTERNAL_IPS = ['127.0.0.1']

# Email backend (console for dev)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**config/settings/production.py**
```python
from .base import *

DEBUG = False

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='').split(',')

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# CORS
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='').split(',')

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# Static files storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 2.5 Créer `.env` pour Development

**backend/.env**
```bash
ENVIRONMENT=development
SECRET_KEY=dev-secret-key-change-in-production
DEBUG=True

# Database
DB_NAME=learning_platform
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis
REDIS_HOST=localhost
REDIS_URL=redis://localhost:6379/1

# Celery
CELERY_BROKER_URL=redis://localhost:6379/2
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### 2.6 Créer App `accounts`

```bash
cd ..  # retour à backend/
mkdir apps
cd apps
mkdir accounts
cd accounts

# Créer structure manuelle (ou utiliser startapp puis déplacer)
touch __init__.py models.py views.py serializers.py urls.py admin.py tests.py
```

**apps/accounts/models.py**
```python
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
import uuid

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('LEARNER', 'Apprenant'),
        ('TRAINER', 'Formateur'),
        ('ADMIN', 'Administrateur'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='LEARNER')
    
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'accounts_user'
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class Profile(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    total_points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    timezone = models.CharField(max_length=50, default='UTC')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_profile'
    
    def __str__(self):
        return f"Profile of {self.user.email}"
```

**apps/accounts/serializers.py**
```python
from rest_framework import serializers
from .models import User, Profile

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'avatar', 'total_points', 'level', 'timezone']
        read_only_fields = ['total_points', 'level']


class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'date_joined', 'profile']
        read_only_fields = ['id', 'date_joined', 'role']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'password_confirm', 'first_name', 'last_name']
    
    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        Profile.objects.create(user=user)  # Auto-create profile
        return user
```

**apps/accounts/views.py**
```python
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import User
from .serializers import RegisterSerializer, UserSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'user': UserSerializer(user).data,
            'message': 'User created successfully'
        }, status=status.HTTP_201_CREATED)


class CurrentUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return self.request.user
```

**apps/accounts/urls.py**
```python
from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, CurrentUserView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', CurrentUserView.as_view(), name='current_user'),
]
```

**apps/accounts/admin.py**
```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Profile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'first_name', 'last_name', 'role', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role'),
        }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_points', 'level', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
```

### 2.7 Mettre à jour URLs Principal

**config/urls.py**
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Debug toolbar
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
```

### 2.8 Ajouter AUTH_USER_MODEL

Dans **config/settings/base.py**, ajouter :
```python
AUTH_USER_MODEL = 'accounts.User'
```

Et dans **INSTALLED_APPS** :
```python
INSTALLED_APPS = [
    # ...
    'apps.accounts',
]
```

---

## 🗄️ ÉTAPE 3 : SETUP BASE DE DONNÉES

### 3.1 Démarrer PostgreSQL et Redis avec Docker

**docker-compose.yml** (à la racine du projet)
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: learning_platform
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

```bash
# Démarrer les services
docker-compose up -d

# Vérifier que tout tourne
docker-compose ps
```

### 3.2 Créer et Appliquer Migrations

```bash
cd backend

# Créer migrations
python manage.py makemigrations

# Appliquer migrations
python manage.py migrate

# Créer superuser
python manage.py createsuperuser
# Email: admin@example.com
# Password: admin123
```

### 3.3 Tester Django Admin

```bash
# Lancer serveur
python manage.py runserver

# Ouvrir http://localhost:8000/admin
# Login avec superuser créé
```

---

## ⚛️ ÉTAPE 4 : SETUP FRONTEND REACT

### 4.1 Initialiser Projet Vite + React

```bash
cd ../frontend

# Créer projet Vite
npm create vite@latest . -- --template react

# Installer dépendances
npm install

# Installer Redux Toolkit et autres libs
npm install @reduxjs/toolkit react-redux react-router-dom axios
npm install @monaco-editor/react socket.io-client
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

### 4.2 Configurer Tailwind CSS

**tailwind.config.js**
```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

**src/index.css**
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 4.3 Structure Projet React

```bash
cd src
mkdir -p app features/{auth,chapters} components/{layout,ui} services/{api,websocket} hooks utils

# Créer fichiers de base
touch app/{store.js,rootReducer.js}
touch features/auth/{authSlice.js,Login.jsx,Register.jsx}
touch services/api/apiService.js
touch services/websocket/wsService.js
```

### 4.4 Configuration Redux Store

**src/app/store.js**
```javascript
import { configureStore } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
  },
});
```

**src/app/rootReducer.js**
```javascript
import { combineReducers } from '@reduxjs/toolkit';
import authReducer from '../features/auth/authSlice';

const rootReducer = combineReducers({
  auth: authReducer,
});

export default rootReducer;
```

### 4.5 Auth Slice Redux

**src/features/auth/authSlice.js**
```javascript
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import { authApi } from '../../services/api/authApi';

export const login = createAsyncThunk(
  'auth/login',
  async ({ email, password }, { rejectWithValue }) => {
    try {
      const response = await authApi.login(email, password);
      localStorage.setItem('accessToken', response.data.access);
      localStorage.setItem('refreshToken', response.data.refresh);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Login failed');
    }
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async (userData, { rejectWithValue }) => {
    try {
      const response = await authApi.register(userData);
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data || 'Registration failed');
    }
  }
);

export const fetchCurrentUser = createAsyncThunk(
  'auth/fetchCurrentUser',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authApi.getCurrentUser();
      return response.data;
    } catch (error) {
      return rejectWithValue(error.response?.data);
    }
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState: {
    user: null,
    isAuthenticated: false,
    loading: false,
    error: null,
  },
  reducers: {
    logout: (state) => {
      state.user = null;
      state.isAuthenticated = false;
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.isAuthenticated = true;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Register
      .addCase(register.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state) => {
        state.loading = false;
      })
      .addCase(register.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      })
      // Fetch current user
      .addCase(fetchCurrentUser.fulfilled, (state, action) => {
        state.user = action.payload;
        state.isAuthenticated = true;
      });
  },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;
```

### 4.6 API Service

**src/services/api/apiService.js**
```javascript
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor (add token)
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor (handle 401)
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const refreshToken = localStorage.getItem('refreshToken');
        const response = await axios.post(`${API_URL}/auth/refresh/`, {
          refresh: refreshToken,
        });
        
        const newAccessToken = response.data.access;
        localStorage.setItem('accessToken', newAccessToken);
        
        originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
```

**src/services/api/authApi.js**
```javascript
import apiClient from './apiService';

export const authApi = {
  login: (email, password) =>
    apiClient.post('/auth/login/', { email, password }),
  
  register: (userData) =>
    apiClient.post('/auth/register/', userData),
  
  getCurrentUser: () =>
    apiClient.get('/auth/me/'),
  
  logout: () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
  },
};
```

### 4.7 Composants Login & Register

**src/features/auth/Login.jsx**
```javascript
import { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useNavigate, Link } from 'react-router-dom';
import { login } from './authSlice';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const dispatch = useDispatch();
  const navigate = useNavigate();
  const { loading, error } = useSelector((state) => state.auth);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await dispatch(login({ email, password }));
    
    if (login.fulfilled.match(result)) {
      navigate('/dashboard');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="max-w-md w-full bg-white p-8 rounded-lg shadow-md">
        <h2 className="text-2xl font-bold mb-6 text-center">Connexion</h2>
        
        {error && (
          <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">
            {error.detail || 'Erreur de connexion'}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-gray-700 mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <div className="mb-6">
            <label className="block text-gray-700 mb-2">Mot de passe</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>
          
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Connexion...' : 'Se connecter'}
          </button>
        </form>
        
        <p className="mt-4 text-center text-gray-600">
          Pas encore de compte ?{' '}
          <Link to="/register" className="text-blue-600 hover:underline">
            S'inscrire
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Login;
```

### 4.8 App.jsx Principal

**src/App.jsx**
```javascript
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from './app/store';
import Login from './features/auth/Login';
import Register from './features/auth/Register';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <Provider store={store}>
      <Router>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/" element={<Navigate to="/login" replace />} />
        </Routes>
      </Router>
    </Provider>
  );
}

export default App;
```

### 4.9 Créer .env Frontend

**frontend/.env**
```
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8001
```

---

## ✅ ÉTAPE 5 : TESTER L'INTÉGRATION

### 5.1 Lancer Backend

```bash
cd backend

# Terminal 1 : Django
python manage.py runserver

# Terminal 2 : Celery (optionnel pour l'instant)
celery -A config worker -l info
```

### 5.2 Lancer Frontend

```bash
cd frontend

npm run dev

# Ouvre http://localhost:5173
```

### 5.3 Test End-to-End

1. **Ouvrir http://localhost:5173**
2. **Aller sur /register**
3. **Créer un compte :**
   - Email: test@example.com
   - Mot de passe: testpass123
   - Prénom: Test
   - Nom: User
4. **Se connecter avec ces identifiants**
5. **Vérifier que le token est stocké (DevTools > Application > LocalStorage)**
6. **Vérifier le backend :**
   ```bash
   # Dans backend/
   python manage.py shell
   ```
   ```python
   from apps.accounts.models import User
   User.objects.all()
   # Devrait afficher le user créé
   ```

---

## 📝 ÉTAPE 6 : PREMIERS TESTS

### 6.1 Tests Backend (Pytest)

**backend/pytest.ini**
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.development
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

**apps/accounts/tests/test_models.py**
```python
import pytest
from apps.accounts.models import User, Profile

@pytest.mark.django_db
def test_create_user():
    user = User.objects.create_user(
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    
    assert user.email == 'test@example.com'
    assert user.check_password('testpass123')
    assert user.role == 'LEARNER'
    assert Profile.objects.filter(user=user).exists()

@pytest.mark.django_db
def test_create_superuser():
    user = User.objects.create_superuser(
        email='admin@example.com',
        password='adminpass123'
    )
    
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.role == 'ADMIN'
```

**Lancer tests**
```bash
cd backend
pytest
```

### 6.2 Tests Frontend (Vitest - optionnel)

```bash
cd frontend
npm install -D vitest @testing-library/react @testing-library/jest-dom
```

---

## 🎉 ÉTAPE 7 : COMMIT INITIAL

```bash
# À la racine du projet
git add .
git commit -m "feat: initial setup with Django + React + authentication"
git push origin main
```

---

## 📚 PROCHAINES ÉTAPES

Maintenant que l'infrastructure de base est en place, vous pouvez commencer le **Sprint 1.2** :

1. **Créer app `courses`** avec modèles Chapter, Lesson, Exercise, Quiz
2. **Créer API endpoints** pour lister/créer du contenu
3. **Créer composants React** pour afficher les chapitres
4. **Tester la communication** API complète

Référez-vous aux documents :
- `01_ROADMAP.md` pour les sprints suivants
- `02_USER_STORY_MAPPING.md` pour les fonctionnalités détaillées
- `04_ARCHITECTURE_TECHNIQUE.md` pour les patterns à suivre

---

## 🆘 TROUBLESHOOTING

### Erreur "Module not found: apps.accounts"
```bash
# Vérifier INSTALLED_APPS dans settings.py
# Vérifier que __init__.py existe dans apps/ et apps/accounts/
```

### Erreur "relation does not exist"
```bash
# Recréer migrations
python manage.py makemigrations
python manage.py migrate
```

### CORS error en frontend
```bash
# Vérifier CORS_ALLOWED_ORIGINS dans development.py
# Vérifier que corsheaders est dans INSTALLED_APPS et MIDDLEWARE
```

### WebSocket connection failed
```bash
# Pour l'instant normal, sera configuré au Sprint 2.1
# On utilise REST API uniquement pour MVP
```

---

## 📞 RESSOURCES

- **Django Docs :** https://docs.djangoproject.com/
- **DRF Docs :** https://www.django-rest-framework.org/
- **React Docs :** https://react.dev/
- **Redux Toolkit :** https://redux-toolkit.js.org/
- **Vite Docs :** https://vitejs.dev/

---

✅ **Setup terminé ! Vous êtes prêt à développer la plateforme.**
