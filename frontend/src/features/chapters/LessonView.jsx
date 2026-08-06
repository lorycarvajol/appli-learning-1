import { useCallback, useEffect, lazy, Suspense } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { fetchLesson, fetchChapterDetails, clearCurrentLesson } from './chaptersSlice';
import { lessonIllustration } from './illustrations';
import {
  fetchMyProgress,
  markLessonCompleted,
  selectLessonStatus,
  selectMarkingCompleted,
  selectProgressByLesson,
} from '../progression/progressionSlice';
import useTimeTracker from '../progression/useTimeTracker';
import useScrollCompletion from '../progression/useScrollCompletion';
import { badgesEarned } from '@/features/gamification/gamificationSlice';
import QuizInterface from '@/features/quizzes/QuizInterface';
import MarkdownImage from '@/components/ui/MarkdownImage';
import PageLoader from '@/components/ui/PageLoader';

// L'éditeur Monaco embarqué par `ExerciseInterface` est de loin la plus lourde
// dépendance de l'app. Chargé à la demande, il ne pèse que sur les leçons de
// type EXERCICE — la théorie et les quiz ne le téléchargent jamais.
const ExerciseInterface = lazy(() => import('@/features/exercises/ExerciseInterface'));

export default function LessonView() {
  const { slug } = useParams();
  const dispatch = useDispatch();
  const { currentLesson, currentChapter, loading, error } = useSelector((state) => state.chapters);
  const markingCompleted = useSelector(selectMarkingCompleted);
  const lessonStatus = useSelector(
    currentLesson ? selectLessonStatus(currentLesson.id) : () => 'NOT_STARTED'
  );
  const lessonProgress = useSelector(
    currentLesson ? selectProgressByLesson(currentLesson.id) : () => null
  );
  const isCompleted = lessonStatus === 'COMPLETED';

  // Mesure le temps réellement passé sur la leçon (onglet visible + apprenant
  // actif). Doit être appelé avant les retours anticipés de rendu.
  useTimeTracker(currentLesson?.id);

  const isTheory = currentLesson?.lesson_type === 'THEORY';

  const completeOnScroll = useCallback(() => {
    if (currentLesson) dispatch(markLessonCompleted(currentLesson.id));
  }, [dispatch, currentLesson]);

  // La théorie se valide en atteignant le bas du contenu. Les exercices et les
  // quiz ont leur propre condition de réussite (tests passés, score atteint) :
  // les valider au défilement distribuerait leurs points sans le travail.
  const { sentinelRef, reached } = useScrollCompletion({
    enabled: Boolean(currentLesson) && isTheory && !isCompleted,
    onComplete: completeOnScroll,
    resetOn: currentLesson?.id,
  });

  useEffect(() => {
    dispatch(fetchLesson(slug));
    return () => {
      dispatch(clearCurrentLesson());
    };
  }, [dispatch, slug]);

  // Nécessaire pour connaître le statut/les réponses sauvegardées même en
  // arrivant directement sur une leçon (lien direct, rafraîchissement...)
  useEffect(() => {
    dispatch(fetchMyProgress());
  }, [dispatch]);

  // Charge les leçons du chapitre (une seule fois par chapitre) pour permettre
  // la navigation directe précédent/suivant sans repasser par /chapters/:slug
  useEffect(() => {
    if (currentLesson?.chapter_slug && currentChapter?.slug !== currentLesson.chapter_slug) {
      dispatch(fetchChapterDetails(currentLesson.chapter_slug));
    }
  }, [dispatch, currentLesson?.chapter_slug, currentChapter?.slug]);

  // Remonte en haut de page à chaque changement de leçon
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }, [slug]);

  if (loading && !currentLesson) {
    return (
      <div className="lesson-loading">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="lesson-error">
        <div className="lesson-error__message">Erreur: {error}</div>
      </div>
    );
  }

  if (!currentLesson) {
    return null;
  }

  // Le slug vient de la route : c'est la même valeur que celle de la leçon
  // chargée, mais disponible sans dépendre des champs exposés par l'API.
  const illustration = lessonIllustration(slug);

  const getLessonTypeInfo = (type) => {
    const types = {
      THEORY: { label: 'Théorie', class: 'lesson-header__badge--theory' },
      EXERCISE: { label: 'Exercice', class: 'lesson-header__badge--exercise' },
      QUIZ: { label: 'Quiz', class: 'lesson-header__badge--quiz' },
    };
    return types[type] || types.THEORY;
  };

  const typeInfo = getLessonTypeInfo(currentLesson.lesson_type);

  // Leçon précédente / suivante au sein du chapitre (navigation directe)
  let prevLesson = null;
  let nextLesson = null;
  if (currentChapter?.slug === currentLesson.chapter_slug && currentChapter?.lessons) {
    const orderedLessons = [...currentChapter.lessons].sort(
      (a, b) => a.order_index - b.order_index
    );
    const currentIndex = orderedLessons.findIndex((l) => l.slug === currentLesson.slug);
    if (currentIndex > 0) {
      prevLesson = orderedLessons[currentIndex - 1];
    }
    if (currentIndex !== -1 && currentIndex < orderedLessons.length - 1) {
      nextLesson = orderedLessons[currentIndex + 1];
    }
  }

  // La leçon n'est plus déclarée terminée par l'apprenant mais constatée par
  // l'application : le libellé explique donc ce qui reste à faire, plutôt que
  // d'offrir un bouton.
  const pendingLabel = {
    THEORY: 'Faites défiler jusqu’en bas pour valider la leçon',
    EXERCISE: 'Validée dès que tous les tests passent',
    QUIZ: 'Validée dès que le score requis est atteint',
  }[currentLesson.lesson_type] ?? '';

  let completionLabel = pendingLabel;
  if (isCompleted) {
    completionLabel = '✓ Leçon terminée';
  } else if (markingCompleted || reached) {
    completionLabel = 'Enregistrement…';
  }

  // Composants personnalisés pour ReactMarkdown
  const markdownComponents = {
    img: MarkdownImage,
  };

  return (
    <div className="lesson-page">
      {/* Breadcrumb - sticky */}
      <nav className="lesson-breadcrumb">
        <div className="lesson-container">
          <Link to="/chapters" className="lesson-breadcrumb__link">
            Chapitres
          </Link>
          <span className="lesson-breadcrumb__separator">/</span>
          <Link
            to={`/chapters/${currentLesson.chapter_slug}`}
            className="lesson-breadcrumb__link"
          >
            Chapitre
          </Link>
          <span className="lesson-breadcrumb__separator">/</span>
          <span className="lesson-breadcrumb__current">{currentLesson.title}</span>
        </div>
      </nav>

      <div className="lesson-container">

        {/*
          Lesson Header — l'illustration de la leçon s'y pose en fond, floutée
          et effacée du côté du texte (composant `lesson-illustration`). Une
          leçon sans illustration n'a pas la classe : l'en-tête reste tel quel.
        */}
        <div
          className={`lesson-header ${illustration ? 'lesson-illustration' : ''}`}
          style={illustration ? { '--lesson-illus': `url(${illustration})` } : undefined}
        >
          <div className="lesson-header__meta">
            <span className={`lesson-header__badge ${typeInfo.class}`}>
              {typeInfo.label}
            </span>
            <span className="lesson-header__info">
              {currentLesson.estimated_duration} min
            </span>
            <span className="lesson-header__info">
              {currentLesson.points} points
            </span>
          </div>

          <h1 className="lesson-header__title">{currentLesson.title}</h1>
        </div>

        {/* Lesson Content */}
        <div className="lesson-content">
          {/* Theory Content */}
          {currentLesson.lesson_type === 'THEORY' && (
            <>
              <div className="lesson-markdown">
                {currentLesson.content ? (
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={markdownComponents}
                  >
                    {currentLesson.content}
                  </ReactMarkdown>
                ) : (
                  <p>Aucun contenu disponible.</p>
                )}
              </div>

              {currentLesson.video_url && (
                <div className="lesson-video">
                  <h3 className="lesson-video__title">Vidéo</h3>
                  <div className="lesson-video__wrapper">
                    <iframe
                      src={currentLesson.video_url}
                      title={`Vidéo — ${currentLesson.title}`}
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                    />
                  </div>
                </div>
              )}

              {/* Repère de fin de lecture : son entrée durable dans la fenêtre
                  vaut validation de la leçon (cf. useScrollCompletion). Placé
                  après la vidéo pour qu'une leçon vidéo ne se valide pas dès
                  la fin du texte. */}
              <div ref={sentinelRef} aria-hidden="true" className="lesson-content__end" />
            </>
          )}

          {/* Exercise */}
          {currentLesson.lesson_type === 'EXERCISE' && currentLesson.exercise && (
            <Suspense fallback={<PageLoader />}>
              <ExerciseInterface
                key={currentLesson.id}
                exercise={currentLesson.exercise}
                onSubmit={(code, result) => {
                  // La complétion et les points sont constatés **côté
                  // serveur** quand les tests passent (cf.
                  // `validation.tasks._constater_la_reussite`) : on se contente
                  // de resynchroniser l'état local, comme pour les quiz.
                  //
                  // Le front déclarait auparavant lui-même la réussite en
                  // appelant `mark_completed` — c'était laisser au client le
                  // soin de s'attribuer les points.
                  if (result.success) {
                    dispatch(fetchMyProgress());
                  }
                }}
              />
            </Suspense>
          )}

          {/* Quiz */}
          {currentLesson.lesson_type === 'QUIZ' && currentLesson.quiz && (
            <QuizInterface
              key={currentLesson.id}
              quiz={currentLesson.quiz}
              lessonId={currentLesson.id}
              initialProgress={lessonProgress}
              onSubmit={(result) => {
                // La notation, la complétion et les points sont gérés
                // côté serveur (submit_quiz) : on resynchronise juste l'état local.
                dispatch(fetchMyProgress());
                dispatch(badgesEarned(result?.new_badges));
              }}
            />
          )}
        </div>

        {/* Navigation */}
        <div className="lesson-navigation">
          <div className="lesson-navigation__side">
            {prevLesson ? (
              <Link
                to={`/lessons/${prevLesson.slug}`}
                className="lesson-navigation__button lesson-navigation__button--prev"
              >
                <span className="lesson-navigation__arrow">←</span>
                <span className="lesson-navigation__text">
                  <span className="lesson-navigation__label">Précédent</span>
                  <span className="lesson-navigation__title">{prevLesson.title}</span>
                </span>
              </Link>
            ) : (
              <Link
                to={`/chapters/${currentLesson.chapter_slug}`}
                className="lesson-navigation__button lesson-navigation__button--back"
              >
                ← Retour au chapitre
              </Link>
            )}
          </div>

          <p
            className={`lesson-status ${isCompleted ? 'lesson-status--done' : ''}`}
            role="status"
            aria-label="Statut de la leçon"
          >
            {completionLabel}
          </p>

          <div className="lesson-navigation__side lesson-navigation__side--right">
            {nextLesson ? (
              <Link
                to={`/lessons/${nextLesson.slug}`}
                className="lesson-navigation__button lesson-navigation__button--next"
              >
                <span className="lesson-navigation__text">
                  <span className="lesson-navigation__label">Suivant</span>
                  <span className="lesson-navigation__title">{nextLesson.title}</span>
                </span>
                <span className="lesson-navigation__arrow">→</span>
              </Link>
            ) : (
              <Link
                to={`/chapters/${currentLesson.chapter_slug}`}
                className="lesson-navigation__button lesson-navigation__button--finish"
              >
                Terminer le chapitre ✓
              </Link>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
