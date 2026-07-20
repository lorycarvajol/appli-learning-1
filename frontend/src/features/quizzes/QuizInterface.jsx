import { useState, useEffect, useCallback, useRef } from 'react';
import progressionApi from '@/services/api/progressionApi';
import './QuizInterface.css';

const AUTOSAVE_DELAY_MS = 800;

function shuffledIndices(length) {
  const order = Array.from({ length }, (_, i) => i);
  for (let i = order.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [order[i], order[j]] = [order[j], order[i]];
  }
  return order;
}

/**
 * QuizInterface - Interface interactive pour les quiz
 *
 * La notation se fait exclusivement côté serveur (les bonnes réponses ne
 * sont jamais envoyées au client avant la soumission). Les réponses en
 * cours sont sauvegardées automatiquement au fur et à mesure, et les points
 * ne peuvent être crédités qu'une seule fois (géré côté serveur).
 *
 * @param {object} quiz - Objet quiz (questions sans correct_answer, passing_score, time_limit...)
 * @param {string} lessonId - ID de la leçon, nécessaire pour sauvegarder/soumettre
 * @param {object} initialProgress - Progression déjà connue pour cette leçon (quiz_answers, is_passed, score...)
 * @param {function} onSubmit - Callback appelé après une soumission réussie, avec le résultat noté
 */
function buildOptionOrder(questions, randomize) {
  if (!randomize) return {};
  return Object.fromEntries(
    questions.map((q) => [q.id, shuffledIndices(q.options.length)])
  );
}

