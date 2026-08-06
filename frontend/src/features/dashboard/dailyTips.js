/**
 * Conseil du jour — choisi d'après le comportement réel de l'apprenant.
 *
 * Le bloc affichait une seule phrase, écrite en dur, identique pour tout le
 * monde et tous les jours (« Pratiquez régulièrement ! »). Un conseil qui ne
 * regarde ni ce que vous avez fait ni où vous en êtes n'est pas un conseil,
 * c'est une décoration : on cesse de le lire au deuxième jour.
 *
 * Le moteur est volontairement un **module pur** : il prend un contexte, rend
 * un conseil. Aucun appel réseau, aucun accès au store, aucune dépendance à
 * React — tout est déjà chargé par le tableau de bord, et le tout se teste
 * sans monter un composant.
 *
 * ## Comment un conseil est choisi
 *
 * Chaque règle déclare une `priorite` et une condition. La règle applicable la
 * plus prioritaire gagne. **À priorité égale, on tourne selon le jour** — deux
 * conseils également pertinents alternent au lieu qu'un seul l'emporte pour
 * toujours par ordre de déclaration.
 *
 * La rotation est *déterministe* : même jour, même contexte, même conseil. Un
 * tirage au sort changerait le texte à chaque rendu de React, ce qui donnerait
 * l'impression que la page clignote.
 *
 * ⚠️ **`streak.active_today` ne dit rien d'utile ici.** Le tableau de bord
 * appelle `syncGamification()` à son montage, qui appelle `touch_streak` :
 * ouvrir la page suffit à rendre le drapeau vrai. Les règles s'appuient donc
 * sur la longueur de la série et sur le record, jamais sur « a été actif
 * aujourd'hui ».
 */

/** Numéro du jour, en jours pleins depuis l'époque. */
export function todayIndex(now = Date.now()) {
  return Math.floor(now / 86_400_000)
}

/**
 * Rassemble en un objet plat ce que les règles ont le droit de regarder.
 *
 * Passer les charges utiles brutes aux règles les rendrait dépendantes de la
 * forme exacte de trois API ; ce point de passage unique est aussi ce qui rend
 * les tests lisibles.
 */
export function buildTipContext({ summary, overview, nextLesson } = {}) {
  const lessons = overview?.lessons
  const counters = summary?.counters
  const chapters = overview?.chapters || []

  return {
    total: lessons?.total ?? 0,
    completed: lessons?.completed ?? 0,
    inProgress: lessons?.in_progress ?? 0,
    percent: lessons?.percent ?? 0,

    averageScore: overview?.average_score ?? null,
    gradedCount: overview?.graded_count ?? 0,
    minutesSpent: Math.round((overview?.time_spent_seconds ?? 0) / 60),

    streak: summary?.streak?.current_streak ?? 0,
    longestStreak: summary?.streak?.longest_streak ?? 0,

    exercisesPassed: counters?.exercises_passed ?? 0,
    quizzesPassed: counters?.quizzes_passed ?? 0,
    perfectQuizzes: counters?.perfect_quizzes ?? 0,

    secretsLeft: Math.max(
      0,
      (summary?.badges?.secret_total ?? 0) - (summary?.badges?.secret_found ?? 0)
    ),
    nextObjective: summary?.next_objectives?.[0] ?? null,

    // Chapitre ouvert le plus avancé sans être fini : c'est celui qu'il est le
    // moins coûteux de terminer.
    chapterAlmostDone: chapters
      .filter((c) => c.is_accessible && c.percent >= 60 && c.percent < 100)
      .sort((a, b) => b.percent - a.percent)[0] ?? null,

    allCompleted: Boolean(nextLesson?.all_completed),
    isResuming: Boolean(nextLesson?.is_resuming),
    nextLessonTitle: nextLesson?.lesson?.title ?? null,
    nextLessonType: nextLesson?.lesson?.lesson_type ?? null,
  }
}

