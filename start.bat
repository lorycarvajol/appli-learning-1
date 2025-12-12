@echo off
REM Script de démarrage pour Learning Platform (Windows)

echo.
echo ========================================
echo   Learning Platform - Demarrage
echo ========================================
echo.

REM Vérifier que Docker est lancé
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo X Docker n'est pas lance. Veuillez demarrer Docker Desktop.
    pause
    exit /b 1
)

echo [OK] Docker est lance
echo.

REM Démarrer les services
echo [*] Demarrage des conteneurs...
docker-compose up -d

REM Attendre que les services soient prêts
echo [*] Attente du demarrage des services (30 secondes)...
timeout /t 30 /nobreak >nul

REM Vérifier l'état des services
echo.
echo [*] Verification de l'etat des services...
docker-compose ps

REM Appliquer les migrations
echo.
echo [*] Application des migrations...
docker-compose exec -T backend python manage.py migrate --noinput

echo.
echo ========================================
echo   Learning Platform demarree !
echo ========================================
echo.
echo Acces a l'application :
echo   Frontend:  http://localhost:5173
echo   Backend:   http://localhost:8000/api
echo   Admin:     http://localhost:8000/admin
echo.
echo Prochaines etapes :
echo   1. Creer un superuser: docker-compose exec backend python manage.py createsuperuser
echo   2. Ouvrir http://localhost:5173 et s'inscrire
echo.
echo Commandes utiles :
echo   Voir les logs:    docker-compose logs -f
echo   Arreter:          docker-compose down
echo   Redemarrer:       docker-compose restart
echo.
pause
