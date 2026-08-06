"""
Tests du bac à sable d'exécution de code.

C'est le composant le plus dangereux de la plateforme : il exécute du code
écrit par des apprenants. Il vivait jusqu'ici sans un seul test.

### Ce que ces tests protègent réellement

**L'isolement du conteneur est la seule frontière de sécurité** — au sens
littéral depuis le retrait de la liste noire de motifs : réseau coupé, aucun
montage, mémoire plafonnée, CPU bridé, délai maximal, conteneur jetable.

La majorité des tests ci-dessous vérifient que ces garde-fous sont bien
transmis à Docker. C'est le genre de réglage qu'on supprime par mégarde en
déboguant, sans que rien ne le signale — et il n'y a plus aucun filtre en
amont pour rattraper l'erreur.

Le client Docker est **simulé** : on veut vérifier *avec quels arguments* le
conteneur est lancé, pas regarder un conteneur tourner. C'est plus rapide, ça
tourne en intégration continue, et surtout c'est un contrôle plus strict —
lancer un vrai conteneur ne dirait pas si `network_disabled` a disparu.

Les tests de bout en bout, eux, sont marqués `docker` et ne tournent que là où
le démon est accessible (voir `test_sandbox_reel.py`).
"""
import json
from unittest.mock import MagicMock, patch

import pytest

from apps.validation.services import CodeValidationError, DockerSandbox


@pytest.fixture
def docker_mock():
    """Remplace le client Docker et rend le conteneur qu'il fabrique."""
    with patch('apps.validation.services.docker') as docker_module:
        container = MagicMock()
        container.wait.return_value = {'StatusCode': 0}
        container.logs.return_value = json.dumps({
            'results': [{'name': 'T1', 'passed': True, 'points': 10, 'message': 'ok'}],
            'total_points': 10,
            'max_points': 10,
        }).encode('utf-8')

        client = MagicMock()
        client.containers.run.return_value = container
        docker_module.from_env.return_value = client
        # Les `except docker.errors.*` du code testé ont besoin de vraies
        # classes d'exception, qu'un MagicMock ne fournit pas.
        docker_module.errors.ContainerError = type('ContainerError', (Exception,), {})

        yield client, container


TESTS = [{'name': 'T1', 'code': 'assert True', 'points': 10}]


# ---------------------------------------------------------------------------
# La vraie frontière : l'isolement du conteneur
# ---------------------------------------------------------------------------

def test_le_code_utilisateur_na_jamais_acces_au_reseau(docker_mock):
    """Sans cette coupure, du code d'apprenant peut appeler l'extérieur —
    exfiltrer, miner, ou servir de rebond depuis notre infrastructure."""
    client, _ = docker_mock
    DockerSandbox(language='python').run_code('x = 1', TESTS)

    assert client.containers.run.call_args.kwargs['network_disabled'] is True


def test_les_ressources_sont_plafonnees(docker_mock):
    """Une boucle infinie qui alloue est le premier accident d'un débutant.
    Sans plafond, elle emporte l'hôte avec elle."""
    client, _ = docker_mock
    DockerSandbox(language='python').run_code('x = 1', TESTS)

    kwargs = client.containers.run.call_args.kwargs
    assert kwargs['mem_limit'] == '128m'
    assert kwargs['cpu_quota'] == 50000


def test_lexecution_est_bornee_dans_le_temps(docker_mock):
    """`while(true)` ne doit pas immobiliser un worker Celery indéfiniment."""
    _, container = docker_mock
    DockerSandbox(language='python').run_code('x = 1', TESTS)

    assert container.wait.call_args.kwargs['timeout'] == 5


def test_le_conteneur_est_supprime_apres_execution(docker_mock):
    """Un conteneur oublié par soumission remplit le disque en quelques jours."""
    _, container = docker_mock
    DockerSandbox(language='python').run_code('x = 1', TESTS)

    assert container.remove.called


def test_le_conteneur_est_tue_et_supprime_meme_en_cas_de_depassement(docker_mock):
    """C'est le cas qui compte : un conteneur qui ne rend pas la main est
    précisément celui qu'on risque de laisser derrière soi."""
    _, container = docker_mock
    container.wait.side_effect = TimeoutError('délai dépassé')

    result = DockerSandbox(language='python').run_code('while True: pass', TESTS)

    assert container.kill.called
    assert container.remove.called
    assert result['success'] is False