/**
 * Règles, de la plus spécifique à la plus générale.
 *
 * Un conseil ne se contente pas d'encourager : il dit **quoi faire ensuite**,
 * avec les chiffres de la personne à qui il s'adresse. « Bravo, continuez »
 * n'aide personne.
 */
export const TIP_RULES = [
  {
    id: 'parcours-termine',
    priorite: 100,
    quand: (c) => c.allCompleted,
    texte: (c) =>
      c.secretsLeft > 0
        ? `Tout le programme est bouclé. Il reste ${c.secretsLeft} objectif(s) `
          + `caché(s) : personne ne vous dira comment les décrocher.`
        : 'Tout le programme est bouclé, objectifs cachés compris. Chapeau.',
    lien: { to: '/badges', label: 'Voir mes trophées' },
  },
  {
    id: 'premier-pas',
    priorite: 90,
    quand: (c) => c.completed === 0 && c.total > 0,
    texte: (c) =>
      c.nextLessonTitle
        ? `Rien n'est encore commencé — et « ${c.nextLessonTitle} » ne demande `
          + `qu'à être lue. La première leçon est la seule qui coûte.`
        : "Rien n'est encore commencé. La première leçon est la seule qui coûte.",
    lien: { to: '/chapters', label: 'Ouvrir le programme' },
  },
  {
    id: 'trop-de-lecons-ouvertes',
    priorite: 80,
    quand: (c) => c.inProgress >= 3,
    texte: (c) =>
      `${c.inProgress} leçons sont ouvertes en même temps. En terminer une `
      + `avant d'en ouvrir une autre vous coûtera moins d'efforts — et fera `
      + `enfin bouger votre progression.`,
    lien: { to: '/progression', label: 'Voir ce qui est en cours' },
  },
  {
    id: 'scores-en-baisse',
    priorite: 70,
    quand: (c) => c.gradedCount >= 2 && c.averageScore !== null && c.averageScore < 60,
    texte: (c) =>
      `Votre moyenne est de ${c.averageScore} % sur ${c.gradedCount} `
      + `évaluation(s). Repasser un quiz ne vous fait rien perdre : les points `
      + `déjà gagnés vous restent, seule la compréhension change.`,
    lien: { to: '/progression', label: 'Revoir mes résultats' },
  },
  {
    id: 'chapitre-a-portee',
    priorite: 65,
    quand: (c) => Boolean(c.chapterAlmostDone),
    texte: (c) => {
      const chapitre = c.chapterAlmostDone
      const reste = chapitre.total - chapitre.completed
      return `Plus que ${reste} leçon(s) pour terminer « ${chapitre.title} » `
        + `(${chapitre.percent} % de fait). C'est le chapitre le moins cher à `
        + `boucler aujourd'hui.`
    },
    lien: (c) => ({
      to: `/chapters/${c.chapterAlmostDone.slug}`,
      label: 'Reprendre ce chapitre',
    }),
  },
  {
    id: 'objectif-a-portee',
    priorite: 60,
    // Chaînage optionnel de bout en bout : une règle doit rester vraie ou
    // fausse sur un contexte incomplet, jamais lever. `pickTip` rattrape
    // l'exception, mais une règle qui trébuche est une règle qui ne s'applique
    // plus — un silence bien plus difficile à voir qu'une erreur.
    quand: (c) => (c.nextObjective?.progress?.percent ?? 0) >= 70,
    texte: (c) => {
      const objectif = c.nextObjective
      const reste = objectif.progress.target - objectif.progress.current
      return `« ${objectif.name} » est à ${objectif.progress.percent} % : encore `
        + `${reste} et il est à vous.`
    },
    lien: { to: '/badges', label: 'Voir mes objectifs' },
  },
  {
    id: 'quiz-sans-exercice',
    priorite: 55,
    quand: (c) => c.perfectQuizzes >= 2 && c.exercisesPassed === 0,
    texte: (c) =>
      `${c.perfectQuizzes} quiz sans faute : la théorie est acquise. Les `
      + `exercices, eux, ne se réussissent qu'en écrivant du code — c'est là `
      + `que le reste s'apprend.`,
    lien: { to: '/chapters', label: 'Trouver un exercice' },
  },
  {
    id: 'serie-lancee',
    priorite: 50,
    quand: (c) => c.streak === 1 && c.completed > 0,
    texte: () =>
      'Votre série de jours vient de démarrer. Elle ne tient qu\'à une chose : '
      + 'revenir demain, même dix minutes.',
  },
  {
    id: 'record-a-battre',
    priorite: 48,
    quand: (c) => c.longestStreak >= 3 && c.longestStreak > c.streak + 1,
    texte: (c) =>
      `Votre record est de ${c.longestStreak} jours d'affilée ; vous en êtes à `
      + `${c.streak}. Il n'y a rien à rattraper, seulement à recommencer.`,
  },
  {
    id: 'belle-serie',
    priorite: 45,
    quand: (c) => c.streak >= 5,
    texte: (c) =>
      `${c.streak} jours d'affilée. C'est la régularité, bien plus que la durée `
      + `des sessions, qui fait la différence à l'arrivée.`,
  },
  {
    id: 'reprendre-plutot-que-choisir',
    priorite: 40,
    quand: (c) => c.isResuming && c.nextLessonTitle,
    texte: (c) =>
      `« ${c.nextLessonTitle} » est restée en plan. La reprendre demande moins `
      + `d'élan que de choisir par quoi commencer.`,
  },
  {
    id: 'temps-court',
    priorite: 35,
    quand: (c) => c.completed >= 1 && c.minutesSpent < 20,
    texte: () =>
      'Quinze minutes par jour valent mieux que deux heures le dimanche : on '
      + 'oublie beaucoup moins entre deux séances.',
  },

  // Filet : toujours applicables, donc toujours en dernier recours. Ils sont
  // plusieurs pour que le bloc change quand même de jour en jour.
  {
    id: 'general-relire-son-code',
    priorite: 0,
    quand: () => true,
    texte: () =>
      'Relisez à voix haute le code que vous venez d\'écrire. Ce qu\'on ne sait '
      + 'pas expliquer, on ne l\'a pas encore compris.',
  },
  {
    id: 'general-casser-pour-comprendre',
    priorite: 0,
    quand: () => true,
    texte: () =>
      'Cassez volontairement un exemple qui marche, puis réparez-le. On '
      + 'apprend davantage d\'une erreur provoquée que d\'un exemple qui '
      + 'fonctionne du premier coup.',
  },
  {
    id: 'general-taper-plutot-que-copier',
    priorite: 0,
    quand: () => true,
    texte: () =>
      'Retapez les exemples au lieu de les copier. La main retient ce que '
      + 'l\'œil laisse filer.',
  },
  {
    id: 'general-pause',
    priorite: 0,
    quand: () => true,
    texte: () =>
      'Bloqué depuis vingt minutes ? Faites autre chose. La solution arrive '
      + 'presque toujours pendant la pause, jamais pendant l\'acharnement.',
  },
]

/**
 * Rend le conseil du jour : `{ id, texte, lien }`.
 *
 * @param {object} context   sortie de `buildTipContext`
 * @param {number} [jour]    numéro du jour, injectable pour les tests
 */
export function pickTip(context, jour = todayIndex()) {
  const applicables = TIP_RULES.filter((regle) => {
    try {
      return regle.quand(context)
    } catch {
      // Une règle qui trébuche sur un contexte partiel ne doit pas priver
      // l'apprenant de son conseil : elle s'efface, les autres restent.
      return false
    }
  })

  if (applicables.length === 0) return null

  const priorite = Math.max(...applicables.map((regle) => regle.priorite))
  const candidats = applicables.filter((regle) => regle.priorite === priorite)
  const choisie = candidats[Math.abs(jour) % candidats.length]

  const lien = typeof choisie.lien === 'function' ? choisie.lien(context) : choisie.lien

  return { id: choisie.id, texte: choisie.texte(context), lien: lien ?? null }
}
