import { useEffect, useState } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { Link } from 'react-router-dom'
import Avatar from '@/components/ui/Avatar'
import {
  fetchLeaderboard,
  selectLeaderboard,
  selectLeaderboardLoading,
} from './gamificationSlice'
import './LeaderboardPage.css'

/**
 * Classement des apprenants.
 *
 * Ce que la page affiche vient tel quel du serveur : les noms arrivent déjà
 * réduits à « Prénom N. » et aucun email n'est transmis (cf.
 * `backend/apps/gamification/leaderboard.py`). Il n'y a donc **rien à masquer
 * ici** — et surtout rien à « compléter » : ré-afficher un nom entier
 * demanderait de le faire sortir de l'API, ce que le backend refuse.
 *
 * Le rang personnel est épinglé en permanence, même quand il tombe hors du
 * tableau : un palmarès qui ne parle qu'à ses vingt premiers ne sert à rien
 * au vingt-et-unième.
 */

const SCOPES = [
  { key: 'global', label: 'Toute la plateforme' },
  { key: 'cohort', label: 'Ma classe' },
]

const MEDALS = { 1: '🥇', 2: '🥈', 3: '🥉' }

export default function LeaderboardPage() {
  const dispatch = useDispatch()
  const [scope, setScope] = useState('global')
  const board = useSelector(selectLeaderboard(scope))
  const loading = useSelector(selectLeaderboardLoading)
  const optedOut = useSelector(
    (state) => state.auth.user?.profile?.show_in_leaderboard === false
  )

  useEffect(() => {
    dispatch(fetchLeaderboard({ scope }))
  }, [dispatch, scope])

  const entries = board?.entries || []

  return (
    <div className="leaderboard">
      <header className="leaderboard__hero">
        <div className="leaderboard__hero-content">
          <h1 className="leaderboard__title">Classement</h1>
          <p className="leaderboard__subtitle">
            Les points viennent des leçons terminées, des exercices réussis et
            des trophées — rien d’autre ne les fait bouger.
          </p>

          <nav className="leaderboard__scopes" aria-label="Portée du classement">
            {SCOPES.map((item) => (
              <button
                key={item.key}
                type="button"
                className={`leaderboard__scope ${
                  scope === item.key ? 'leaderboard__scope--active' : ''
                }`}
                aria-pressed={scope === item.key}
                onClick={() => setScope(item.key)}
              >
                {item.label}
              </button>
            ))}
          </nav>
        </div>
      </header>

      <div className="leaderboard__container">
        {board && !board.available ? (
          <p className="leaderboard__empty">
            {board.reason}{' '}
            Le classement général reste accessible dans l’onglet voisin.
          </p>
        ) : loading && !board ? (
          <p className="leaderboard__empty">Chargement du classement…</p>
        ) : entries.length === 0 ? (
          <p className="leaderboard__empty">
            Personne n’a encore marqué de point ici. À vous de commencer.
          </p>
        ) : (
          <>
            <MyPosition board={board} optedOut={optedOut} />

            <ol className="leaderboard__list">
              {entries.map((entry, index) => (
                <Row key={`${entry.rank}-${entry.display_name}-${index}`} entry={entry} />
              ))}
            </ol>

            <p className="leaderboard__footnote">
              {board.total_participants} apprenant(s) classé(s). Vous pouvez
              vous retirer de cette liste à tout moment depuis{' '}
              <Link to="/profil">votre profil</Link> — vos points et vos
              trophées, eux, ne bougent pas.
            </p>
          </>
        )}
      </div>
    </div>
  )
}

/**
 * Bandeau « votre position ».
 *
 * `me: null` recouvre deux situations que l'apprenant ne doit surtout pas
 * confondre : s'être retiré volontairement du classement, ou ne pas y être
 * encore entré. Le serveur ne les distingue pas (il renvoie la même absence
 * dans les deux cas) ; c'est le réglage du profil, déjà chargé, qui tranche.
 * Afficher « non classé » à quelqu'un qui s'est retiré ressemblerait à une
 * panne, et l'inverse laisserait croire à un réglage qu'il n'a pas touché.
 */
function MyPosition({ board, optedOut }) {
  if (board.me) {
    return (
      <section className="leaderboard__me" aria-label="Votre position">
        <span className="leaderboard__me-rank">#{board.me.rank}</span>
        <span className="leaderboard__me-text">
          Votre position sur {board.total_participants} apprenant(s) classé(s)
        </span>
        <span className="leaderboard__me-points">{board.me.points} pts</span>
      </section>
    )
  }

  return (
    <section className="leaderboard__me leaderboard__me--out" aria-label="Votre position">
      <span className="leaderboard__me-text">
        {optedOut ? (
          <>
            Vous vous êtes retiré du classement : vous n’y figurez pas et n’y
            voyez pas votre rang. Réversible depuis{' '}
            <Link to="/profil">votre profil</Link>.
          </>
        ) : (
          'Terminez une leçon pour entrer au classement.'
        )}
      </span>
    </section>
  )
}

function Row({ entry }) {
  const medal = MEDALS[entry.rank]

  return (
    <li
      className={`leaderboard-row ${entry.is_me ? 'leaderboard-row--me' : ''}`}
      aria-current={entry.is_me ? 'true' : undefined}
    >
      <span className="leaderboard-row__rank">
        {medal ? <span aria-hidden="true">{medal}</span> : null}
        <span className={medal ? 'leaderboard-row__rank-number--medal' : ''}>
          {entry.rank}
        </span>
      </span>

      <Avatar
        user={{
          display_name: entry.display_name,
          profile: { avatar_key: entry.avatar_key },
        }}
        size={40}
        className="leaderboard-row__avatar"
      />

      <span className="leaderboard-row__identity">
        <span className="leaderboard-row__name">{entry.display_name}</span>
        {entry.is_me && <span className="leaderboard-row__badge-me">Vous</span>}
      </span>

      <span className="leaderboard-row__stat">
        Niveau {entry.level}
      </span>
      <span className="leaderboard-row__stat leaderboard-row__stat--trophies">
        {entry.badges_count} 🏅
      </span>
      <span className="leaderboard-row__points">{entry.points} pts</span>
    </li>
  )
}
