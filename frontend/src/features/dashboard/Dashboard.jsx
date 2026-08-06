import { useEffect, useMemo } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import {
  fetchMyProgress,
  fetchNextLesson,
  fetchProgressOverview,
  selectNextLesson,
  selectProgressOverview,
} from '../progression/progressionSlice';
import NextObjectives from '../gamification/NextObjectives';
import {
  selectLevel,
  selectSummary,
  syncGamification,
} from '../gamification/gamificationSlice';
import { buildTipContext, pickTip } from './dailyTips';
import './Dashboard.css';

const LESSON_TYPE_LABELS = {
  THEORY: '📖 Théorie',
  EXERCISE: '💻 Exercice',
  QUIZ: '❓ Quiz',
};

export default function Dashboard() {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const summary = useSelector(selectSummary);
  const level = useSelector(selectLevel);
  const nextLesson = useSelector(selectNextLesson);
  const overview = useSelector(selectProgressOverview);

  useEffect(() => {
    dispatch(fetchMyProgress());
    dispatch(fetchNextLesson());
    dispatch(fetchProgressOverview());
    // `sync` est idempotent côté serveur : il rattrape un éventuel badge
    // manqué (session interrompue, onglet fermé) sans rien redistribuer.
    dispatch(syncGamification());
  }, [dispatch]);

  /*
    Les compteurs viennent du serveur, plus d'un calcul local.

    ⚠️ Ils étaient dérivés des seules leçons déjà touchées, ce qui donnait deux
    chiffres faux : une « progression globale » à 100 % dès la première leçon
    terminée (le programme entier n'était pas au dénominateur), et un score
    moyen qui comptait les leçons de théorie — non notées, donc `score: null` —
    comme des zéros. Le client ne peut pas les corriger : il ignore combien de
    leçons existent.
  */
  const lessons = overview?.lessons;
  const completedLessons = lessons?.completed ?? 0;
  const inProgressLessons = lessons?.in_progress ?? 0;
  const totalLessons = lessons?.total ?? 0;
  const globalPercent = lessons?.percent ?? 0;
  const totalTimeSpent = overview?.time_spent_seconds ?? 0;

  const tip = useMemo(
    () => pickTip(buildTipContext({ summary, overview, nextLesson })),
    [summary, overview, nextLesson]
  );

  const formatTime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `${hours}h ${minutes}min`;
    return `${minutes}min`;
  };

  return (
    <div className="dashboard">
      {/* Hero Section */}
      <section className="dashboard__hero">
        <div className="dashboard__hero-content">
          <h1 className="dashboard__hero-title">
            Bonjour {user?.first_name || 'Apprenant'} ! 👋
          </h1>
          <p className="dashboard__hero-subtitle">
            Prêt à continuer votre apprentissage aujourd’hui ?
          </p>
        </div>
        <div className="dashboard__hero-illustration" aria-hidden="true">
          <div className="dashboard__hero-circle dashboard__hero-circle--1"></div>
          <div className="dashboard__hero-circle dashboard__hero-circle--2"></div>
          <div className="dashboard__hero-circle dashboard__hero-circle--3"></div>
        </div>
      </section>

      <div className="dashboard__container">
        {/* Stats Cards */}
        <section className="dashboard__stats">
          <div className="stat-card stat-card--purple">
            <div className="stat-card__icon" aria-hidden="true">🎯</div>
            <div className="stat-card__content">
              <div className="stat-card__value">
                {summary?.points ?? user?.profile?.total_points ?? 0}
              </div>
              <div className="stat-card__label">Points totaux</div>
              {level && (
                <div className="stat-card__sublabel">
                  Encore {level.points_for_next} pts avant le niveau {level.level + 1}
                </div>
              )}
            </div>
            <div className="stat-card__badge">
              Niveau {level?.level ?? user?.profile?.level ?? 1}
            </div>
          </div>

          <div className="stat-card stat-card--green">
            <div className="stat-card__icon" aria-hidden="true">✅</div>
            <div className="stat-card__content">
              <div className="stat-card__value">
                {completedLessons}
                {totalLessons > 0 && (
                  <span className="stat-card__value-total">/{totalLessons}</span>
                )}
              </div>
              <div className="stat-card__label">Leçons complétées</div>
            </div>
            <div className="stat-card__progress">{inProgressLessons} en cours</div>
          </div>

          <div className="stat-card stat-card--blue">
            <div className="stat-card__icon" aria-hidden="true">⏱️</div>
            <div className="stat-card__content">
              <div className="stat-card__value">{formatTime(totalTimeSpent)}</div>
              <div className="stat-card__label">Temps d’apprentissage</div>
            </div>
          </div>

          <div className="stat-card stat-card--orange">
            <div className="stat-card__icon" aria-hidden="true">📊</div>
            <div className="stat-card__content">
              {/*
                Un tiret, pas « 0 % » : rien de noté ne veut pas dire zéro, et
                un débutant lit un zéro comme un échec.
              */}
              <div className="stat-card__value">
                {overview?.average_score === null || overview?.average_score === undefined
                  ? '—'
                  : `${overview.average_score}%`}
              </div>
              <div className="stat-card__label">Score moyen</div>
              <div className="stat-card__sublabel">
                {overview?.graded_count
                  ? `sur ${overview.graded_count} évaluation(s)`
                  : 'quiz et exercices notés'}
              </div>
            </div>
          </div>

          <div className="stat-card stat-card--trophy">
            <div className="stat-card__icon" aria-hidden="true">🏅</div>
            <div className="stat-card__content">
              <div className="stat-card__value">
                {summary?.badges?.earned ?? 0}
                <span className="stat-card__value-total">
                  /{summary?.badges?.total ?? 0}
                </span>
              </div>
              <div className="stat-card__label">Trophées</div>
              <div className="stat-card__sublabel">
                {summary?.badges?.secret_found ?? 0} secret(s) sur{' '}
                {summary?.badges?.secret_total ?? 0} révélé(s)
              </div>
            </div>
          </div>
        </section>

        {/*
          Une seule grille de trois colonnes, cinq blocs de même facture.

          Il y avait auparavant deux conteneurs — une colonne principale et une
          barre latérale — chacun avec son propre style de carte. Le contenu ne
          suivait pas ce découpage : « Actions rapides » (trois liens) étirait
          les deux tiers de la largeur pendant que « Prochains objectifs »,
          nettement plus dense, se serrait dans le tiers restant.

          Les blocs sont donc désormais placés d'après leur contenu :
              ┌───────────────────────────┬──────────────┐
              │ Continuer l'apprentissage │ Vue d'ensemb.│
              ├──────────────┬────────────┼──────────────┤
              │ Actions rap. │ Objectifs  │ Conseil      │
              └──────────────┴────────────┴──────────────┘
          Les trois blocs d'une même rangée s'alignent en hauteur d'eux-mêmes :
          c'est le comportement par défaut d'une grille, aucun calcul à faire.
        */}
        <div className="dashboard__content">
          {/* Continue Learning */}
          <section className="dashboard__section dashboard__section--wide">
            <div className="dashboard__section-header">
              <h2 className="dashboard__section-title">📚 Continuer l’apprentissage</h2>
              <Link to="/chapters" className="dashboard__section-link">
                Voir tout →
              </Link>
            </div>

            {nextLesson?.lesson ? (
              <div className="learning-card">
                <div className="learning-card__content">
                  <span className="learning-card__kicker">
                    {nextLesson.chapter.title}
                  </span>
                  <h3 className="learning-card__title">{nextLesson.lesson.title}</h3>
                  <p className="learning-card__description">
                    {nextLesson.is_resuming
                      ? 'Vous aviez commencé cette leçon — reprenez où vous en étiez.'
                      : 'La prochaine étape de votre parcours vous attend.'}
                  </p>
                  <div className="learning-card__meta">
                    <span className="learning-card__badge">
                      {LESSON_TYPE_LABELS[nextLesson.lesson.lesson_type] || '📄 Leçon'}
                    </span>
                    <span className="learning-card__duration">
                      ⏱️ {nextLesson.lesson.estimated_duration} min
                    </span>
                    <span className="learning-card__duration">
                      📍 Leçon {nextLesson.chapter_progress.position} sur{' '}
                      {nextLesson.chapter_progress.total}
                    </span>
                  </div>
                </div>
                <Link
                  to={`/lessons/${nextLesson.lesson.slug}`}
                  className="learning-card__button"
                >
                  {nextLesson.is_resuming ? 'Reprendre' : 'Commencer'}
                </Link>
              </div>
            ) : nextLesson?.locked ? (
              /*
                Rien d'ouvert n'est pas « rien de publié ». Un apprenant en
                classe qui a fini ce que son formateur lui a ouvert attend
                la suite : lui annoncer un contenu absent lui ferait croire
                à une panne de la plateforme.
              */
              <div className="learning-card learning-card--empty">
                <div className="learning-card__content">
                  <h3 className="learning-card__title">
                    La suite viendra de votre formateur
                  </h3>
                  <p className="learning-card__description">
                    Vous avez terminé tout ce qui vous est ouvert. Le prochain
                    chapitre s’ouvrira quand votre formateur le décidera.
                  </p>
                </div>
                <Link to="/chapters" className="learning-card__button">
                  Voir le programme
                </Link>
              </div>
            ) : nextLesson?.all_completed ? (
              <div className="learning-card learning-card--done">
                <div className="learning-card__content">
                  <h3 className="learning-card__title">
                    Parcours terminé, félicitations ! 🎉
                  </h3>
                  <p className="learning-card__description">
                    Vous avez complété toutes les leçons disponibles. Il reste
                    peut-être des trophées à décrocher.
                  </p>
                </div>
                <Link to="/badges" className="learning-card__button">
                  Voir mes trophées
                </Link>
              </div>
            ) : (
              <div className="learning-card learning-card--empty">
                <div className="learning-card__content">
                  <h3 className="learning-card__title">Aucune leçon disponible</h3>
                  <p className="learning-card__description">
                    Le contenu n’est pas encore publié. Revenez bientôt !
                  </p>
                </div>
              </div>
            )}
          </section>

          {/* Progress Overview */}
          <section className="dashboard__section">
            <h2 className="dashboard__section-title">
              <span aria-hidden="true">🎯</span> Vue d’ensemble
            </h2>
            <div className="progress-overview">
              <div className="progress-overview__item">
                <div className="progress-overview__label" id="global-progress-label">
                  Progression globale
                  {totalLessons > 0 && (
                    <span className="progress-overview__count">
                      {completedLessons} / {totalLessons} leçons
                    </span>
                  )}
                </div>
                <div
                  className="progress-overview__bar"
                  role="progressbar"
                  aria-labelledby="global-progress-label"
                  aria-valuenow={globalPercent}
                  aria-valuemin={0}
                  aria-valuemax={100}
                >
                  <div
                    className="progress-overview__fill"
                    style={{ width: `${globalPercent}%` }}
                  ></div>
                </div>
                <div className="progress-overview__value">{globalPercent}%</div>
              </div>

              {/*
                Le détail par chapitre est ce qui rend le bloc utile : « 12 sur
                68 » ne dit pas où l'on en est, « chapitre 2 à moitié fait » si.
                Les chapitres verrouillés restent affichés, comme dans le
                sommaire — on montre la suite du parcours, on ne l'ouvre pas.
              */}
              {overview?.chapters?.map((chapter) => (
                <div className="chapter-progress" key={chapter.slug}>
                  <div className="chapter-progress__head">
                    <span className="chapter-progress__title">
                      {!chapter.is_accessible && (
                        <span aria-label="Chapitre verrouillé" title="Chapitre verrouillé">
                          🔒{' '}
                        </span>
                      )}
                      {chapter.title}
                    </span>
                    <span className="chapter-progress__count">
                      {chapter.completed}/{chapter.total}
                    </span>
                  </div>
                  <div
                    className="chapter-progress__bar"
                    role="progressbar"
                    aria-label={`Avancement du chapitre ${chapter.title}`}
                    aria-valuenow={chapter.percent}
                    aria-valuemin={0}
                    aria-valuemax={100}
                  >
                    <div
                      className="chapter-progress__fill"
                      style={{ width: `${chapter.percent}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          {/* Quick Actions */}
          <section className="dashboard__section">
            <h2 className="dashboard__section-title">⚡ Actions rapides</h2>

            <div className="quick-actions">
              <Link to="/chapters" className="quick-action">
                <div className="quick-action__icon">📖</div>
                <div className="quick-action__content">
                  <h3 className="quick-action__title">Explorer les chapitres</h3>
                  <p className="quick-action__description">Découvrez tous nos cours</p>
                </div>
                <span className="quick-action__arrow">→</span>
              </Link>

              <Link to="/progression" className="quick-action">
                <div className="quick-action__icon">📈</div>
                <div className="quick-action__content">
                  <h3 className="quick-action__title">Ma progression</h3>
                  <p className="quick-action__description">Suivez vos résultats</p>
                </div>
                <span className="quick-action__arrow">→</span>
              </Link>

              <Link to="/badges" className="quick-action">
                <div className="quick-action__icon">🏆</div>
                <div className="quick-action__content">
                  <h3 className="quick-action__title">Mes trophées</h3>
                  <p className="quick-action__description">
                    {summary?.badges
                      ? `${summary.badges.earned}/${summary.badges.total} obtenus, ${
                          summary.badges.secret_total - summary.badges.secret_found
                        } encore cachés`
                      : 'Badges obtenus et objectifs cachés'}
                  </p>
                </div>
                <span className="quick-action__arrow">→</span>
              </Link>
            </div>
          </section>

          {/* Prochains objectifs — alimentés par le moteur de badges */}
          <section className="dashboard__section">
            <h2 className="dashboard__section-title">🏆 Prochains objectifs</h2>
            <NextObjectives />
          </section>

          {/*
            Conseil du jour : choisi d'après le comportement réel (série,
            leçons laissées ouvertes, scores, chapitre à portée…), pas écrit
            en dur. Voir `dailyTips.js` pour les règles.

            Le bloc est plus haut que son contenu — il s'aligne sur ses deux
            voisins de rangée. Le conseil se cale donc au milieu de l'espace
            disponible plutôt que de laisser un vide sous une seule phrase.
          */}
          {tip && (
            <section className="dashboard__section dashboard__section--tip">
              <h2 className="dashboard__section-title">💡 Conseil du jour</h2>
              <div className="dashboard__tip-body">
                {/*
                  Guillemet ouvrant, dans le flux et non en position absolue :
                  la première version était posée en absolu puis rognée par
                  l'`overflow` du bloc, ce qui la réduisait à deux virgules
                  perdues dans un coin. En tête de citation, il annonce une
                  parole — le bloc dit une phrase là où ses voisins alignent
                  des chiffres. Décoratif, donc masqué aux lecteurs d'écran.
                */}
                <span className="dashboard__tip-mark" aria-hidden="true">“</span>
                <p className="dashboard__tip-text">{tip.texte}</p>
                {tip.lien && (
                  <Link to={tip.lien.to} className="dashboard__tip-link">
                    {tip.lien.label}
                    <span className="dashboard__tip-arrow" aria-hidden="true">→</span>
                  </Link>
                )}
              </div>
            </section>
          )}
        </div>
      </div>
    </div>
  );
}
