import { useEffect, useCallback, useRef } from 'react';
import './ImageLightbox.css';

/**
 * ImageLightbox - Composant pour afficher une image en plein écran
 *
 * @param {string} src - URL de l'image
 * @param {string} alt - Texte alternatif de l'image
 * @param {function} onClose - Callback appelé lors de la fermeture
 */
export default function ImageLightbox({ src, alt, onClose }) {
  const closeButtonRef = useRef(null);
  const previouslyFocusedRef = useRef(null);

  // Fermer avec la touche Escape
  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    },
    [onClose]
  );

  // Ajouter/retirer l'event listener + gestion du focus
  useEffect(() => {
    previouslyFocusedRef.current = document.activeElement;
    closeButtonRef.current?.focus();

    document.addEventListener('keydown', handleKeyDown);
    // Empêcher le scroll du body quand le lightbox est ouvert
    document.body.style.overflow = 'hidden';

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = 'unset';
      previouslyFocusedRef.current?.focus?.();
    };
  }, [handleKeyDown]);

  // Fermer en cliquant sur le backdrop
  const handleBackdropClick = (e) => {
    if (e.target === e.currentTarget) {
      onClose();
    }
  };

  return (
    <div
      className="image-lightbox"
      onClick={handleBackdropClick}
      role="dialog"
      aria-modal="true"
      aria-label={alt || 'Illustration agrandie'}
    >
      <div className="image-lightbox__container">
        {/* Bouton de fermeture */}
        <button
          ref={closeButtonRef}
          className="image-lightbox__close"
          onClick={onClose}
          aria-label="Fermer"
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        {/* Image */}
        <img
          src={src}
          alt={alt}
          className="image-lightbox__image"
          onClick={(e) => e.stopPropagation()}
        />

        {/* Légende */}
        {alt && (
          <div className="image-lightbox__caption">
            {alt}
          </div>
        )}

        {/* Aide */}
        <div className="image-lightbox__help">
          Appuyez sur <kbd>ESC</kbd> ou cliquez à l'extérieur pour fermer
        </div>
      </div>
    </div>
  );
}
