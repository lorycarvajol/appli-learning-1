import { useEffect, useMemo, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Link } from 'react-router-dom';
import { fetchChapters } from '../chapters/chaptersSlice';
import { fetchMyProgress, selectAllProgress } from './progressionSlice';
import coursesApi from '@/services/api/coursesApi';
import progressionApi from '@/services/api/progressionApi';
import { describeActivity } from '@/constants/activity';
import './ProgressionPage.css';

function formatRelativeTime(dateString) {
  const date = new Date(dateString);
  const diffMin = Math.floor((Date.now() - date.getTime()) / 60000);

  if (diffMin < 1) return "à l'instant";
  if (diffMin < 60) return `il y a ${diffMin} min`;

  const diffHours = Math.floor(diffMin / 60);
  if (diffHours < 24) return `il y a ${diffHours} h`;

  const diffDays = Math.floor(diffHours / 24);
  if (diffDays < 7) return `il y a ${diffDays} j`;

  return date.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
}

function formatDuration(seconds) {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  if (hours > 0) return `${hours}h ${minutes}min`;
  return `${minutes}min`;
}

export default function ProgressionPage() {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const { chapters, loading: chaptersLoading } = useSelector((state) => state.chapters);
  const progressByLesson = useSelector(selectAllProgress);
  const progressLoading = useSelector((state) => state.progression.loading);

  const [chapterLessons, setChapterLessons] = useState({});
  const [activity, setActivity] = useState([]);
  const [activityLoading, setActivityLoading] = useState(true);

  useEffect(() => {
    dispatch(fetchChapters());
    dispatch(fetchMyProgress());
  }, [dispatch]);

  useEffect(() => {
    let cancelled = false;
    progressionApi
      .getMyActivity()
      .then((data) => {
        if (cancelled) return;
        setActivity(Array.isArray(data) ? data : data.results || []);
      })
      .catch(() => {})
      .finally(() => {
        if (!cancelled) setActivityLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (chapters.length === 0) return undefined;
    let cancelled = false;

    Promise.all(
      chapters.map((chapter) =>
        coursesApi
          .getChapter(chapter.slug)
          .then((data) => [chapter.id, data.lessons || []])
      )
    ).then((entries) => {
      if (!cancelled) setChapterLessons(Object.fromEntries(entries));
    });

    return () => {
      cancelled = true;
    };
  }, [chapters]);

  const progressValues = Object.values(progressByLesson);
  const completedLessons = progressValues.filter((p) => p.status === 'COMPLETED').length;
  const inProgressLessons = progressValues.filter((p) => p.status === 'IN_PROGRESS').length;
  const totalTimeSpent = progressValues.reduce((sum, p) => sum + (p.time_spent || 0), 0);
  const avgScore =
    progressValues.length > 0
      ? progressValues.reduce((sum, p) => sum + (p.score || 0), 0) / progressValues.length
      : 0;

  const totalLessonsAvailable = chapters.reduce((sum, c) => sum + (c.lesson_count || 0), 0);
  const overallPercent =
    totalLessonsAvailable > 0 ? Math.round((completedLessons / totalLessonsAvailable) * 100) : 0;

  const orderedChapters = useMemo(
    () => [...chapters].sort((a, b) => a.order_index - b.order_index),
    [chapters]
  );

  const isLoading = (chaptersLoading || progressLoading) && chapters.length === 0;

  if (isLoading) {
    return (
      <div className="progression-loading">
        <div className="loading-spinner"></div>
      </div>
    );
  }

  return (
    <div className="progression-page">
      <div className="progression-container">
        <div className="progression-header">
          <h1 className="progression-header__title">Ma progression</h1>
          <p className="progression-header__subtitle">
            {user?.first_name ? `${user.first_name}, voici` : 'Voici'} où vous en êtes dans votre parcours
          </p>
        </div>

        {/* Vue d'ensemble */}
        <section className="progression-overview" aria-label="Vue d'ensemble">
          <div className="progression-ring-card">
            <div
              className="progression-ring"
              style={{ '--percent': overallPercent }}
              role="progressbar"
              aria-valuenow={overallPercent}
              aria-valuemin={0}
              aria-valuemax={100}
              aria-label="Progression globale du parcours"
            >
              <span className="progression-ring__value">{overallPercent}%</span>
            </div>
            <div className="progression-ring-card__text">
              <span className="progression-ring-card__title">Parcours global</span>
              <span className="progression-ring-card__detail">
                {completedLessons} / {totalLessonsAvailable || '—'} leçons terminées
              </span>
            </div>
          </div>

          <div className="progression-stats">
            <div className="progression-stat">
              <span className="progression-stat__value">{user?.profile?.total_points || 0}</span>
              <span className="progression-stat__label">Points</span>
            </div>
            <div className="progression-stat">
              <span className="progression-stat__value">{inProgressLessons}</span>
              <span className="progression-stat__label">En cours</span>
            </div>
            <div className="progression-stat">
              <span className="progression-stat__value">{formatDuration(totalTimeSpent)}</span>
              <span className="progression-stat__label">Temps investi</span>
            </div>
            <div className="progression-stat">
              <span className="progression-stat__value">{Math.round(avgScore)}%</span>
              <span className="progression-stat__label">Score moyen</span>
            </div>
          </div>
        </section>

        <div className="progression-content">
          {/* Progression par chapitre */}
          <section className="progression-section">
            <h2 className="progression-section__title">Par chapitre</h2>

            {orderedChapters.length === 0 ? (
              <p className="progression-empty">Aucun chapitre disponible pour le moment.</p>
            ) : (
              <ol className="progression-chapters">
                {orderedChapters.map((chapter) => {
                  const lessons = [...(chapterLessons[chapter.id] || [])].sort(
                    (a, b) => a.order_index - b.order_index
                  );
                  const total = lessons.length || chapter.lesson_count || 0;
                  const completedInChapter = lessons.filter(
                    (l) => progressByLesson[l.id]?.status === 'COMPLETED'
                  ).length;
                  const percent = total > 0 ? Math.round((completedInChapter / total) * 100) : 0;

                  return (
                    <li key={chapter.id} className="progression-chapter">
                      <Link to={`/chapters/${chapter.slug}`} className="progression-chapter__link">
                        <div className="progression-chapter__head">
                          <span className="progression-chapter__index">
                            Ch. {String(chapter.order_index).padStart(2, '0')}
                          </span>
                          <span className="progression-chapter__title">{chapter.title}</span>
                          <span className="progression-chapter__count">
                            {completedInChapter}/{total} leçons
                          </span>
                        </div>

                        <div
                          className="progression-chapter__bar"
                          role="progressbar"
                          aria-valuenow={percent}
                          aria-valuemin={0}
                          aria-valuemax={100}
                          aria-label={`Progression du chapitre ${chapter.title}`}
                        >
                          <div className="progression-chapter__fill" style={{ width: `${percent}%` }} />
                        </div>

                        {lessons.length > 0 && (
                          <ul className="progression-chapter__dots" aria-hidden="true">
                            {lessons.map((lesson) => {
                              const status = progressByLesson[lesson.id]?.status || 'NOT_STARTED';
                              return (
                                <li
                                  key={lesson.id}
                                  className={`progression-dot progression-dot--${status.toLowerCase()}`}
                                  title={lesson.title}
                                ></li>
                              );
                            })}
                          </ul>
                        )}
                      </Link>
                    </li>
                  );
                })}
              </ol>
            )}
          </section>

          {/* Activité récente */}
          <section className="progression-section progression-section--activity">
            <h2 className="progression-section__title">Activité récente</h2>

            {activityLoading ? (
              <div className="progression-activity-loading">
                <div className="loading-spinner"></div>
              </div>
            ) : activity.length === 0 ? (
              <p className="progression-empty">
                Aucune activité pour le moment. Terminez une leçon pour la voir apparaître ici.
              </p>
            ) : (
              <ul className="progression-activity">
                {activity.slice(0, 12).map((item) => {
                  const { icon, label } = describeActivity(item);
                  return (
                    <li key={item.id} className="progression-activity__item">
                      <span className="progression-activity__icon" aria-hidden="true">
                        {icon}
                      </span>
                      <span className="progression-activity__text">{label}</span>
                      <time
                        className="progression-activity__time"
                        dateTime={item.created_at}
                      >
                        {formatRelativeTime(item.created_at)}
                      </time>
                    </li>
                  );
                })}
              </ul>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
