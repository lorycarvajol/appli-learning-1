"""
Limitation de débit sur la connexion.

### Pourquoi pas un simple throttle par IP

Le réglage évident — « N tentatives par heure et par adresse IP » — est le
mauvais réglage **ici**. Une classe entière se connecte depuis le NAT de son
établissement : trente élèves partagent une seule adresse. Un plafond par IP
mettrait la promo dehors à neuf heures du matin, tous les matins.

On compte donc par **compte visé**, pas par origine. Une attaque par
dictionnaire vise un compte précis et se fait arrêter, quelle que soit
l'adresse d'où elle vient — y compris répartie sur plusieurs machines, ce
qu'un compteur par IP ne voit pas.

### Pourquoi seuls les échecs sont comptés

Compter toutes les tentatives ouvrirait un déni de service trivial : brûler
le quota d'un camarade suffirait à l'empêcher de se connecter pendant une
heure. En ne comptant que les échecs, quiconque connaît son mot de passe entre
toujours — et l'attaquant, qui ne le connaît pas, épuise son quota.

Le compteur est en outre **remis à zéro à la connexion réussie** : trois
fautes de frappe suivies d'une réussite ne laissent aucune trace.

La limite globale `anon` (100/h par IP) reste par-dessus, comme garde-fou
contre l'abus massif depuis une même origine.
"""
from rest_framework.settings import api_settings
from rest_framework.throttling import SimpleRateThrottle


class FailedLoginThrottle(SimpleRateThrottle):
    """Compte les échecs de connexion par compte visé."""

    scope = 'login'

    def get_rate(self):
        """Lit le débit dans les réglages courants, et tolère son absence.

        Deux écarts avec `SimpleRateThrottle.get_rate`, chacun pour une raison
        précise :

        1. **Pas d'exception si le scope n'est pas réglé.** `development.py`
           vide `DEFAULT_THROTTLE_RATES` ; comme ce throttle est déclaré sur la
           vue (et non via `DEFAULT_THROTTLE_CLASSES`, vidé lui aussi), il est
           instancié malgré tout. La version d'origine lèverait
           `ImproperlyConfigured` et **casserait la connexion en
           développement**. Un débit nul désactive proprement la limitation.

        2. **Lecture à l'appel plutôt que via `THROTTLE_RATES`.** Cet attribut
           de classe est un instantané pris à l'import de DRF, que
           `override_settings` ne restaure pas : un réglage posé par un test
           fuyait sur les suivants. Relire `api_settings` rend le comportement
           déterministe — et c'est de toute façon la valeur qu'on veut.
        """
        return api_settings.DEFAULT_THROTTLE_RATES.get(self.scope)

    def get_cache_key(self, request, view):
        """Clé fondée sur l'email soumis, normalisé.

        La normalisation en minuscules est indispensable : `User.save()`
        normalise déjà les emails, donc `Eve@x.fr` et `eve@x.fr` désignent le
        même compte. Sans elle, il suffirait de varier la casse pour repartir
        avec un compteur neuf.

        Renvoyer `None` désactive le throttle — cas d'une requête sans email,
        que le serializer rejettera de toute façon en 400.
        """
        email = request.data.get('email') if hasattr(request, 'data') else None
        if not email or not isinstance(email, str):
            return None

        return self.cache_format % {
            'scope': self.scope,
            'ident': email.strip().lower(),
        }

    def allow_request(self, request, view):
        """Vérifie le quota **sans le consommer**.

        `SimpleRateThrottle` enregistre normalement chaque passage ici. On
        sépare les deux : la consommation est décidée après coup par la vue,
        selon que l'authentification a réussi ou non.
        """
        if self.rate is None:  # limitation désactivée (développement)
            self.key = None
            return True

        self.key = self.get_cache_key(request, view)
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])
        self.now = self.timer()

        # Purge des tentatives sorties de la fenêtre glissante.
        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()

        return len(self.history) < self.num_requests

    def record_failure(self):
        """Décompte une tentative — appelé uniquement après un échec."""
        if getattr(self, 'key', None) is None:
            return
        self.history.insert(0, self.now)
        self.cache.set(self.key, self.history, self.duration)

    def reset(self):
        """Efface l'historique après une connexion réussie."""
        if getattr(self, 'key', None) is None:
            return
        self.cache.delete(self.key)
