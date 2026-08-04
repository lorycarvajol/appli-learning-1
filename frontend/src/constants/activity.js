/**
 * Types d'activité — miroir de `ActivityLog.ActivityType` côté Django
 * (`apps/progression/models.py`).
 *
 * Ce tableau était recopié dans trois écrans, et les trois avaient divergé :
 *
 * - `ProgressionPage` ignorait `LESSON_STARTED` et affichait donc la clé brute
 *   « LESSON_STARTED » derrière une puce, sans icône ;
 * - `LearnerDetail` et `RecentActivity` fabriquaient leur libellé avec
 *   `activity_type.replace('_', ' ').toLowerCase()`, ce qui donnait « lesson
 *   started » — de l'anglais, en minuscules, dans une interface française.
 *
 * `LESSON_STARTED` est le type le plus fréquent depuis que l'ouverture d'une
 * leçon journalise une activité : c'est celui qu'il était le plus coûteux
 * d'oublier.
 *
 * ⚠️ Ajouter une valeur à `ActivityType` côté Django impose d'ajouter une
 * entrée ici. Un test vérifie que la liste est complète et que chaque entrée
 * a une icône et un libellé.
 */

export const ACTIVITY_TYPES = {
  LESSON_STARTED: 'LESSON_STARTED',
  LESSON_COMPLETED: 'LESSON_COMPLETED',
  EXERCISE_SUBMITTED: 'EXERCISE_SUBMITTED',
  QUIZ_COMPLETED: 'QUIZ_COMPLETED',
  CHAPTER_UNLOCKED: 'CHAPTER_UNLOCKED',
  BADGE_EARNED: 'BADGE_EARNED',
};

/**
 * Icône et libellé de chaque type.
 *
 * `label` reçoit l'activité sérialisée (`lesson_title`, `chapter_title`…) et
 * rend une phrase complète. Les replis (« leçon », « chapitre ») couvrent le
 * cas d'un contenu supprimé depuis : le serializer renvoie alors `null`.
 */
export const ACTIVITY_META = {
  [ACTIVITY_TYPES.LESSON_STARTED]: {
    icon: '▶️',
    color: 'bg-blue-50 border-blue-200',
    label: (a) => `Leçon commencée — ${a.lesson_title || 'leçon'}`,
  },
  [ACTIVITY_TYPES.LESSON_COMPLETED]: {
    icon: '✅',
    color: 'bg-green-50 border-green-200',
    label: (a) => `Leçon terminée — ${a.lesson_title || 'leçon'}`,
  },
  [ACTIVITY_TYPES.EXERCISE_SUBMITTED]: {
    icon: '💻',
    color: 'bg-purple-50 border-purple-200',
    label: (a) => `Exercice soumis — ${a.lesson_title || 'exercice'}`,
  },
  [ACTIVITY_TYPES.QUIZ_COMPLETED]: {
    icon: '📝',
    color: 'bg-yellow-50 border-yellow-200',
    label: (a) => `Quiz terminé — ${a.lesson_title || 'quiz'}`,
  },
  [ACTIVITY_TYPES.CHAPTER_UNLOCKED]: {
    icon: '🔓',
    color: 'bg-indigo-50 border-indigo-200',
    label: (a) => `Chapitre débloqué — ${a.chapter_title || 'chapitre'}`,
  },
  [ACTIVITY_TYPES.BADGE_EARNED]: {
    icon: '🏆',
    color: 'bg-pink-50 border-pink-200',
    label: () => 'Nouveau badge débloqué',
  },
};

/** Repli pour un type inconnu — un backend plus récent que ce fichier. */
const FALLBACK = {
  icon: '📌',
  color: 'bg-gray-50 border-gray-200',
  label: () => 'Activité',
};

/**
 * Décrit une activité, sans jamais laisser fuiter une clé technique.
 *
 * C'était tout l'enjeu du repli précédent : il affichait `activity_type` tel
 * quel, donc du jargon de base de données dans l'interface. Mieux vaut un
 * libellé vague mais lisible.
 */
export function describeActivity(activity) {
  const meta = ACTIVITY_META[activity?.activity_type] ?? FALLBACK;
  return { icon: meta.icon, color: meta.color, label: meta.label(activity ?? {}) };
}
