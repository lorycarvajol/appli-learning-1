"""
Tests de bout en bout du bac à sable : du vrai code, dans un vrai conteneur.

Complémentaires de `test_sandbox.py`, qui simule Docker pour vérifier *comment*
le conteneur est lancé. Ici on vérifie que l'ensemble produit le bon verdict —
ce qu'aucune simulation ne peut démontrer.

⚠️ **Ces tests ne tournent que là où le démon Docker est joignable.**
`/var/run/docker.sock` n'est monté que sur le service `celery`, pas sur
`backend` où pytest s'exécute d'habitude :

    docker-compose exec celery pytest apps/validation -m docker

Ailleurs — y compris dans le conteneur `backend` — ils sont ignorés, pas en
échec. Un test qui échoue faute d'environnement finit par être désactivé, et
emporte avec lui ceux qui avaient quelque chose à dire.
"""
import pytest

from apps.validation.services import DockerSandbox

pytestmark = pytest.mark.docker


def _sandbox_ou_skip(language):
    """Construit le bac à sable, ou passe le test si Docker est absent."""
    try:
        return DockerSandbox(language=language)
    except Exception as exc:  # docker.errors.DockerException et dérivés
        pytest.skip(f'Démon Docker injoignable : {exc}')


JS_TESTS = [
    {'name': 'somme(2,3)', 'code': 'assert.strictEqual(somme(2, 3), 5);', 'points': 10},
]


def test_un_code_correct_obtient_tous_les_points():
    sandbox = _sandbox_ou_skip('javascript')

    result = sandbox.run_code('function somme(a, b) { return a + b; }', JS_TESTS)

    assert result['success'] is True
    assert result['total_points'] == result['max_points'] == 10
    assert result['results'][0]['passed'] is True


def test_un_code_faux_est_recale_avec_un_message_utile():
    """Le message d'échec est ce que l'apprenant lit : il doit désigner l'écart,
    pas se contenter d'annoncer « raté »."""
    sandbox = _sandbox_ou_skip('javascript')

    result = sandbox.run_code('function somme(a, b) { return a * b; }', JS_TESTS)

    assert result['success'] is False
    assert result['total_points'] == 0
    assert '5' in result['results'][0]['message']


def test_un_code_qui_ne_compile_pas_ne_fait_pas_planter_le_worker():
    sandbox = _sandbox_ou_skip('javascript')

    result = sandbox.run_code('function somme(a, b { return', JS_TESTS)

    assert result['success'] is False


def test_une_boucle_infinie_est_interrompue():
    """Le garde-fou qui compte vraiment : sans lui, une soumission d'apprenant
    immobilise un worker Celery pour toujours."""
    sandbox = _sandbox_ou_skip('javascript')

    result = sandbox.run_code('while (true) {}', JS_TESTS)

    assert result['success'] is False


def test_du_code_autrefois_rejete_a_tort_est_maintenant_accepte():
    """La raison d'être du retrait de la liste noire.

    Ces trois lignes — un nom de fonction, un nom de variable, un commentaire
    en français — étaient rejetées avec un message accusant l'apprenant, parce
    qu'elles contiennent les sous-chaînes « exec » et « eval ».
    """
    sandbox = _sandbox_ou_skip('javascript')

    result = sandbox.run_code(
        'function executeTask() {}\n'
        'const evaluation = 0;\n'
        '// on va evaluer le resultat\n'
        'function somme(a, b) { return a + b; }',
        JS_TESTS,
    )

    assert result['success'] is True


def test_une_tentative_de_sortie_reseau_est_contenue():
    """Ce que la liste noire prétendait empêcher, et que le conteneur fait
    réellement : la requête n'aboutit pas, et l'exécution est coupée au délai."""
    sandbox = _sandbox_ou_skip('javascript')

    result = sandbox.run_code(
        'require("http").get("http://example.com");\n'
        'function somme(a, b) { return a + b; }',
        JS_TESTS,
    )

    assert result['success'] is False


def test_le_code_html_est_valide_par_analyse_de_balises():
    sandbox = _sandbox_ou_skip('html')

    result = sandbox.run_code(
        '<h1>Bonjour</h1><p>Texte</p>',
        [{'name': 'a un titre', 'code': "assert 'h1' in tags", 'points': 5}],
    )

    assert result['success'] is True
