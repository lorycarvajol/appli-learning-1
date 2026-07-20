import { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import CodeEditor from '@/components/ui/CodeEditor';
import validationApi from '@/services/api/validationApi';
import './ExerciseInterface.css';

/**
 * ExerciseInterface - Interface complète pour un exercice de code
 *
 * @param {object} exercise - Objet exercice contenant instructions, starter_code, language, etc.
 * @param {function} onSubmit - Callback appelé lors de la soumission du code
 */
export default function ExerciseInterface({ exercise, onSubmit }) {
  const [code, setCode] = useState(exercise.starter_code || '');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [testResults, setTestResults] = useState(null);
  const [showHints, setShowHints] = useState(false);

  // Réinitialiser le code quand l'exercice change
  useEffect(() => {
    setCode(exercise.starter_code || '');
    setTestResults(null);
  }, [exercise.id]);

  // Gérer la soumission du code
  const handleSubmit = async () => {
    setIsSubmitting(true);
    setTestResults(null); // Reset des résultats précédents

    try {
      // Soumet le code puis attend le résultat (exécution asynchrone côté serveur)
      const result = await validationApi.submitCodeAndWait(exercise.id, code);
      setTestResults(result);

      if (onSubmit) {
        onSubmit(code, result);
      }
    } catch (error) {
      console.error('Erreur lors de la soumission:', error);
      setTestResults({
        success: false,
        error: error.message || 'Une erreur est survenue lors de la validation',
        results: [],
        total_points: 0,
        max_points: 0,
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  // Réinitialiser le code au starter_code
  const handleReset = () => {
    if (window.confirm('Voulez-vous vraiment réinitialiser votre code ?')) {
      setCode(exercise.starter_code || '');
      setTestResults(null);
    }
  };

  const getDifficultyClass = (difficulty) => {
    const classes = {
      EASY: 'exercise-difficulty--easy',
      MEDIUM: 'exercise-difficulty--medium',
      HARD: 'exercise-difficulty--hard',
    };
    return classes[difficulty] || classes.EASY;
  };

  const getDifficultyLabel = (difficulty) => {
    const labels = {
      EASY: 'Facile',
      MEDIUM: 'Moyen',
      HARD: 'Difficile',
    };
    return labels[difficulty] || difficulty;
  };

  return (
    <div className="exercise-interface">
      {/* En-tête de l'exercice */}
      <div className="exercise-header">
        <div className="exercise-header__meta">
          <span className={`exercise-difficulty ${getDifficultyClass(exercise.difficulty)}`}>
            {getDifficultyLabel(exercise.difficulty)}
          </span>
          <span className="exercise-language">
            {exercise.language?.toUpperCase() || 'HTML'}
          </span>
        </div>
      </div>

      {/* Instructions */}
      <div className="exercise-instructions">
        <h3 className="exercise-instructions__title">Instructions</h3>
        <div className="exercise-instructions__content">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>
            {exercise.instructions || 'Aucune instruction fournie.'}
          </ReactMarkdown>
        </div>
      </div>

      {/* Hints (indices) */}
      {exercise.hints && exercise.hints.length > 0 && (
        <div className="exercise-hints">
          <button
            className="exercise-hints__toggle"
            onClick={() => setShowHints(!showHints)}
          >
            {showHints ? '▼' : '▶'} Indices ({exercise.hints.length})
          </button>

          {showHints && (
            <div className="exercise-hints__content">
              {exercise.hints.map((hint, index) => (
                <div key={index} className="exercise-hint">
                  <span className="exercise-hint__number">Indice {index + 1}:</span>
                  <span className="exercise-hint__text">{hint}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Éditeur de code */}
      <div className="exercise-editor">
        <div className="exercise-editor__header">
          <h3 className="exercise-editor__title">Votre code</h3>
          <button
            className="exercise-editor__reset"
            onClick={handleReset}
            disabled={isSubmitting}
          >
            Réinitialiser
          </button>
        </div>

        <CodeEditor
          value={code}
          onChange={setCode}
          language={exercise.language || 'html'}
          height={450}
          theme="vs-dark"
        />
      </div>

      {/* Bouton de soumission */}
      <div className="exercise-actions">
        <button
          className="exercise-submit-button"
          onClick={handleSubmit}
          disabled={isSubmitting}
        >
          {isSubmitting ? (
            <>
              <div className="button-spinner"></div>
              Validation en cours...
            </>
          ) : (
            'Soumettre le code'
          )}
        </button>
      </div>

      {/* Résultats des tests */}
      {testResults && (
        <div className={`exercise-results ${testResults.success ? 'exercise-results--success' : 'exercise-results--error'}`}>
          <div className="exercise-results__header">
            <h3 className="exercise-results__title">
              {testResults.success ? '✓ Succès !' : '✗ Échec'}
            </h3>
            <p className="exercise-results__message">{testResults.message}</p>
          </div>

          {testResults.results && testResults.results.length > 0 && (
            <div className="exercise-results__tests">
              <h4 className="exercise-results__tests-title">Résultats des tests :</h4>
              <ul className="exercise-results__tests-list">
                {testResults.results.map((test, index) => (
                  <li
                    key={index}
                    className={`exercise-test ${test.passed ? 'exercise-test--passed' : 'exercise-test--failed'}`}
                  >
                    <span className="exercise-test__icon">
                      {test.passed ? '✓' : '✗'}
                    </span>
                    <div className="exercise-test__content">
                      <span className="exercise-test__name">{test.name}</span>
                      {test.message && (
                        <span className="exercise-test__message">{test.message}</span>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {testResults.error && (
            <div className="exercise-results__error">
              <strong>Erreur :</strong> {testResults.error}
            </div>
          )}
        </div>
      )}

      {/* Note pour l'utilisateur */}
      <div className="exercise-note">
        <strong>💻 Validation automatique :</strong> Votre code est exécuté dans un environnement
        Docker sécurisé et isolé. Les tests définis pour l'exercice vérifient automatiquement
        la validité de votre solution.
      </div>
    </div>
  );
}
