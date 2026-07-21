/**
 * Rôles utilisateur — miroir de `User.Role` côté Django.
 *
 * Rappel : ces constantes ne servent qu'à l'affichage et au routage. La garde
 * côté client empêche un apprenant de tomber sur une page vide, elle ne
 * protège **rien** — les données sont protégées par `IsTrainerOrAdmin` côté
 * API, qui reste la seule autorité.
 */
export const ROLES = {
  LEARNER: 'LEARNER',
  TRAINER: 'TRAINER',
  ADMIN: 'ADMIN',
}

/** Rôles autorisés à piloter des apprenants (espace formateur). */
export const STAFF_ROLES = [ROLES.TRAINER, ROLES.ADMIN]

export const ROLE_LABELS = {
  [ROLES.LEARNER]: 'Apprenant',
  [ROLES.TRAINER]: 'Formateur',
  [ROLES.ADMIN]: 'Admin',
}
