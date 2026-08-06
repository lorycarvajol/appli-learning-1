import { describe, it, expect } from 'vitest'

import { ACTIVITY_META, ACTIVITY_TYPES, describeActivity } from './activity'

/**
 * L'écran de progression affichait « LESSON_STARTED » derrière une puce, sans
 * icône : le tableau de correspondance avait été écrit avant que l'ouverture
 * d'une leçon ne journalise une activité, et personne ne l'avait complété.
 * Deux autres écrans fabriquaient leur libellé avec
 * `activity_type.replace('_', ' ').toLowerCase()` — donc « lesson started »,
 * de l'anglais dans une interface française.
 *
 * Ces tests portent sur ce qui a réellement cassé : la **complétude** de la
 * table, et le fait qu'aucune clé technique ne puisse atteindre l'écran.
 */

// Miroir de `ActivityLog.ActivityType` (apps/progression/models.py). Toute
// valeur ajoutée côté Django doit apparaître ici — et donc dans ACTIVITY_META.
const TYPES_BACKEND = [
  'LESSON_STARTED',
  'LESSON_COMPLETED',
  'EXERCISE_SUBMITTED',
  'QUIZ_COMPLETED',
  'CHAPTER_UNLOCKED',
  'BADGE_EARNED',
]

describe('table des types d’activité', () => {
  it('couvre tous les types déclarés par le backend', () => {
    expect(Object.keys(ACTIVITY_META).sort()).toEqual([...TYPES_BACKEND].sort())
  })

  it('donne à chaque type une icône et un libellé en français', () => {
    for (const type of TYPES_BACKEND) {
      const { icon, label } = describeActivity({ activity_type: type, lesson_title: 'Les listes' })
      expect(icon, type).toBeTruthy()
      expect(label, type).toBeTruthy()
      // Aucune clé technique ne doit transparaître.
      expect(label, type).not.toMatch(/_/)
      expect(label.toUpperCase(), type).not.toBe(label)
    }
  })

  it('nomme LESSON_STARTED, le type qui manquait', () => {
    const { icon, label } = describeActivity({
      activity_type: ACTIVITY_TYPES.LESSON_STARTED,
      lesson_title: 'Les listes',
    })
    expect(icon).toBe('▶️')
    expect(label).toBe('Leçon commencée — Les listes')
  })

  it('reste lisible quand le contenu lié a été supprimé', () => {
    // `lesson_title` est `null` si la leçon n'existe plus : le libellé ne doit
    // pas afficher « null ».
    const { label } = describeActivity({
      activity_type: ACTIVITY_TYPES.LESSON_COMPLETED,
      lesson_title: null,
    })
    expect(label).toBe('Leçon terminée — leçon')
  })

  it('ne laisse jamais fuiter une clé technique pour un type inconnu', () => {
    // Un backend plus récent que ce fichier : mieux vaut un libellé vague
    // qu'un identifiant de base de données affiché tel quel.
    const { icon, label } = describeActivity({ activity_type: 'FORUM_POST_CREATED' })
    expect(icon).toBeTruthy()
    expect(label).toBe('Activité')
    expect(label).not.toMatch(/FORUM/)
  })
})
