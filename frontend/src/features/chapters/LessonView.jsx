import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams, Link } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { fetchLesson, clearCurrentLesson } from './chaptersSlice';
import ExerciseInterface from '@/features/exercises/ExerciseInterface';
import MarkdownImage from '@/components/ui/MarkdownImage';

export default function LessonView() {
  const { slug } = useParams();
  const dispatch = useDispatch();
  const { currentLesson, loading, error } = useSelector((state) => state.chapters);

  useEffect(() => {
    dispatch(fetchLesson(slug));
    return () => {
      dispatch(clearCurrentLesson());
    };
  }, [dispatch, slug]);

  if (loading) {
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
              exercise={currentLesson.exercise}
              onSubmit={(code, result) => {
                console.log('Code soumis:', code);
                console.log('Résultat:', result);
                // TODO: Implémenter la sauvegarde de la progression
              }}
            />
          )}

          {/* Quiz */}
          {currentLesson.lesson_type === 'QUIZ' && currentLesson.quiz && (
            <div className="lesson-quiz">
              <h2 className="lesson-quiz__header">Quiz</h2>

              {currentLesson.quiz.instructions && (
                <div className="lesson-quiz__instructions">
                  <p>{currentLesson.quiz.instructions}</p>
                </div>
              )}

              <div className="lesson-quiz__meta">
                <span className="lesson-quiz__meta-item">
                  {currentLesson.quiz.question_count} questions
                </span>
                <span className="lesson-quiz__meta-item">
                  Score minimum: {currentLesson.quiz.passing_score}%
                </span>
                {currentLesson.quiz.time_limit > 0 && (
                  <span className="lesson-quiz__meta-item">
                    Temps limite: {currentLesson.quiz.time_limit} min
                  </span>
                )}
              </div>

              <div className="lesson-quiz__placeholder">
                <p>L'interface de quiz interactive sera disponible prochainement.</p>
                <button disabled>Commencer le quiz</button>
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="lesson-navigation">
          <Link
            to={`/chapters/${currentLesson.chapter_slug}`}
            className="lesson-navigation__button lesson-navigation__button--back"
          >
            ← Retour au chapitre
          </Link>

          <button
            className="lesson-navigation__button lesson-navigation__button--complete"
            onClick={() => alert('Fonctionnalité à venir: Marquer comme terminé')}
          >
            Marquer comme terminé
          </button>
        </div>
      </div>
    </div>
  );
}
