import { useCallback, useEffect, useRef } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  acknowledgeBadges,
  dismissReveal,
  selectPendingReveal,
} from './gamificationSlice';
import './BadgeRevealModal.css';

const CONFETTI_COUNT = 24;

/**
 * Célébration d'un badge fraîchement débloqué.
 *
 * Monté une seule fois dans le Layout : il consomme la file de révélation du
 * store, badge après badge. Chaque fermeture acquitte le badge côté serveur
 * (`mark_seen`), donc l'animation ne se rejoue pas au rechargement.
 */
export default function BadgeRevealModal() {
  const dispatch = useDispatch();
  const badge = useSelector(selectPendingReveal);
  const closeRef = useRef(null);

  const handleClose = useCallback(() => {
    if (!badge) return;
    dispatch(acknowledgeBadges([badge.id]));
    dispatch(dismissReveal());
  }, [dispatch, badge]);

  useEffect(() => {
    if (badge) closeRef.current?.focus();
  }, [badge]);

  useEffect(() => {
    if (!badge) return undefined;
    const onKeyDown = (e) => {
      if (e.key === 'Escape') handleClose();
    };
    document.addEventListener('keydown', onKeyDown);
    return () => document.removeEventListener('keydown', onKeyDown);
  }, [badge, handleClose]);

  if (!badge) return null;

  return (
    <div className="badge-reveal" role="presentation" onClick={handleClose}>
      <div
        className={`badge-reveal__card badge-reveal__card--${badge.tier.toLowerCase()}`}
        role="alertdialog"
        aria-modal="true"
        aria-labelledby="badge-reveal-title"
        aria-describedby="badge-reveal-desc"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="badge-reveal__confetti" aria-hidden="true">
          {Array.from({ length: CONFETTI_COUNT }, (_, i) => (
            <span
              key={i}
              className="badge-reveal__confetto"
              style={{
                left: `${(i / CONFETTI_COUNT) * 100}%`,
                animationDelay: `${(i % 8) * 0.09}s`,
              }}
            />
          ))}
        </div>

        <p className="badge-reveal__kicker">
          {badge.was_secret ? 'Objectif secret révélé !' : 'Nouveau trophée !'}
        </p>

        <div className="badge-reveal__medal" aria-hidden="true">
          <span className="badge-reveal__icon">{badge.icon}</span>
        </div>

        <h2 className="badge-reveal__name" id="badge-reveal-title">
          {badge.name}
        </h2>
        <p className="badge-reveal__description" id="badge-reveal-desc">
          {badge.description}
        </p>

        {badge.points_reward > 0 && (
          <p className="badge-reveal__reward">+{badge.points_reward} points</p>
        )}

        <button
          type="button"
          className="badge-reveal__button"
          onClick={handleClose}
          ref={closeRef}
        >
          Continuer
        </button>
      </div>
    </div>
  );
}
