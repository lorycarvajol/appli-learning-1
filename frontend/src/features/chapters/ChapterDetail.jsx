import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams, Link } from 'react-router-dom';
import { fetchChapterDetails, clearCurrentChapter } from './chaptersSlice';

export default function ChapterDetail() {
  const { slug } = useParams();
  const dispatch = useDispatch();
  const { currentChapter, loading, error } = useSelector((state) => state.chapters);

  useEffect(() => {
    dispatch(fetchChapterDetails(slug));
    return () => {
      dispatch(clearCurrentChapter());
    };
  }, [dispatch, slug]);

  if (loading) {
    return (
      <div className="chapter-detail-loading">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chapter-detail-error">
        <div className="chapter-detail-error__message">
          Erreur: {typeof error === 'object' ? error.detail || JSON.stringify(error) : error}
        </div>
      </div>
    );
  }

  if (!currentChapter) {
    return null;
  }

  const getLessonTypeInfo = (type) => {
    const types = {
      THEORY: { label: 'Théorie', class: 'lesson-card__badge--theory' },
      EXERCISE: { label: 'Exercice', class: 'lesson-card__badge--exercise' },
      QUIZ: { label: 'Quiz', class: 'lesson-card__badge--quiz' },
    };
    return types[type] || types.THEORY;
  };

  return (
    <div className="chapter-detail-page">
      {/* Breadcrumb - sticky */}
      <nav className="chapter-breadcrumb">
        <div className="chapter-detail-container">
          <Link to="/chapters" className="chapter-breadcrumb__link">
            Chapitres
          </Link>
          <span className="chapter-breadcrumb__separator">/</span>
          <span className="chapter-breadcrumb__current">{currentChapter.title}</span>
        </div>
      </nav>

      <div className="chapter-detail-container">

        {/* Chapter Header */}
        <div className="chapter-detail-header">
          <h1 className="chapter-detail-header__title">{currentChapter.title}</h1>

          <p className="chapter-detail-header__description">
            {currentChapter.description}
          </p>

          <div className="chapter-detail-header__meta">
            <div className="chapter-detail-header__meta-item">
              <strong>Chapitre {currentChapter.order_index}</strong>
            </div>
            <div className="chapter-detail-header__meta-item">
              Durée estimée: <strong>{currentChapter.estimated_duration} min</strong>
            </div>
            <div className="chapter-detail-header__meta-item">
              <strong>{currentChapter.lesson_count || 0}</strong> leçons
            </div>
            {currentChapter.is_published && (
              <span className="chapter-detail-header__badge">Publié</span>
            )}
          </div>
        </div>

        {/* Lessons List */}
        <div className="lessons-section">
          <h2 className="lessons-section__title">Leçons</h2>

          {currentChapter.lessons && currentChapter.lessons.length > 0 ? (
            <div className="lessons-list">
              {currentChapter.lessons.map((lesson) => {
                const typeInfo = getLessonTypeInfo(lesson.lesson_type);
                return (
                  <Link
                    key={lesson.id}
                    to={`/lessons/${lesson.slug}`}
                    className="lesson-card"
                  >
                    <div className="lesson-card__number">
                      {lesson.order_index}
                    </div>

                    <div className="lesson-card__content">
                      <div className="lesson-card__header">
                        <h3 className="lesson-card__title">{lesson.title}</h3>
                        <div className="lesson-card__badges">
                          <span className={`lesson-card__badge ${typeInfo.class}`}>
                            {typeInfo.label}
                          </span>
                        </div>
                      </div>

                      <div className="lesson-card__meta">
                        <span className="lesson-card__meta-item">
                          {lesson.estimated_duration} min
                        </span>
                        <span className="lesson-card__meta-item">
                          {lesson.points} points
                        </span>
                      </div>
                    </div>

                    <button className="lesson-card__button">
                      Commencer
                    </button>
                  </Link>
                );
              })}
            </div>
          ) : (
            <div className="chapters-empty">
              <p className="chapters-empty__message">
                Aucune leçon disponible dans ce chapitre.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
