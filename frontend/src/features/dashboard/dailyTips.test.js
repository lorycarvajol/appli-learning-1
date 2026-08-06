import { describe, it, expect } from 'vitest'
import { TIP_RULES, buildTipContext, pickTip, todayIndex } from './dailyTips'

/**
 * Ce qui est verrouillé ici :
 *
 * 1. Le conseil **répond au comportement** — c'est toute la raison d'être du
 *    module, qui remplace une phrase écrite en dur.
 * 2. Il est **stable dans la journée** (pas de tirage au sort qui changerait
 *    le texte à chaque rendu de React) et **tourne d'un jour à l'autre** entre
 *    conseils également pertinents.
 * 3. Il ne casse jamais : un contexte vide ou partiel rend quand même un
 *    conseil, plutôt qu'une page en erreur.
 */

const VIDE = buildTipContext({})

describe('buildTipContext', () => {
  it('accepte des charges utiles absentes sans lever', () => {
    expect(VIDE.total).toBe(0)
    expect(VIDE.averageScore).toBeNull()
    expect(VIDE.chapterAlmostDone).toBeNull()
  })

  it('retient le chapitre ouvert le plus avancé qui ne soit pas fini', () => {
    const context = buildTipContext({
      overview: {
        lessons: { total: 20, completed: 10, in_progress: 0, percent: 50 },
        chapters: [
          { slug: 'html', title: 'HTML', percent: 100, completed: 5, total: 5, is_accessible: true },
          { slug: 'css', title: 'CSS', percent: 80, completed: 4, total: 5, is_accessible: true },
          { slug: 'js', title: 'JS', percent: 70, completed: 7, total: 10, is_accessible: true },
          // Verrouillé : le proposer enverrait vers une leçon qui répond 403.
          { slug: 'vitrine', title: 'Vitrine', percent: 90, completed: 9, total: 10, is_accessible: false },
        ],
      },
    })

    expect(context.chapterAlmostDone.slug).toBe('css')
  })
})

describe('pickTip — le conseil suit le comportement', () => {
  it('parle de la première leçon à qui n’a rien terminé', () => {
    const context = buildTipContext({
      overview: { lessons: { total: 30, completed: 0, in_progress: 0, percent: 0 } },
      nextLesson: { lesson: { title: 'Les balises' }, is_resuming: false },
    })

    const tip = pickTip(context, 0)
    expect(tip.id).toBe('premier-pas')
    expect(tip.texte).toContain('Les balises')
  })

  it('signale les leçons laissées ouvertes plutôt que d’encourager dans le vide', () => {
    const tip = pickTip(buildTipContext({
      overview: { lessons: { total: 30, completed: 4, in_progress: 3, percent: 13 } },
    }), 0)

    expect(tip.id).toBe('trop-de-lecons-ouvertes')
    expect(tip.texte).toContain('3 leçons')
  })

  it('ne fait pas la morale sur des scores faibles sans les rendre réparables', () => {
    const tip = pickTip(buildTipContext({
      overview: {
        lessons: { total: 30, completed: 5, in_progress: 0, percent: 17 },
        average_score: 45,
        graded_count: 3,
      },
    }), 0)

    expect(tip.id).toBe('scores-en-baisse')
    // Le point essentiel : repasser un quiz ne retire aucun point déjà acquis.
    expect(tip.texte).toMatch(/rien perdre|vous restent/i)
  })

  it('ne déclenche pas l’alerte de score sur une seule évaluation ratée', () => {
    const tip = pickTip(buildTipContext({
      overview: {
        lessons: { total: 30, completed: 5, in_progress: 0, percent: 17 },
        average_score: 40,
        graded_count: 1,
      },
    }), 0)

    expect(tip.id).not.toBe('scores-en-baisse')
  })

  it('pointe le chapitre le moins cher à terminer, et jamais un verrouillé', () => {
    const tip = pickTip(buildTipContext({
      overview: {
        lessons: { total: 20, completed: 12, in_progress: 0, percent: 60 },
        chapters: [
          { slug: 'css', title: 'CSS', percent: 80, completed: 4, total: 5, is_accessible: true },
          { slug: 'js', title: 'JS', percent: 95, completed: 19, total: 20, is_accessible: false },
        ],
      },
    }), 0)

    expect(tip.id).toBe('chapitre-a-portee')
    expect(tip.texte).toContain('CSS')
    expect(tip.lien).toEqual({ to: '/chapters/css', label: 'Reprendre ce chapitre' })
  })

  it('renvoie vers les objectifs cachés quand tout est terminé', () => {
    const tip = pickTip(buildTipContext({
      overview: { lessons: { total: 30, completed: 30, in_progress: 0, percent: 100 } },
      summary: { badges: { secret_total: 8, secret_found: 5 } },
      nextLesson: { all_completed: true },
    }), 0)

    expect(tip.id).toBe('parcours-termine')
    expect(tip.texte).toContain('3 objectif(s) caché(s)')
    expect(tip.lien.to).toBe('/badges')
  })

  it('propose un exercice à qui ne réussit que des quiz', () => {
    const tip = pickTip(buildTipContext({
      overview: { lessons: { total: 30, completed: 8, in_progress: 0, percent: 27 } },
      summary: {
        counters: { perfect_quizzes: 3, exercises_passed: 0, quizzes_passed: 3 },
        streak: { current_streak: 2, longest_streak: 2 },
      },
    }), 0)

    expect(tip.id).toBe('quiz-sans-exercice')
  })

  it('l’urgence prime sur l’encouragement', () => {
    // Belle série *et* trois leçons ouvertes : c'est la dispersion qu'il faut
    // dire, pas la régularité qu'il faut féliciter.
    const tip = pickTip(buildTipContext({
      overview: { lessons: { total: 30, completed: 9, in_progress: 3, percent: 30 } },
      summary: { streak: { current_streak: 9, longest_streak: 9 } },
    }), 0)

    expect(tip.id).toBe('trop-de-lecons-ouvertes')
  })
})

