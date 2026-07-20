import { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { fetchLesson, fetchChapterDetails, clearCurrentLesson } from './chaptersSlice';
import {
  fetchMyProgress,
  markLessonCompleted,
  selectLessonStatus,
  selectMarkingCompleted,
  selectProgressByLesson,
} from '../progression/progressionSlice';
import ExerciseInterface from '@/features/exercises/ExerciseInterface';
import QuizInterface from '@/features/quizzes/QuizInterface';
import MarkdownImage from '@/components/ui/MarkdownImage';

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

  const getLessonTypeInfo = (type) => {
    const types = {
      THEORY: { label: 'Théorie', class: 'lesson-header__badge--theory' },
      EXERCISE: { label: 'Exercice', class: 'lesson-header__badge--exercise' },
      QUIZ: { label: 'Quiz', class: 'lesson-header__badge--quiz' },
    };
    return types[type] || types.THEORY;
  };

  const getDifficultyClass = (difficulty) => {
    const classes = {
      EASY: 'lesson-exercise__difficulty--easy',
      MEDIUM: 'lesson-exercise__difficulty--medium',
      HARD: 'lesson-exercise__difficulty--hard',
    };
    return classes[difficulty] || classes.EASY;
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

  // Handler pour marquer la leçon comme terminée
  const handleMarkCompleted = async () => {
    if (currentLesson && !isCompleted) {
      await dispatch(markLessonCompleted(currentLesson.id));
    }
  };

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

        {/* Lesson Header */}
        <div className="lesson-header">
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
            </>
          )}

          {/* Exercise */}
          {currentLesson.lesson_type === 'EXERCISE' && currentLesson.exercise && (
            <ExerciseInterface
              key={currentLesson.id}
              exercise={currentLesson.exercise}
              onSubmit={(code, result) => {
                // Auto-mark as completed if all tests pass
                if (result.success && !isCompleted) {
                  dispatch(markLessonCompleted(currentLesson.id));
                }
              }}
            />
          )}

          {/* Quiz */}
          {currentLesson.lesson_type === 'QUIZ' && currentLesson.quiz && (
            <QuizInterface
              key={currentLesson.id}
              quiz={currentLesson.quiz}
              lessonId={currentLesson.id}
              initialProgress={lessonProgress}
              onSubmit={() => {
                // La notation, la complétion et les points sont gérés
                // côté serveur (submit_quiz) : on resynchronise juste l'état local.
                dispatch(fetchMyProgress());
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

          <button
            className={`lesson-navigation__button lesson-navigation__button--complete ${
              isCompleted ? 'lesson-navigation__button--completed' : ''
            }`}
            onClick={handleMarkCompleted}
            disabled={isCompleted || markingCompleted}
          >
            {isCompleted ? '✓ Leçon terminée' : markingCompleted ? 'Enregistrement...' : 'Marquer comme terminé'}
          </button>

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
