#!/bin/bash

# Script de démarrage pour Learning Platform
echo "🚀 Démarrage de la Learning Platform..."

# Vérifier que Docker est lancé
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker n'est pas lancé. Veuillez démarrer Docker Desktop."
    exit 1
fi

echo "✅ Docker est lancé"

# Démarrer les services
echo "📦 Démarrage des conteneurs..."
docker-compose up -d

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services (30 secondes)..."
sleep 30

# Vérifier l'état des services
echo "🔍 Vérification de l'état des services..."
docker-compose ps

# Appliquer les migrations si nécessaire
echo "📊 Application des migrations..."
docker-compose exec -T backend python manage.py migrate --noinput

echo ""
echo "✅ =============================================="
echo "✅  Learning Platform démarrée avec succès !"
echo "✅ =============================================="
echo ""
echo "🌐 Accédez à l'application :"
echo "   Frontend:  http://localhost:5173"
echo "   Backend:   http://localhost:8000/api"
echo "   Admin:     http://localhost:8000/admin"
echo ""
echo "📝 Prochaines étapes :"
echo "   1. Créer un superuser: docker-compose exec backend python manage.py createsuperuser"
echo "   2. Ouvrir http://localhost:5173 et s'inscrire"
echo ""
echo "📋 Commandes utiles :"
echo "   Voir les logs:    docker-compose logs -f"
echo "   Arrêter:          docker-compose down"
echo "   Redémarrer:       docker-compose restart"
echo ""