# ---------------------------------------------------------------------------
# Choix de l'image et de l'interpréteur
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('langage,image,binaire', [
    ('javascript', 'node:18-alpine', 'node'),
    ('python', 'python:3.11-slim', 'python'),
    ('html', 'python:3.11-slim', 'python'),
    ('css', 'python:3.11-slim', 'python'),
])
def test_chaque_langage_utilise_son_image(docker_mock, langage, image, binaire):
    client, _ = docker_mock
    DockerSandbox(language=langage).run_code('x = 1', TESTS)

    args, kwargs = client.containers.run.call_args
    assert args[0] == image
    assert kwargs['command'][0] == binaire


def test_un_langage_inconnu_retombe_sur_python(docker_mock):
    """Plutôt que de planter : un exercice mal étiqueté doit donner un verdict
    d'échec lisible, pas une erreur 500."""
    client, _ = docker_mock
    DockerSandbox(language='cobol').run_code('x = 1', TESTS)

    assert client.containers.run.call_args[0][0] == 'python:3.11-slim'


# ---------------------------------------------------------------------------
# Résultats et robustesse de l'analyse
# ---------------------------------------------------------------------------

def test_le_score_est_agrege_depuis_les_tests(docker_mock):
    _, container = docker_mock
    container.logs.return_value = json.dumps({
        'results': [
            {'name': 'T1', 'passed': True, 'points': 10, 'message': ''},
            {'name': 'T2', 'passed': False, 'points': 0, 'message': 'raté'},
        ],
        'total_points': 10,
        'max_points': 20,
    }).encode('utf-8')

    result = DockerSandbox(language='python').run_code('x = 1', TESTS)

    assert result['total_points'] == 10
    assert result['max_points'] == 20
    # La réussite exige le score **maximum**, pas un seuil.
    assert result['success'] is False


def test_une_sortie_illisible_ne_fait_pas_planter(docker_mock):
    """Le conteneur peut écrire n'importe quoi (trace d'erreur, sortie vide).
    L'apprenant doit voir un échec, jamais une erreur serveur."""
    _, container = docker_mock
    container.logs.return_value = b'Traceback (most recent call last):\n  ...'

    result = DockerSandbox(language='python').run_code('x = 1', TESTS)

    assert result['success'] is False
    assert result['max_points'] == 10
    assert 'logs' in result


def test_une_panne_du_demon_docker_est_rattrapee(docker_mock):
    """Si Docker est arrêté, la soumission échoue proprement."""
    client, _ = docker_mock
    client.containers.run.side_effect = RuntimeError('démon injoignable')

    result = DockerSandbox(language='python').run_code('x = 1', TESTS)

    assert result['success'] is False
    assert 'error' in result


# ---------------------------------------------------------------------------
# Il n'y a plus de filtrage du code en amont
# ---------------------------------------------------------------------------

@pytest.mark.parametrize('code,pourquoi_cetait_bloque', [
    ('function executeTask() {}', 'contient « exec »'),
    ('const evaluation = 12;', 'contient « eval »'),
    ('document.open();', 'contient « open( »'),
    ('// on va evaluer le resultat', 'commentaire français contenant « eval »'),
    ('const data = require("./mod");', 'contient « require( »'),
    ('import subprocess', 'contient « subprocess »'),
])
def test_le_code_est_execute_sans_filtrage_prealable(
    docker_mock, code, pourquoi_cetait_bloque
):
    """Une liste noire de sous-chaînes rejetait ces codes avant tout lancement.

    Les quatre premiers cas sont du **code d'apprenant légitime** : elle leur
    reprochait une faute qu'ils n'avaient pas commise. Les deux derniers sont
    de vraies tentatives, mais elles restent enfermées dans le conteneur —
    et la liste ne savait de toute façon pas arrêter `new Function("…")()`.

    Ce qui compte désormais : le conteneur **est lancé**, avec ses garde-fous.
    """
    client, _ = docker_mock
    result = DockerSandbox(language='javascript').run_code(code, TESTS)

    assert client.containers.run.called, pourquoi_cetait_bloque
    assert client.containers.run.call_args.kwargs['network_disabled'] is True
    assert 'error' not in result


