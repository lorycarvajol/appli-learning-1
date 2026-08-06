# Multi-stage build for the Django backend

# ---- Base: shared system deps, no requirements installed yet ----
FROM python:3.11-slim AS base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/base.txt requirements/base.txt

# ---- Development: dev tools, tests, debug toolbar ----
FROM base AS development

# Polices utilisées par `manage.py generate_course_images` pour dessiner les
# illustrations des cours. Volontairement absentes de l'étage production : les
# PNG y sont servis depuis le dépôt, jamais régénérés.
RUN apt-get update && apt-get install -y --no-install-recommends \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

COPY requirements/development.txt requirements/development.txt
RUN pip install -r requirements/development.txt

COPY . .
RUN mkdir -p staticfiles media logs

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--reload"]

# ---- Production: lean image, no dev/test dependencies ----
FROM base AS production

COPY requirements/production.txt requirements/production.txt
RUN pip install -r requirements/production.txt

COPY . .
RUN mkdir -p staticfiles media logs

EXPOSE 8000

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
