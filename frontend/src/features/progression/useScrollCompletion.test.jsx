import { act, render } from '@testing-library/react';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';

import useScrollCompletion, { DWELL_MS } from './useScrollCompletion';

/**
 * Le bouton « Marquer comme terminé » demandait à l'apprenant de déclarer une
 * progression que l'application peut constater. Il est remplacé par
 * l'observation d'un repère placé en fin de contenu.
 *
 * Trois propriétés font la différence entre « constater » et « distribuer des
 * points au hasard », et chacune est verrouillée ici.
 */

/** Pilote un IntersectionObserver factice : jsdom n'en fournit aucun. */
let observers = [];

function setupObserver() {
  observers = [];
  vi.stubGlobal(
    'IntersectionObserver',
    class {
      constructor(callback) {
        this.callback = callback;
        this.disconnect = vi.fn();
        observers.push(this);
      }

      observe() {}

      /** Simule l'entrée (ou la sortie) du repère dans la fenêtre. */
      trigger(isIntersecting) {
        this.callback([{ isIntersecting }]);
      }
    }
  );
}

function Harness({ enabled = true, onComplete, resetOn }) {
  const { sentinelRef, reached } = useScrollCompletion({ enabled, onComplete, resetOn });
  return (
    <div>
      <span data-testid="reached">{String(reached)}</span>
      <div ref={sentinelRef} />
    </div>
  );
}

beforeEach(() => {
  vi.useFakeTimers();
  setupObserver();
});

afterEach(() => {
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

describe('useScrollCompletion', () => {
  it('valide la leçon quand le bas reste visible assez longtemps', () => {
    const onComplete = vi.fn();
    render(<Harness onComplete={onComplete} />);

    act(() => observers[0].trigger(true));
    expect(onComplete).not.toHaveBeenCalled();

    act(() => vi.advanceTimersByTime(DWELL_MS));
    expect(onComplete).toHaveBeenCalledTimes(1);
  });

  it('ne valide pas si le bas est quitté avant la fin du délai', () => {
    // Le cas d'un défilement rapide de haut en bas puis retour : l'apprenant
    // n'a rien lu, la leçon ne doit pas être créditée.
    const onComplete = vi.fn();
    render(<Harness onComplete={onComplete} />);

    act(() => observers[0].trigger(true));
    act(() => vi.advanceTimersByTime(DWELL_MS - 500));
    act(() => observers[0].trigger(false));
    act(() => vi.advanceTimersByTime(5000));

    expect(onComplete).not.toHaveBeenCalled();
  });

  it('ne valide qu’une seule fois, même si le repère repasse à l’écran', () => {
    // Sinon chaque aller-retour en bas de page relancerait un appel réseau.
    const onComplete = vi.fn();
    render(<Harness onComplete={onComplete} />);

    act(() => observers[0].trigger(true));
    act(() => vi.advanceTimersByTime(DWELL_MS));

    act(() => observers[0].trigger(false));
    act(() => observers[0].trigger(true));
    act(() => vi.advanceTimersByTime(DWELL_MS * 3));

    expect(onComplete).toHaveBeenCalledTimes(1);
  });

  it('se réarme en passant à la leçon suivante', () => {
    // `LessonView` ne se remonte pas quand le slug change : sans réarmement,
    // la première leçon lue serait la seule jamais validée de la session.
    const onComplete = vi.fn();
    const { rerender } = render(<Harness onComplete={onComplete} resetOn="lecon-1" />);

    act(() => observers[0].trigger(true));
    act(() => vi.advanceTimersByTime(DWELL_MS));
    expect(onComplete).toHaveBeenCalledTimes(1);

    rerender(<Harness onComplete={onComplete} resetOn="lecon-2" />);
    act(() => observers[observers.length - 1].trigger(true));
    act(() => vi.advanceTimersByTime(DWELL_MS));

    expect(onComplete).toHaveBeenCalledTimes(2);
  });

  it('n’observe rien quand il est désactivé', () => {
    // C'est ce qui empêche un exercice ou un quiz d'être validé au défilement :
    // `LessonView` ne l'active que pour la théorie non terminée.
    const onComplete = vi.fn();
    render(<Harness enabled={false} onComplete={onComplete} />);

    expect(observers).toHaveLength(0);
    act(() => vi.advanceTimersByTime(DWELL_MS * 3));
    expect(onComplete).not.toHaveBeenCalled();
  });

  it('expose `reached` pour l’affichage, une fois le délai écoulé', () => {
    const { getByTestId } = render(<Harness onComplete={vi.fn()} />);
    expect(getByTestId('reached').textContent).toBe('false');

    act(() => observers[0].trigger(true));
    act(() => vi.advanceTimersByTime(DWELL_MS));

    expect(getByTestId('reached').textContent).toBe('true');
  });

  it('s’abstient si le navigateur n’a pas d’IntersectionObserver', () => {
    // Mieux vaut ne rien valider que valider à tort : sans observateur, on ne
    // peut pas savoir si l'apprenant a atteint le bas.
    vi.stubGlobal('IntersectionObserver', undefined);
    const onComplete = vi.fn();

    expect(() => render(<Harness onComplete={onComplete} />)).not.toThrow();
    act(() => vi.advanceTimersByTime(DWELL_MS * 3));
    expect(onComplete).not.toHaveBeenCalled();
  });
});