def test_aucun_systeme_de_fichiers_hote_nest_monte(docker_mock):
    """Le garde-fou devenu le plus important.

    Le worker Celery a `/var/run/docker.sock` monté — c'est ainsi qu'il pilote
    le bac à sable. Monter quoi que ce soit de l'hôte dans le conteneur
    d'exécution donnerait au code d'apprenant un chemin vers cette socket,
    donc le contrôle du démon Docker, donc l'hôte entier.

    Combiné à `network_disabled`, l'absence de montage rend ce chemin
    inatteignable. Il n'y a plus de filtrage en amont pour rattraper l'erreur.
    """
    client, _ = docker_mock
    DockerSandbox(language='python').run_code('x = 1', TESTS)

    kwargs = client.containers.run.call_args.kwargs
    assert 'volumes' not in kwargs
    assert 'mounts' not in kwargs


# ---------------------------------------------------------------------------
# Durcissement du conteneur d'exécution
# ---------------------------------------------------------------------------
#
# Ces réglages ont été ajoutés pour pouvoir réactiver l'exécution de code sur
# un **hôte mutualisé**. Chacun retire un moyen d'évasion précis ; les vérifier
# sur les arguments passés à Docker est délibéré — lancer un vrai conteneur ne
# dirait pas si l'un d'eux a disparu d'un appel.

def test_le_code_ne_sexecute_plus_en_root(docker_mock):
    """Sans cela, une faille du runtime donnait `root` sur l'hôte d'un coup.

    Les identifiants sont numériques (65534:65534) et non `nobody` : le nom
    n'est pas garanti d'une image à l'autre — Debian pour `python:slim`,
    Alpine pour `node:alpine`.
    """
    client, _ = docker_mock
    DockerSandbox(language='python').run_code('x = 1', TESTS)

    assert client.containers.run.call_args.kwargs['user'] == '65534:65534'


def test_aucune_capacite_linux_nest_conservee(docker_mock):
    """`cap_drop=ALL` retire jusqu'à `CAP_CHOWN` et `CAP_SETUID`.

    Un exercice n'a besoin d'aucune capacité privilégiée : les garder ne
    servait qu'à un éventuel attaquant.
    """
    client, _ = docker_mock
    DockerSandbox(language='python').run_code('x = 1', TESTS)

    assert client.containers.run.call_args.kwargs['cap_drop'] == ['ALL']


def test_lelevation_de_privileges_est_neutralisee(docker_mock):
    """`no-new-privileges` rend inopérant tout binaire setuid de l'image."""
    client, _ = docker_mock
    DockerSandbox(language='python').run_code('x = 1', TESTS)

    assert 'no-new-privileges:true' in client.containers.run.call_args.kwargs['security_opt']


def test_le_systeme_de_fichiers_est_en_lecture_seule(docker_mock):
    """Un code qui ne peut rien écrire ne peut pas déposer de binaire à exécuter.

    `/tmp` reste inscriptible — certains interpréteurs en ont besoin — mais en
    mémoire, plafonné, et surtout `noexec`.
    """
    client, _ = docker_mock
    DockerSandbox(language='python').run_code('x = 1', TESTS)

    kwargs = client.containers.run.call_args.kwargs
    assert kwargs['read_only'] is True
    assert 'noexec' in kwargs['tmpfs']['/tmp']
    assert 'size=' in kwargs['tmpfs']['/tmp']


def test_le_nombre_de_processus_est_borne(docker_mock):
    """Une bombe à fork épuise le conteneur, jamais la table de l'hôte."""
    client, _ = docker_mock
    DockerSandbox(language='python').run_code('x = 1', TESTS)

    assert client.containers.run.call_args.kwargs['pids_limit'] == 64


def test_la_branche_python_produit_un_resultat_lisible(docker_mock):
    """Elle ne produisait **aucune** sortie JSON, donc échouait toujours.

    Le défaut est resté invisible parce qu'aucun exercice n'utilise ce
    langage — il aurait accueilli le premier.
    """
    client, _ = docker_mock
    script = DockerSandbox(language='python')._create_validation_script(
        'def somme(a, b):\n    return a + b',
        [{'name': 'somme', 'code': 'assert somme(2, 3) == 5', 'points': 5}],
    )

    assert 'json.dumps' in script, "sans sortie JSON, le résultat est impossible à lire"
    assert 'total_points' in script
    assert 'max_points' in script
