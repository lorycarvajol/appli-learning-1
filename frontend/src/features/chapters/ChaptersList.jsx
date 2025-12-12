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
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl">Chargement des chapitres...</div>
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

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">Chapitres</h1>
          <p className="mt-2 text-lg text-gray-600">
            Explorez les différents chapitres de formation
          </p>
        </div>

        {chapters.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-xl text-gray-500">Aucun chapitre disponible pour le moment.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {chapters.map((chapter) => (
              <Link
                key={chapter.id}
                to={`/chapters/${chapter.slug}`}
                className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden"
              >
                <div className="p-6">
                  <div className="flex items-center justify-between mb-3">
                    <span className="text-sm font-semibold text-blue-600">
                      Chapitre {chapter.order_index}
                    </span>
                    <span className="text-xs text-gray-500">
                      {chapter.estimated_duration} min
                    </span>
                  </div>

                  <h3 className="text-xl font-bold text-gray-900 mb-2">
                    {chapter.title}
                  </h3>

                  <p className="text-gray-600 text-sm line-clamp-3 mb-4">
                    {chapter.description}
                  </p>

                  <div className="flex items-center justify-between text-sm text-gray-500">
                    <span>{chapter.lesson_count} leçons</span>
                    <span className="text-blue-600 font-medium">
                      Commencer →
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
