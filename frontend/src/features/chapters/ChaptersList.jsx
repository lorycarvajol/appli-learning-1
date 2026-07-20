import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { fetchChapters } from './chaptersSlice';

export default function ChaptersList() {
  const dispatch = useDispatch();
  const { chapters, loading, error } = useSelector((state) => state.chapters);

  useEffect(() => {
    dispatch(fetchChapters());
  }, [dispatch]);

  if (loading) {
    return (
      <div className="chapters-loading">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="chapters-error">
        <div className="chapters-error__message">Erreur: {error}</div>
      </div>
    );
  }

  return (
    <div className="chapters-page">
      <div className="chapters-container">
        <div className="chapters-header">
          <h1 className="chapters-header__title">Chapitres</h1>
          <p className="chapters-header__subtitle">
            Explorez les différents chapitres de formation
          </p>
        </div>

        {chapters.length === 0 ? (
          <div className="chapters-empty">
            <h2 className="chapters-empty__title">Aucun chapitre disponible</h2>
            <p className="chapters-empty__message">
              Les chapitres seront bientôt disponibles.
            </p>
          </div>
        ) : (
          <div className="chapters-grid">
            {chapters.map((chapter) => (
              <Link
                key={chapter.id}
                to={`/chapters/${chapter.slug}`}
                className="chapter-card"
              >
                <div className="chapter-card__header">
                  <span className="chapter-card__index">
                    Ch. {String(chapter.order_index).padStart(2, '0')}
                  </span>
                  {chapter.is_published && (
                    <span className="chapter-card__badge">Publié</span>
                  )}
                </div>

                <h3 className="chapter-card__title">{chapter.title}</h3>

                <p className="chapter-card__description">
                  {chapter.description}
                </p>

                <div className="chapter-card__meta">
                  <span className="chapter-card__meta-item">
                    {chapter.estimated_duration} min
                  </span>
                  <span className="chapter-card__meta-item">
                    {chapter.lesson_count || 0} leçons
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
