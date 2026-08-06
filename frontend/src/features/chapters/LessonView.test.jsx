import { describe, it, expect, vi } from 'vitest'
import { render, screen } from '@testing-library/react'
import { Provider } from 'react-redux'
import { configureStore } from '@reduxjs/toolkit'
import { MemoryRouter, Route, Routes } from 'react-router-dom'

import LessonView from './LessonView'

/**
 * Le bouton « Marquer comme terminé » demandait à l'apprenant de déclarer une
 * progression que l'application peut constater. Il a été retiré au profit
 * d'une validation automatique en bas de page (`useScrollCompletion`).
 *
 * Ce que ces tests protègent, c'est la **frontière** de cette automatisation.
 * `useScrollCompletion` a ses propres tests ; ici on vérifie qu'il est branché
 * sur la théorie et sur rien d'autre — la question qui a des conséquences.
 * Un exercice validé au défilement distribuerait ses points sans le travail.
 *
 * Le repère de fin est cherché par sa classe : c'est un élément `aria-hidden`
 * sans rôle ni texte, donc invisible aux requêtes accessibles, et lui donner un
 * libellé pour les besoins du test le ferait annoncer par les lecteurs d'écran.
 */

vi.mock('@/features/quizzes/QuizInterface', () => ({
  default: () => <div>interface de quiz</div>,
}))
vi.mock('@/features/exercises/ExerciseInterface', () => ({
  default: () => <div>interface d’exercice</div>,
}))
vi.mock('../progression/useTimeTracker', () => ({ default: () => {} }))

const LESSONS = {
  theorie: {
    id: 'l-theorie',
    slug: 'une-lecon-de-theorie',
    title: 'Une leçon de théorie',
    lesson_type: 'THEORY',
    chapter_slug: 'chap',
    content: '# Titre\n\nDu contenu.',
    estimated_duration: 10,
    points: 10,
  },
  exercice: {
    id: 'l-exercice',
    slug: 'un-exercice',
    title: 'Un exercice',
    lesson_type: 'EXERCISE',
    chapter_slug: 'chap',
    content: '',
    estimated_duration: 20,
    points: 50,
    exercise: { id: 'e1', instructions: '', starter_code: '', tests: [] },
  },
  quiz: {
    id: 'l-quiz',
    slug: 'un-quiz',
    title: 'Un quiz',
    lesson_type: 'QUIZ',
    chapter_slug: 'chap',
    content: '',
    estimated_duration: 15,
    points: 30,
    quiz: { id: 'q1', questions: [], instructions: '' },
  },
}

function renderLesson(lesson, { status = 'NOT_STARTED' } = {}) {
  const store = configureStore({
    reducer: {
      chapters: (state = {
        currentLesson: lesson,
        currentChapter: null,
        loading: false,
        error: null,
      }) => state,
      progression: (state = {
        progressByLesson:
          status === 'NOT_STARTED' ? {} : { [lesson.id]: { status } },
        nextLesson: null,
        markingCompleted: false,
        loading: false,
        error: null,
      }) => state,
    },
  })

  const view = render(
    <Provider store={store}>
      <MemoryRouter initialEntries={[`/lessons/${lesson.slug}`]}>
        <Routes>
          <Route path="/lessons/:slug" element={<LessonView />} />
        </Routes>
      </MemoryRouter>
    </Provider>
  )
  return { ...view, store }
}

const sentinelle = (container) => container.querySelector('.lesson-content__end')

describe('LessonView — validation de la leçon', () => {
  it('n’offre plus de bouton « Marquer comme terminé »', () => {
    renderLesson(LESSONS.theorie)
    expect(screen.queryByRole('button', { name: /marquer comme terminé/i })).toBeNull()
  })

  it('pose le repère de fin de lecture sur une leçon de théorie', () => {
    const { container } = renderLesson(LESSONS.theorie)
    expect(sentinelle(container)).not.toBeNull()
    expect(screen.getByRole('status', { name: /statut de la leçon/i })).toHaveTextContent(/faites défiler/i)
  })

  it('ne pose aucun repère sur un exercice', () => {
    // Sinon, faire défiler la page suffirait à empocher les points sans
    // écrire une ligne de code.
    const { container } = renderLesson(LESSONS.exercice)
    expect(sentinelle(container)).toBeNull()
    expect(screen.getByRole('status', { name: /statut de la leçon/i })).toHaveTextContent(/tests passent/i)
  })

  it('ne pose aucun repère sur un quiz', () => {
    const { container } = renderLesson(LESSONS.quiz)
    expect(sentinelle(container)).toBeNull()
    expect(screen.getByRole('status', { name: /statut de la leçon/i })).toHaveTextContent(/score requis/i)
  })

  it('annonce une leçon déjà terminée sans proposer de la revalider', () => {
    renderLesson(LESSONS.theorie, { status: 'COMPLETED' })
    expect(screen.getByRole('status', { name: /statut de la leçon/i })).toHaveTextContent(/leçon terminée/i)
    expect(screen.queryByRole('button', { name: /terminé/i })).toBeNull()
  })
})
