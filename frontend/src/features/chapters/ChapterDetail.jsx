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
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl">Chargement du chapitre...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl text-red-600">Erreur: {error}</div>
      </div>
    );
  }

  if (!currentChapter) {
    return null;
  }

  const getLessonTypeLabel = (type) => {
    const types = {
      THEORY: { label: 'Théorie', color: 'bg-blue-100 text-blue-800' },
      EXERCISE: { label: 'Exercice', color: 'bg-green-100 text-green-800' },
      QUIZ: { label: 'Quiz', color: 'bg-purple-100 text-purple-800' },
    };
    return types[type] || types.THEORY;
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Breadcrumb */}
        <nav className="mb-8 text-sm">
          <Link to="/chapters" className="text-blue-600 hover:text-blue-800">
            Chapitres
          </Link>
          <span className="mx-2 text-gray-400">/</span>
          <span className="text-gray-600">{currentChapter.title}</span>
        </nav>

        {/* Chapter Header */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm font-semibold text-blue-600">
              Chapitre {currentChapter.order_index}
            </span>
            <span className="text-sm text-gray-500">
              {currentChapter.estimated_duration} min
            </span>
          </div>

          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            {currentChapter.title}
          </h1>

          <p className="text-lg text-gray-600 mb-6">
            {currentChapter.description}
          </p>

          <div className="flex items-center space-x-6 text-sm text-gray-500">
            <span>{currentChapter.lesson_count} leçons</span>
          </div>
        </div>

        {/* Lessons List */}
        <div className="bg-white rounded-lg shadow-md p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Leçons</h2>

          {currentChapter.lessons && currentChapter.lessons.length > 0 ? (
            <div className="space-y-4">
              {currentChapter.lessons.map((lesson) => {
                const typeInfo = getLessonTypeLabel(lesson.lesson_type);
                return (
                  <Link
                    key={lesson.id}
                    to={`/lessons/${lesson.slug}`}
                    className="block border border-gray-200 rounded-lg p-6 hover:border-blue-500 hover:shadow-md transition-all duration-200"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <span className="text-sm font-semibold text-gray-400">
                            {currentChapter.order_index}.{lesson.order_index}
                          </span>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${typeInfo.color}`}>
                            {typeInfo.label}
                          </span>
                        </div>

                        <h3 className="text-lg font-bold text-gray-900 mb-1">
                          {lesson.title}
                        </h3>

                        <div className="flex items-center space-x-4 text-sm text-gray-500 mt-3">
                          <span>{lesson.estimated_duration} min</span>
                          <span>{lesson.points} points</span>
                        </div>
                      </div>

                      <div className="ml-4">
                        <span className="text-blue-600 font-medium">→</span>
                      </div>
                    </div>
                  </Link>
                );
              })}
            </div>
          ) : (
            <p className="text-gray-500 text-center py-8">
              Aucune leçon disponible dans ce chapitre.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