export default function QuizInterface({ quiz, lessonId, initialProgress, onSubmit }) {
  const questions = Array.isArray(quiz.questions) ? quiz.questions : [];

  const [quizStarted, setQuizStarted] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState(initialProgress?.quiz_answers || {});
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [submitResult, setSubmitResult] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);
  // Ordre d'affichage des options par question (mélangé une fois par
  // tentative si quiz.randomize_options, pour ne jamais laisser la bonne
  // réponse toujours à la même position). Les indices stockés dans
  // userAnswers restent toujours les indices d'origine.
  const [optionOrder, setOptionOrder] = useState(() =>
    buildOptionOrder(questions, quiz.randomize_options)
  );

  const autosaveTimeoutRef = useRef(null);

  const totalQuestions = questions.length;
  const currentQuestion = questions[currentQuestionIndex];
  const currentOptionOrder =
    currentQuestion && optionOrder[currentQuestion.id]
      ? optionOrder[currentQuestion.id]
      : currentQuestion?.options.map((_, i) => i) || [];

  const alreadyPassed = initialProgress?.is_passed;
  const attemptsSoFar = initialProgress?.attempts || 0;
  const attemptsExhausted =
    quiz.max_attempts > 0 && attemptsSoFar >= quiz.max_attempts && !alreadyPassed;

  // Sauvegarde automatique des réponses en cours (debounce)
  useEffect(() => {
    if (!quizStarted || showResults || !lessonId) return undefined;

    if (autosaveTimeoutRef.current) clearTimeout(autosaveTimeoutRef.current);
    autosaveTimeoutRef.current = setTimeout(() => {
      progressionApi.saveQuizProgress(lessonId, userAnswers).catch(() => {});
    }, AUTOSAVE_DELAY_MS);

    return () => clearTimeout(autosaveTimeoutRef.current);
  }, [userAnswers, quizStarted, showResults, lessonId]);

  const handleSubmitQuiz = useCallback(async () => {
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      const result = await progressionApi.submitQuiz(lessonId, userAnswers);
      setSubmitResult(result);
      setShowResults(true);
      if (onSubmit) onSubmit(result);
    } catch (error) {
      setSubmitError(
        error.response?.data?.error || 'Une erreur est survenue lors de la soumission du quiz.'
      );
    } finally {
      setIsSubmitting(false);
    }
  }, [lessonId, userAnswers, onSubmit]);

  // Timer countdown
  useEffect(() => {
    if (quizStarted && quiz.time_limit > 0 && timeRemaining > 0 && !showResults) {
      const timer = setInterval(() => {
        setTimeRemaining((prev) => {
          if (prev <= 1) {
            handleSubmitQuiz();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
    return undefined;
  }, [quizStarted, timeRemaining, showResults, quiz.time_limit, handleSubmitQuiz]);

  if (totalQuestions === 0) {
    return (
      <div className="quiz-interface">
        <div className="quiz-start">
          <p>Aucune question n'est disponible pour ce quiz.</p>
        </div>
      </div>
    );
  }

  const handleStartQuiz = () => {
    setQuizStarted(true);
    if (quiz.time_limit > 0) {
      setTimeRemaining(quiz.time_limit * 60);
    }
  };

  const handleSelectAnswer = (questionId, optionIndex) => {
    const question = questions.find((q) => q.id === questionId);

    if (question.type === 'multiple') {
      const currentAnswers = userAnswers[questionId] || [];
      const newAnswers = currentAnswers.includes(optionIndex)
        ? currentAnswers.filter((idx) => idx !== optionIndex)
        : [...currentAnswers, optionIndex];

      setUserAnswers({ ...userAnswers, [questionId]: newAnswers });
    } else {
      setUserAnswers({ ...userAnswers, [questionId]: [optionIndex] });
    }
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < totalQuestions - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleGoToQuestion = (index) => {
    setCurrentQuestionIndex(index);
  };

  const handleRetry = () => {
    setQuizStarted(false);
    setCurrentQuestionIndex(0);
    setUserAnswers({});
    setShowResults(false);
    setSubmitResult(null);
    setSubmitError(null);
    setTimeRemaining(null);
    setOptionOrder(buildOptionOrder(questions, quiz.randomize_options));
  };

  const formatTime = (seconds) => {
    if (seconds === null) return '';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const allQuestionsAnswered = questions.every((q) => userAnswers[q.id]?.length > 0);

  // Interface de démarrage
  if (!quizStarted) {
    return (
      <div className="quiz-interface">
        <div className="quiz-start">
          <div className="quiz-start__icon" aria-hidden="true">📝</div>
          <h2 className="quiz-start__title">Prêt à commencer le quiz ?</h2>

          {quiz.instructions && (
            <div className="quiz-start__instructions">
              <p>{quiz.instructions}</p>
            </div>
          )}

          <div className="quiz-start__meta">
            <div className="quiz-start__meta-item">
              <strong>{totalQuestions}</strong> questions
            </div>
            <div className="quiz-start__meta-item">
              Score minimum : <strong>{quiz.passing_score}%</strong>
            </div>
            {quiz.time_limit > 0 && (
              <div className="quiz-start__meta-item">
                Temps limite : <strong>{quiz.time_limit} min</strong>
              </div>
            )}
            {quiz.max_attempts > 0 && (
              <div className="quiz-start__meta-item">
                Tentatives : <strong>{attemptsSoFar}/{quiz.max_attempts}</strong>
              </div>
            )}
          </div>

          {alreadyPassed && (
            <p className="quiz-start__note">
              ✅ Vous avez déjà réussi ce quiz{initialProgress?.score != null ? ` (${initialProgress.score}%)` : ''}.
              Vous pouvez le repasser pour vous entraîner, sans perdre vos points déjà acquis.
            </p>
          )}

          {attemptsExhausted ? (
            <p className="quiz-start__error" role="alert">
              Vous avez atteint le nombre maximum de tentatives ({quiz.max_attempts}) pour ce quiz.
            </p>
          ) : (
            <button className="quiz-start__button" onClick={handleStartQuiz}>
              {Object.keys(userAnswers).length > 0 ? 'Reprendre le quiz' : 'Commencer le quiz'}
            </button>
          )}
        </div>
      </div>
    );
  }

  // Interface de résultats
  if (showResults && submitResult) {
    const { passed, score, details } = submitResult;
    const detailsByQuestionId = new Map(details.map((d) => [String(d.question_id), d]));

    return (
      <div className="quiz-interface">
        <div className={`quiz-results ${passed ? 'quiz-results--passed' : 'quiz-results--failed'}`}>
          <div className="quiz-results__icon" aria-hidden="true">
            {passed ? '🎉' : '📚'}
          </div>

          <h2 className="quiz-results__title">
            {passed ? 'Félicitations !' : 'Continuez vos efforts !'}
          </h2>

          <div className="quiz-results__score">
            <div className="quiz-results__score-circle">
              <span className="quiz-results__score-value">{score}%</span>
            </div>
          </div>

          <p className="quiz-results__message" role="status">
            {passed
              ? `Excellent travail ! Vous avez réussi le quiz avec ${score}% de bonnes réponses.` +
                (submitResult.points_earned > 0
                  ? ` +${submitResult.points_earned} points !`
                  : '')
              : `Vous avez obtenu ${score}%. Le score minimum requis est de ${quiz.passing_score}%. Révisez le contenu de la leçon et réessayez !`}
          </p>

          <div className="quiz-results__details">
            <h3 className="quiz-results__details-title">Récapitulatif</h3>

            {questions.map((question, index) => {
              const detail = detailsByQuestionId.get(String(question.id));
              if (!detail) return null;

              const isCorrect = detail.is_correct;
              const correctAnswer = Array.isArray(detail.correct_answer)
                ? detail.correct_answer
                : [detail.correct_answer];

              return (
                <div
                  key={question.id}
                  className={`quiz-results__question ${
                    isCorrect ? 'quiz-results__question--correct' : 'quiz-results__question--incorrect'
                  }`}
                >
                  <div className="quiz-results__question-header">
                    <span className="quiz-results__question-icon" aria-hidden="true">
                      {isCorrect ? '✓' : '✗'}
                    </span>
                    <span className="quiz-results__question-number">
                      Question {index + 1}
                    </span>
                  </div>

                  <p className="quiz-results__question-text">{question.question}</p>

                  <div className="quiz-results__question-answer">
                    <strong>Votre réponse :</strong>{' '}
                    {detail.user_answer.length > 0
                      ? detail.user_answer.map((idx) => question.options[idx]).join(', ')
                      : 'Non répondu'}
                  </div>

                  {!isCorrect && (
                    <div className="quiz-results__question-correct">
                      <strong>Réponse correcte :</strong>{' '}
                      {correctAnswer.map((idx) => question.options[idx]).join(', ')}
                    </div>
                  )}

                  {detail.explanation && (
                    <div className="quiz-results__question-explanation">
                      <strong>💡 Explication :</strong> {detail.explanation}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {!attemptsExhausted && (
            <button className="quiz-results__retry-button" onClick={handleRetry}>
              Réessayer le quiz
            </button>
          )}
        </div>
      </div>
    );
  }

  // Interface de quiz en cours
  return (
    <div className="quiz-interface">
      <div className="quiz-header">
        <div className="quiz-progress">
          <div className="quiz-progress__text">
            Question {currentQuestionIndex + 1} / {totalQuestions}
          </div>
          <div className="quiz-progress__bar">
            <div
              className="quiz-progress__fill"
              style={{ width: `${((currentQuestionIndex + 1) / totalQuestions) * 100}%` }}
            />
          </div>
        </div>

        {quiz.time_limit > 0 && (
          <div className={`quiz-timer ${timeRemaining < 60 ? 'quiz-timer--warning' : ''}`}>
            ⏱️ {formatTime(timeRemaining)}
          </div>
        )}
      </div>

      <div className="quiz-question">
        <h3 className="quiz-question__text">{currentQuestion.question}</h3>

        <div className="quiz-options">
          {currentOptionOrder.map((originalIndex) => {
            const option = currentQuestion.options[originalIndex];
            const isSelected = (userAnswers[currentQuestion.id] || []).includes(originalIndex);
            const inputType = currentQuestion.type === 'multiple' ? 'checkbox' : 'radio';

            return (
              <label
                key={originalIndex}
                className={`quiz-option ${isSelected ? 'quiz-option--selected' : ''}`}
              >
                <input
                  type={inputType}
                  name={`question-${currentQuestion.id}`}
                  checked={isSelected}
                  onChange={() => handleSelectAnswer(currentQuestion.id, originalIndex)}
                />
                <span className="quiz-option__text">{option}</span>
              </label>
            );
          })}
        </div>

        {currentQuestion.type === 'multiple' && (
          <p className="quiz-question__hint">
            💡 Cette question accepte plusieurs réponses
          </p>
        )}
      </div>

      {submitError && (
        <p className="quiz-submit-error" role="alert">{submitError}</p>
      )}

      <div className="quiz-navigation">
        <button
          className="quiz-navigation__button quiz-navigation__button--prev"
          onClick={handlePreviousQuestion}
          disabled={currentQuestionIndex === 0}
        >
          ← Précédent
        </button>

        <div className="quiz-navigation__dots">
          {questions.map((q, index) => {
            const isAnswered = userAnswers[q.id]?.length > 0;
            const isCurrent = index === currentQuestionIndex;

            return (
              <button
                key={q.id}
                className={`quiz-navigation__dot ${
                  isCurrent ? 'quiz-navigation__dot--current' : ''
                } ${isAnswered ? 'quiz-navigation__dot--answered' : ''}`}
                onClick={() => handleGoToQuestion(index)}
                title={`Question ${index + 1}`}
              >
                {index + 1}
              </button>
            );
          })}
        </div>

        {currentQuestionIndex < totalQuestions - 1 ? (
          <button
            className="quiz-navigation__button quiz-navigation__button--next"
            onClick={handleNextQuestion}
          >
            Suivant →
          </button>
        ) : (
          <button
            className="quiz-navigation__button quiz-navigation__button--submit"
            onClick={handleSubmitQuiz}
            disabled={!allQuestionsAnswered || isSubmitting}
            aria-busy={isSubmitting}
          >
            {isSubmitting
              ? 'Envoi en cours...'
              : allQuestionsAnswered
                ? 'Terminer le quiz'
                : 'Répondre à toutes les questions'}
          </button>
        )}
      </div>
    </div>
  );
}
