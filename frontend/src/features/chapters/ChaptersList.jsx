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
            {chapters.map((chapter) => {
              // `is_accessible` absent (ancienne réponse en cache) : on
              // n'invente pas un verrou, on laisse passer — l'API tranchera.
              const locked = chapter.is_accessible === false

              const body = (
                <>
                  <div className="chapter-card__header">
                    <span className="chapter-card__index">
                      Ch. {String(chapter.order_index).padStart(2, '0')}
                    </span>
                    {locked ? (
                      <span className="chapter-card__badge chapter-card__badge--locked">
                        <span aria-hidden="true">🔒</span> Verrouillé
                      </span>
                    ) : (
                      chapter.is_published && (
                        <span className="chapter-card__badge">Publié</span>
                      )
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

                  {locked && (
                    <p className="chapter-card__locked-hint">
                      Terminez le chapitre précédent, ou attendez que votre
                      formateur l’ouvre.
                    </p>
                  )}
                </>
              )

              // Un chapitre verrouillé reste affiché — il montre la suite du
              // parcours — mais n'est pas cliquable.
              return locked ? (
                <div
                  key={chapter.id}
                  className="chapter-card chapter-card--locked"
                  aria-disabled="true"
                >
                  {body}
                </div>
              ) : (
                <Link
                  key={chapter.id}
                  to={`/chapters/${chapter.slug}`}
                  className="chapter-card"
                >
                  {body}
                </Link>
              )
            })}
          </div>
        )}
      </div>
    </div>
  );
}
