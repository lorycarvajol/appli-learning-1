import { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { useParams, Link } from 'react-router-dom';
import { fetchLesson, clearCurrentLesson } from './chaptersSlice';

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
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-xl">Chargement de la leçon...</div>
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

  if (!currentLesson) {
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

  const typeInfo = getLessonTypeLabel(currentLesson.lesson_type);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Breadcrumb */}
        <nav className="mb-8 text-sm">
          <Link to="/chapters" className="text-blue-600 hover:text-blue-800">
            Chapitres
          </Link>
          <span className="mx-2 text-gray-400">/</span>
          <Link
            to={`/chapters/${currentLesson.chapter}`}
            className="text-blue-600 hover:text-blue-800"
          >
            Chapitre
          </Link>
          <span className="mx-2 text-gray-400">/</span>
          <span className="text-gray-600">{currentLesson.title}</span>
        </nav>

        {/* Lesson Header */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          <div className="flex items-center space-x-3 mb-4">
            <span className={`px-3 py-1 rounded-full text-xs font-medium ${typeInfo.color}`}>
              {typeInfo.label}
            </span>
            <span className="text-sm text-gray-500">
              {currentLesson.estimated_duration} min
            </span>
            <span className="text-sm text-gray-500">
              {currentLesson.points} points
            </span>
          </div>

          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            {currentLesson.title}
          </h1>
        </div>

        {/* Lesson Content */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8">
          {/* Theory Content */}
          {currentLesson.lesson_type === 'THEORY' && (
            <div className="prose max-w-none">
              {currentLesson.content ? (
                <div dangerouslySetInnerHTML={{ __html: currentLesson.content }} />
              ) : (
                <p className="text-gray-500">Aucun contenu disponible.</p>
              )}

              {currentLesson.video_url && (
                <div className="mt-8">
                  <h3 className="text-xl font-bold mb-4">Vidéo</h3>
                  <div className="aspect-w-16 aspect-h-9">
                    <iframe
                      src={currentLesson.video_url}
                      className="w-full h-96 rounded-lg"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowFullScreen
                    />
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Exercise */}
          {currentLesson.lesson_type === 'EXERCISE' && currentLesson.exercise && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Exercice</h2>

              <div className="mb-6">
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  currentLesson.exercise.difficulty === 'EASY' ? 'bg-green-100 text-green-800' :
                  currentLesson.exercise.difficulty === 'MEDIUM' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  Difficulté: {currentLesson.exercise.difficulty}
                </span>
              </div>

              <div className="prose max-w-none mb-6">
                <h3 className="text-lg font-semibold mb-2">Instructions</h3>
                <div dangerouslySetInnerHTML={{ __html: currentLesson.exercise.instructions }} />
              </div>

              <div className="bg-gray-50 rounded-lg p-4 mb-6">
                <h3 className="text-lg font-semibold mb-2">Code de départ</h3>
                <pre className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
                  <code>{currentLesson.exercise.starter_code}</code>
                </pre>
              </div>

              <div className="text-center">
                <p className="text-gray-500 italic">
                  L'éditeur de code interactif sera disponible prochainement.
                </p>
              </div>
            </div>
          )}

          {/* Quiz */}
          {currentLesson.lesson_type === 'QUIZ' && currentLesson.quiz && (
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-4">Quiz</h2>

              {currentLesson.quiz.instructions && (
                <div className="prose max-w-none mb-6">
                  <p>{currentLesson.quiz.instructions}</p>
                </div>
              )}

              <div className="mb-6 flex items-center space-x-4 text-sm text-gray-600">
                <span>{currentLesson.quiz.question_count} questions</span>
                <span>•</span>
                <span>Score minimum: {currentLesson.quiz.passing_score}%</span>
                {currentLesson.quiz.time_limit > 0 && (
                  <>
                    <span>•</span>
                    <span>Temps limite: {currentLesson.quiz.time_limit} min</span>
                  </>
                )}
              </div>

              <div className="text-center py-8">
                <p className="text-gray-500 italic mb-4">
                  L'interface de quiz interactive sera disponible prochainement.
                </p>
                <button
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                  disabled
                >
                  Commencer le quiz
                </button>
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          <Link
            to={`/chapters/${currentLesson.chapter}`}
            className="bg-gray-200 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-300 transition-colors"
          >
            ← Retour au chapitre
          </Link>

          <button
            className="bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 transition-colors"
            onClick={() => alert('Fonctionnalité à venir: Marquer comme terminé')}
          >
            Marquer comme terminé
          </button>
        </div>
      </div>
    </div>
  );
}
