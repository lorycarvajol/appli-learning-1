import { useEffect, useRef } from 'react';
import progressionApi from '@/services/api/progressionApi';

const TICK_MS = 1000;
const FLUSH_EVERY_SECONDS = 30;
const IDLE_TIMEOUT_MS = 90_000;
const MIN_FLUSH_SECONDS = 5;

const ACTIVITY_EVENTS = ['mousemove', 'mousedown', 'keydown', 'scroll', 'touchstart'];

/**
 * Mesure le temps réellement passé sur une leçon.
 *
 * Le compteur n'avance que si l'onglet est visible **et** que l'apprenant a
 * interagi dans les 90 dernières secondes. Sans ces deux garde-fous, un
 * onglet oublié toute la nuit crédite huit heures d'apprentissage et fausse
 * les badges basés sur le temps.
 *
 * L'accumulation se fait par tics d'une seconde plutôt que par différence de
 * timestamps : si la machine se met en veille ou que le navigateur gèle le
 * timer, les tics ne se produisent pas et le temps n'est pas compté — ce qui
 * est précisément le comportement voulu.
 *
 * Le serveur reçoit des **incréments** (`track_time`), jamais un total :
 * deux onglets ouverts sur la même leçon s'additionnent au lieu de s'écraser.
 */
export default function useTimeTracker(lessonId) {
  const pendingRef = useRef(0);
  const lastActivityRef = useRef(Date.now());

  useEffect(() => {
    if (!lessonId) return undefined;

    pendingRef.current = 0;
    lastActivityRef.current = Date.now();

    const markActive = () => {
      lastActivityRef.current = Date.now();
    };
    ACTIVITY_EVENTS.forEach((event) =>
      window.addEventListener(event, markActive, { passive: true })
    );

    const flush = ({ keepalive = false } = {}) => {
      const seconds = pendingRef.current;
      if (seconds < MIN_FLUSH_SECONDS) return;
      pendingRef.current = 0;

      if (keepalive) {
        // Sur fermeture d'onglet, une requête XHR classique est annulée.
        // `fetch(keepalive)` survit au déchargement de la page.
        progressionApi.trackTimeBeacon(lessonId, seconds);
      } else {
        progressionApi.trackTime(lessonId, seconds).catch(() => {
          // Perdre un intervalle de suivi n'est pas une erreur à remonter
          // à l'apprenant : on réessaiera au tic suivant.
        });
      }
    };

    const interval = setInterval(() => {
      const isVisible = document.visibilityState === 'visible';
      const isIdle = Date.now() - lastActivityRef.current > IDLE_TIMEOUT_MS;
      if (!isVisible || isIdle) return;

      pendingRef.current += TICK_MS / 1000;
      if (pendingRef.current >= FLUSH_EVERY_SECONDS) flush();
    }, TICK_MS);

    // L'onglet passe en arrière-plan (ou se ferme sur mobile) : on sauve le
    // reliquat tant que la page est encore vivante.
    const onVisibilityChange = () => {
      if (document.visibilityState === 'hidden') flush({ keepalive: true });
    };
    const onPageHide = () => flush({ keepalive: true });
    document.addEventListener('visibilitychange', onVisibilityChange);
    window.addEventListener('pagehide', onPageHide);

    return () => {
      clearInterval(interval);
      ACTIVITY_EVENTS.forEach((event) => window.removeEventListener(event, markActive));
      document.removeEventListener('visibilitychange', onVisibilityChange);
      window.removeEventListener('pagehide', onPageHide);
      // Changement de leçon ou démontage : on envoie le reliquat.
      flush();
    };
  }, [lessonId]);
}
