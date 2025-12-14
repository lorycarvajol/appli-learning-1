import { useState, useEffect, useCallback } from 'react';
import './QuizInterface.css';

/**
 * QuizInterface - Interface interactive pour les quiz
 *
 * @param {object} quiz - Objet quiz avec questions, passing_score, time_limit, etc.
 * @param {function} onSubmit - Callback appelé lors de la soumission du quiz
 */
export default function QuizInterface({ quiz, onSubmit }) {
  const [quizStarted, setQuizStarted] = useState(false);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [quizCompleted, setQuizCompleted] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(null);
  const [showResults, setShowResults] = useState(false);
  const [score, setScore] = useState(null);

  // Extraire les questions depuis le JSONB
  const questions = Array.isArray(quiz.questions) ? quiz.questions : [];
  const totalQuestions = questions.length;
  const currentQuestion = questions[currentQuestionIndex];

  // Si pas de questions, afficher un message
  if (totalQuestions === 0) {
    return (
      <div className="quiz-interface">
        <div className="quiz-start">
          <p>Aucune question n'est disponible pour ce quiz.</p>
        </div>
      </div>
    );
  }

  // Timer countdown
  useEffect(() => {
    if (quizStarted && quiz.time_limit > 0 && timeRemaining > 0 && !quizCompleted) {
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
  }, [quizStarted, timeRemaining, quizCompleted]);

  // Démarrer le quiz
  const handleStartQuiz = () => {
    setQuizStarted(true);
    if (quiz.time_limit > 0) {
      setTimeRemaining(quiz.time_limit * 60); // Convertir minutes en secondes
    }
  };

  // Sélectionner une réponse
  const handleSelectAnswer = (questionId, optionIndex) => {
    const question = questions.find((q) => q.id === questionId);

    if (question.type === 'multiple') {
      // Pour les questions à choix multiples
      const currentAnswers = userAnswers[questionId] || [];
      const newAnswers = currentAnswers.includes(optionIndex)
        ? currentAnswers.filter((idx) => idx !== optionIndex)
        : [...currentAnswers, optionIndex];

      setUserAnswers({
        ...userAnswers,
        [questionId]: newAnswers,
      });
    } else {
      // Pour les questions à choix unique
      setUserAnswers({
        ...userAnswers,
        [questionId]: [optionIndex],
      });
    }
  };

  // Navigation entre les questions
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

  // Calculer le score
  const calculateScore = useCallback(() => {
    let correctAnswers = 0;

    questions.forEach((question) => {
      const userAnswer = userAnswers[question.id] || [];
      const correctAnswer = question.correct_answer;

      // Vérifier si la réponse est correcte
      if (Array.isArray(correctAnswer)) {
        // Question à choix multiples
        const isCorrect =
          userAnswer.length === correctAnswer.length &&
          userAnswer.every((ans) => correctAnswer.includes(ans));
        if (isCorrect) correctAnswers++;
      } else {
        // Question à choix unique
        if (userAnswer[0] === correctAnswer) correctAnswers++;
      }
    });

    return Math.round((correctAnswers / totalQuestions) * 100);
  }, [questions, userAnswers, totalQuestions]);

  // Soumettre le quiz
  const handleSubmitQuiz = useCallback(() => {
    const calculatedScore = calculateScore();
    setScore(calculatedScore);
    setQuizCompleted(true);
    setShowResults(true);

    if (onSubmit) {
      onSubmit({
        answers: userAnswers,
        score: calculatedScore,
        passed: calculatedScore >= quiz.passing_score,
        time_spent: quiz.time_limit > 0 ? (quiz.time_limit * 60 - timeRemaining) : null,
      });
    }
  }, [calculateScore, userAnswers, quiz, timeRemaining, onSubmit]);

  // Formater le temps restant
  const formatTime = (seconds) => {
    if (seconds === null) return '';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Vérifier si toutes les questions ont été répondues
  const allQuestionsAnswered = questions.every((q) => userAnswers[q.id]?.length > 0);

  // Interface de démarrage
  if (!quizStarted) {
    return (
      <div className="quiz-interface">
        <div className="quiz-start">
          <div className="quiz-start__icon">📝</div>
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
          </div>

          <button className="quiz-start__button" onClick={handleStartQuiz}>
            Commencer le quiz
          </button>
        </div>
      </div>
    );
  }

  // Interface de résultats
  if (showResults) {
    const passed = score >= quiz.passing_score;

    return (
      <div className="quiz-interface">
        <div className={`quiz-results ${passed ? 'quiz-results--passed' : 'quiz-results--failed'}`}>
          <div className="quiz-results__icon">
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

          <p className="quiz-results__message">
            {passed
              ? `Excellent travail ! Vous avez réussi le quiz avec ${score}% de bonnes réponses.`
              : `Vous avez obtenu ${score}%. Le score minimum requis est de ${quiz.passing_score}%. Révisez le contenu de la leçon et réessayez !`}
          </p>

          <div className="quiz-results__details">
            <h3 className="quiz-results__details-title">Récapitulatif</h3>

            {questions.map((question, index) => {
              const userAnswer = userAnswers[question.id] || [];
              const correctAnswer = Array.isArray(question.correct_answer)
                ? question.correct_answer
                : [question.correct_answer];

              const isCorrect = Array.isArray(question.correct_answer)
                ? userAnswer.length === correctAnswer.length &&
                  userAnswer.every((ans) => correctAnswer.includes(ans))
                : userAnswer[0] === question.correct_answer;

              return (
                <div
                  key={question.id}
                  className={`quiz-results__question ${
                    isCorrect ? 'quiz-results__question--correct' : 'quiz-results__question--incorrect'
                  }`}
                >
                  <div className="quiz-results__question-header">
                    <span className="quiz-results__question-icon">
                      {isCorrect ? '✓' : '✗'}
                    </span>
                    <span className="quiz-results__question-number">
                      Question {index + 1}
                    </span>
                  </div>

                  <p className="quiz-results__question-text">{question.question}</p>

                  <div className="quiz-results__question-answer">
                    <strong>Votre réponse :</strong>{' '}
                    {userAnswer.length > 0
                      ? userAnswer.map((idx) => question.options[idx]).join(', ')
                      : 'Non répondu'}
                  </div>

                  {!isCorrect && (
                    <div className="quiz-results__question-correct">
                      <strong>Réponse correcte :</strong>{' '}
                      {correctAnswer.map((idx) => question.options[idx]).join(', ')}
                    </div>
                  )}

                  {question.explanation && (
                    <div className="quiz-results__question-explanation">
                      <strong>💡 Explication :</strong> {question.explanation}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {!passed && (
            <button
              className="quiz-results__retry-button"
              onClick={() => {
                setQuizStarted(false);
                setCurrentQuestionIndex(0);
                setUserAnswers({});
                setQuizCompleted(false);
                setShowResults(false);
                setScore(null);
                setTimeRemaining(null);
              }}
            >
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
      {/* Header avec progression et timer */}
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

      {/* Question actuelle */}
      <div className="quiz-question">
        <h3 className="quiz-question__text">{currentQuestion.question}</h3>

        <div className="quiz-options">
          {currentQuestion.options.map((option, index) => {
            const isSelected = (userAnswers[currentQuestion.id] || []).includes(index);
            const inputType = currentQuestion.type === 'multiple' ? 'checkbox' : 'radio';

            return (
              <label
                key={index}
                className={`quiz-option ${isSelected ? 'quiz-option--selected' : ''}`}
              >
                <input
                  type={inputType}
                  name={`question-${currentQuestion.id}`}
                  checked={isSelected}
                  onChange={() => handleSelectAnswer(currentQuestion.id, index)}
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

      {/* Navigation des questions */}
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
            disabled={!allQuestionsAnswered}
          >
            {allQuestionsAnswered ? 'Terminer le quiz' : 'Répondre à toutes les questions'}
          </button>
        )}
      </div>
    </div>
  );
}