describe('pickTip — stabilité et rotation', () => {
  it('rend toujours le même conseil pour un même jour', () => {
    const context = buildTipContext({})
    const rendus = Array.from({ length: 5 }, () => pickTip(context, 4242).id)

    expect(new Set(rendus).size).toBe(1)
  })

  it('fait tourner les conseils généraux d’un jour à l’autre', () => {
    const context = buildTipContext({})
    const generaux = TIP_RULES.filter((r) => r.priorite === 0)
    const surUneSemaine = new Set(
      Array.from({ length: generaux.length }, (_, jour) => pickTip(context, jour).id)
    )

    // Aucun conseil général ne doit être inatteignable.
    expect(surUneSemaine.size).toBe(generaux.length)
  })

  it('rend un conseil même sans aucune donnée', () => {
    expect(pickTip(VIDE)).not.toBeNull()
    expect(pickTip(buildTipContext({}), todayIndex()).texte.length).toBeGreaterThan(20)
  })

  it('écarte une règle qui trébuche sans priver l’apprenant de conseil', () => {
    // Contexte volontairement malformé : `next_objectives[0]` sans `progress`.
    const context = buildTipContext({
      summary: { next_objectives: [{ name: 'Bancal' }] },
      overview: { lessons: { total: 10, completed: 1, in_progress: 0, percent: 10 } },
    })

    expect(() => pickTip(context, 0)).not.toThrow()
    expect(pickTip(context, 0).id).not.toBe('objectif-a-portee')
  })
})

describe('TIP_RULES — hygiène du catalogue', () => {
  it('n’a aucun identifiant en double', () => {
    const ids = TIP_RULES.map((rule) => rule.id)
    expect(new Set(ids).size).toBe(ids.length)
  })

  it('garde un filet de conseils toujours applicables', () => {
    const filet = TIP_RULES.filter((rule) => rule.quand(VIDE))
    expect(filet.length).toBeGreaterThanOrEqual(2)
  })

  it('aucune règle ne lève sur un contexte brut', () => {
    // `pickTip` rattrape, mais une règle qui trébuche est une règle qui ne
    // s'applique plus jamais — un silence, pas une erreur visible.
    for (const rule of TIP_RULES) {
      expect(() => rule.quand({}), `règle ${rule.id}`).not.toThrow()
    }
  })
})
