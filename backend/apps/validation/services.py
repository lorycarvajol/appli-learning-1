"""
Service de validation de code avec sandbox Docker
Exécute le code utilisateur dans un environnement isolé et sécurisé
"""

import docker
import json
import time
from typing import Dict, List, Any
from django.conf import settings


class CodeValidationError(Exception):
    """Exception levée lors d'erreurs de validation"""
    pass


class DockerSandbox:
    """
    Exécute du code d'apprenant dans un conteneur jetable.

    ### Le conteneur est la seule frontière de sécurité

    Ce qui protège l'hôte, et rien d'autre :

    - `network_disabled=True` — aucune sortie réseau, donc pas d'exfiltration,
      pas de minage, et **aucun moyen d'atteindre le démon Docker** dont le
      worker Celery détient pourtant le socket.
    - **Aucun montage** : le conteneur ne voit jamais le système de fichiers de
      l'hôte. Ne jamais ajouter de `volumes=` ici.
    - `mem_limit` / `cpu_quota` — une boucle qui alloue ne peut pas emporter
      la machine.
    - `TIMEOUT`, puis `kill()` et `remove()` dans tous les cas.
    - Instance recréée à chaque soumission : rien ne persiste d'une exécution
      à l'autre.

    ### Pourquoi il n'y a plus de liste de motifs interdits

    Une liste noire (`eval`, `exec`, `open(`…) a existé ici. Elle a été retirée
    après mesure : elle **rejetait du code d'apprenant parfaitement légitime**
    — `executeTask` déclenchait sur `exec`, `evaluation` sur `eval`, et même le
    mot français « evaluer » dans un commentaire — tout en laissant passer les
    contournements évidents (`new Function("…")()`, `this["ev"+"al"]`).

    Une recherche de sous-chaîne ne peut pas arrêter quelqu'un qui cherche à la
    contourner ; elle ne gênait donc que les élèves de bonne foi, en leur
    reprochant une faute qu'ils n'avaient pas commise.

    Ce que du code arbitraire peut faire aujourd'hui : lire et écrire dans le
    système de fichiers **du conteneur** (une image de base publique, jetée
    aussitôt), et consommer ses propres ressources plafonnées. Rien de cela
    n'atteint l'hôte ni les autres apprenants.

    ⚠️ Corollaire : **toute atténuation de l'isolement du conteneur est
    désormais une régression de sécurité directe**, sans filet en amont.
    """

    # Limites de ressources
    MEMORY_LIMIT = '128m'  # 128 MB de RAM
    CPU_QUOTA = 50000  # 50% d'un CPU
    TIMEOUT = 5  # 5 secondes max

    # Images Docker par langage
    DOCKER_IMAGES = {
        'html': 'python:3.11-slim',  # On utilise Python pour valider le HTML
        'css': 'python:3.11-slim',   # Même principe : tests par regex sur le texte brut
        'python': 'python:3.11-slim',
        'javascript': 'node:18-alpine',
    }

    def __init__(self, language='html'):
        """
        Initialize Docker sandbox

        Args:
            language: Langage de programmation (html, python, javascript)
        """
        self.language = language.lower()
        self.client = docker.from_env()

    def _create_validation_script(self, user_code: str, tests: List[Dict]) -> str:
        """
        Crée le script de validation Python

        Args:
            user_code: Code HTML de l'utilisateur
            tests: Liste des tests à exécuter

        Returns:
            Script Python qui valide le code
        """
        if self.language in ('html', 'css'):
            # Pour HTML et CSS, on crée un script Python qui expose le texte
            # brut (solution) pour des tests par regex/chaîne. Pour HTML,
            # tags/attrs donnent en plus un accès structuré via HTMLParser
            # (sans effet pour du CSS, qui n'a simplement pas de balises).
            script = '''
import json
import sys
from html.parser import HTMLParser

# Code utilisateur
user_code = """''' + user_code.replace('"""', '\\"\\"\\"') + '''"""

# Tests
tests = ''' + json.dumps(tests) + '''

class HTMLValidator(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.attrs = {}

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs[tag] = dict(attrs)

results = []

for test in tests:
    try:
        test_code = test.get('code', '')
        test_name = test.get('name', 'Test')
        points = test.get('points', 1)
        error_message = test.get('error_message', '')

        # Créer le validateur HTML
        validator = HTMLValidator()
        validator.feed(user_code)

        # Exécuter le test
        local_vars = {
            'user_code': user_code,
            'solution': user_code,  # Alias pour compatibilité avec les tests
            'tags': validator.tags,
            'attrs': validator.attrs,
        }

        # Évaluer le test
        exec(test_code, {}, local_vars)

        results.append({
            'name': test_name,
            'passed': True,
            'points': points,
            'message': '✓ Parfait !'
        })

    except AssertionError as e:
        # Utiliser le message d'erreur pédagogique défini dans le test
        message = error_message if error_message else (str(e) if str(e) else 'Le test a échoué')
        results.append({
            'name': test_name,
            'passed': False,
            'points': 0,
            'message': message
        })
    except Exception as e:
        results.append({
            'name': test_name,
            'passed': False,
            'points': 0,
            'message': f'⚠️ Erreur inattendue: {str(e)}'
        })

# Résultat final
output = {
    'results': results,
    'total_points': sum(r['points'] for r in results),
    'max_points': sum(t.get('points', 1) for t in tests),
}

print(json.dumps(output))
'''
        elif self.language == 'javascript':
            # Pour JavaScript : le code utilisateur est exécuté tel quel (ses
            # variables/fonctions restent donc accessibles aux tests), et le
            # texte source brut est aussi exposé (variable __source) pour les
            # tests qui ont besoin de vérifier la présence de code plutôt que
            # son comportement (ex: manipulation du DOM, non exécutable ici
            # faute de vrai navigateur dans le sandbox).
            script = '''
const assert = require('assert');
const __source = ''' + json.dumps(user_code) + ''';
const __tests = ''' + json.dumps(tests) + ''';
const __results = [];

// Le sandbox n'a pas de vrai navigateur : on fournit des mocks minimalistes
// pour que du code de manipulation du DOM s'exécute sans planter (les tests
// portant sur ce type de code vérifient __source plutôt que le comportement).
function __mockElement() {
    const el = {
        textContent: '', innerHTML: '', value: '', style: {},
        classList: {
            _classes: new Set(),
            add(...names) { names.forEach(n => this._classes.add(n)); },
            remove(...names) { names.forEach(n => this._classes.delete(n)); },
            toggle(name) { this._classes.has(name) ? this._classes.delete(name) : this._classes.add(name); },
            contains(name) { return this._classes.has(name); },
        },
        addEventListener() {}, removeEventListener() {},
        setAttribute(name, value) { el[name] = value; },
        getAttribute(name) { return el[name]; },
        appendChild() {}, remove() {},
    };
    return el;
}
const document = {
    querySelector: () => __mockElement(),
    querySelectorAll: () => [__mockElement()],
    getElementById: () => __mockElement(),
    createElement: () => __mockElement(),
    addEventListener: () => {},
    body: __mockElement(),
};
const window = { document, addEventListener: () => {}, alert: () => {} };
const alert = () => {};

''' + user_code + '''

for (const __test of __tests) {
    const __name = __test.name || 'Test';
    const __points = __test.points || 1;
    const __errorMessage = __test.error_message || '';
    try {
        eval(__test.code);
        __results.push({ name: __name, passed: true, points: __points, message: '✓ Parfait !' });
    } catch (__e) {
        const __message = __errorMessage || __e.message || 'Le test a échoué';
        __results.push({ name: __name, passed: false, points: 0, message: __message });
    }
}

console.log(JSON.stringify({
    results: __results,
    total_points: __results.reduce((s, r) => s + r.points, 0),
    max_points: __tests.reduce((s, t) => s + (t.points || 1), 0),
}));
'''
        else:
            # Pour Python pur
            script = user_code + '\n\n' + '\n'.join(test['code'] for test in tests)

        return script

    def run_code(self, user_code: str, tests: List[Dict]) -> Dict[str, Any]:
        """
        Exécute le code dans un conteneur Docker isolé

        Args:
            user_code: Code de l'utilisateur
            tests: Liste des tests à exécuter

        Returns:
            Résultats de l'exécution avec tests passés/échoués
        """
        try:
            # Aucun filtrage du code en amont : c'est l'isolement du conteneur
            # qui protège (cf. la docstring de la classe).
            validation_script = self._create_validation_script(user_code, tests)

            # Image Docker et interpréteur à utiliser selon le langage
            image = self.DOCKER_IMAGES.get(self.language, self.DOCKER_IMAGES['python'])
            if self.language == 'javascript':
                command = ['node', '-e', validation_script]
            else:
                command = ['python', '-c', validation_script]

            # Créer et exécuter le conteneur
            container = self.client.containers.run(
                image,
                command=command,
                detach=True,
                mem_limit=self.MEMORY_LIMIT,
                cpu_quota=self.CPU_QUOTA,
                network_disabled=True,  # Pas d'accès réseau
                remove=False,  # On supprimera manuellement après avoir récupéré les logs
            )

            try:
                # Attendre la fin avec timeout
                result = container.wait(timeout=self.TIMEOUT)

                # Récupérer les logs avant de supprimer le conteneur
                logs = container.logs().decode('utf-8')

            except Exception as e:
                # En cas d'erreur ou timeout, tuer et supprimer le conteneur
                try:
                    container.kill()
                    container.remove()
                except:
                    pass
                raise CodeValidationError(f"Erreur lors de l'exécution: {str(e)}")
            finally:
                # Supprimer le conteneur dans tous les cas
                try:
                    container.remove()
                except:
                    pass

            # Parser le résultat JSON
            try:
                result = json.loads(logs.strip().split('\n')[-1])
                result['success'] = result['total_points'] == result['max_points']
                return result
            except (json.JSONDecodeError, IndexError):
                return {
                    'success': False,
                    'error': 'Erreur lors du parsing des résultats',
                    'logs': logs,
                    'results': [],
                    'total_points': 0,
                    'max_points': sum(t.get('points', 1) for t in tests),
                }

        except docker.errors.ContainerError as e:
            return {
                'success': False,
                'error': f'Erreur d\'exécution: {str(e)}',
                'results': [],
                'total_points': 0,
                'max_points': sum(t.get('points', 1) for t in tests),
            }
        except CodeValidationError as e:
            return {
                'success': False,
                'error': str(e),
                'results': [],
                'total_points': 0,
                'max_points': sum(t.get('points', 1) for t in tests),
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Erreur inattendue: {str(e)}',
                'results': [],
                'total_points': 0,
                'max_points': sum(t.get('points', 1) for t in tests),
            }


def validate_exercise_code(exercise, user_code: str) -> Dict[str, Any]:
    """
    Valide le code d'un exercice

    Args:
        exercise: Instance du modèle Exercise
        user_code: Code soumis par l'utilisateur

    Returns:
        Résultats de la validation
    """
    # Déterminer le langage à partir de l'exercice (html par défaut, pour
    # rester compatible avec les exercices existants créés avant ce champ)
    language = getattr(exercise, 'language', None) or 'html'

    # Créer le sandbox
    sandbox = DockerSandbox(language=language)

    # La normalisation des deux formes du champ JSONB vit sur le modèle
    # (`Exercise.test_cases`), pour que tous les lecteurs voient la même chose.
    result = sandbox.run_code(user_code, exercise.test_cases)

    return result
