import { useCallback, useEffect, useRef, useState } from 'react';

/** Durée pendant laquelle le bas doit rester visible avant de valider. */
export const DWELL_MS = 3000;

/**
 * Valide une leçon quand l'apprenant atteint le bas du contenu.
 *
 * Remplace le bouton « Marquer comme terminé », qui demandait de déclarer soi-
 * même une progression que l'application peut constater.
 *
 * ## Pourquoi un repère observé, et pas un calcul de défilement
 *
 * Comparer `scrollY + innerHeight` à `scrollHeight` oblige à écouter `scroll`
 * en continu, à l'amortir, et à retomber juste malgré les images qui arrivent
 * après coup et rallongent la page. Un élément-repère placé à la fin du contenu
 * et confié à un `IntersectionObserver` répond exactement à la question posée —
 * « ce point est-il à l'écran ? » — sans écouteur global et en suivant les
 * changements de mise en page.
 *
 * ## Le délai n'est pas cosmétique
 *
 * Une leçon courte tient entièrement à l'écran : son repère est visible dès
 * l'ouverture. Valider aussitôt marquerait la leçon terminée avant même qu'elle
 * s'affiche, ce qui est aussi faux que l'ancien bouton. Le repère doit donc
 * rester visible {@link DWELL_MS} millisecondes d'affilée ; remonter avant la
 * fin annule le compte à rebours.
 *
 * ## Ce que ce hook ne fait pas
 *
 * Il ne s'applique **qu'à la théorie**. Un exercice se valide en passant ses
 * tests, un quiz en atteignant le score requis — déclarer l'un ou l'autre
 * terminé parce qu'on a fait défiler la page reviendrait à en distribuer les
 * points sans le travail. `LessonView` ne le monte donc que pour `THEORY`.
 *
 * @param {object}   options
 * @param {boolean}  options.enabled  Faux ⇒ aucun observateur n'est créé.
 * @param {Function} options.onComplete Appelé **une seule fois** par leçon.
 * @param {*}        options.resetOn Identité de la leçon courante. En changer
 *   réarme le verrou de déclenchement — indispensable car `LessonView` ne se
 *   remonte pas quand on passe d'une leçon à la suivante : sans cela, la
 *   première leçon lue serait la seule jamais validée.
 * @returns {{sentinelRef: Function, reached: boolean}}
 */
export default function useScrollCompletion({ enabled, onComplete, resetOn }) {
  const [reached, setReached] = useState(false);
  const [sentinel, setSentinel] = useState(null);

  // `onComplete` est presque toujours une lambda recréée à chaque rendu ; la
  // garder dans une ref évite de reconstruire l'observateur pour rien.
  const onCompleteRef = useRef(onComplete);
  useEffect(() => {
    onCompleteRef.current = onComplete;
  }, [onComplete]);

  // Un seul déclenchement par leçon, même si le repère repasse à l'écran.
  const firedRef = useRef(false);
  useEffect(() => {
    firedRef.current = false;
    setReached(false);
  }, [enabled, resetOn]);

  // Callback ref plutôt que `useRef` : on veut être prévenu du moment où le
  // nœud existe. Avec une ref classique, l'effet tournerait au premier rendu,
  // quand le repère n'est pas encore monté.
  const sentinelRef = useCallback((node) => setSentinel(node), []);

  useEffect(() => {
    if (!enabled || !sentinel) return undefined;

    // Environnement sans IntersectionObserver (très anciens navigateurs, ou
    // jsdom sans polyfill) : on s'abstient plutôt que de valider à tort.
    if (typeof IntersectionObserver === 'undefined') return undefined;

    let timer = null;
    const cancel = () => {
      if (timer) {
        clearTimeout(timer);
        timer = null;
      }
    };

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (!entry.isIntersecting) {
          cancel();
          return;
        }
        if (firedRef.current || timer) return;

        timer = setTimeout(() => {
          timer = null;
          if (firedRef.current) return;
          firedRef.current = true;
          setReached(true);
          onCompleteRef.current?.();
        }, DWELL_MS);
      },
      // Le repère compte comme atteint dès qu'il entre dans la fenêtre, sans
      // exiger qu'il soit collé au bord — sur une page qui finit par un bloc
      // de navigation, le tout dernier pixel n'est pas toujours accessible.
      { threshold: 0 }
    );

    observer.observe(sentinel);
    return () => {
      cancel();
      observer.disconnect();
    };
  }, [enabled, sentinel]);

  return { sentinelRef, reached };
}
