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
    Sandbox Docker pour exécuter du code de manière sécurisée
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

    # Patterns dangereux à bloquer
    DANGEROUS_PATTERNS = [
        'eval',
        'exec',
        '__import__',
        'os.system',
        'subprocess',
        'open(',
        'file(',
        'require(',
        'process.',
        'child_process',
        '__dirname',
        '__filename',
    ]

    def __init__(self, language='html'):
        """
        Initialize Docker sandbox

        Args:
            language: Langage de programmation (html, python, javascript)
        """
        self.language = language.lower()
        self.client = docker.from_env()

    def _check_dangerous_code(self, code: str) -> None:
        """
        Vérifie si le code contient des patterns dangereux

        Args:
            code: Code à vérifier

        Raises:
            CodeValidationError: Si du code dangereux est détecté
        """
        code_lower = code.lower()
        for pattern in self.DANGEROUS_PATTERNS:
            if pattern in code_lower:
                raise CodeValidationError(
                    f"Code dangereux détecté: '{pattern}' n'est pas autorisé"
                )

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
            # Vérifier le code dangereux
            self._check_dangerous_code(user_code)

            # Créer le script de validation
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

    # Extraire la liste des tests depuis le champ JSONB
    # Le champ exercise.tests peut être {'tests': [...]} ou directement [...]
    tests = exercise.tests
    if isinstance(tests, dict) and 'tests' in tests:
        tests = tests['tests']

    # Exécuter la validation
    result = sandbox.run_code(user_code, tests)

    return result
