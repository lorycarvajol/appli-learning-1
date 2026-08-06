import { useEffect, useCallback, useRef, useState } from 'react';
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

  // Rapport largeur/hauteur du fichier, transmis au CSS en variable.
  //
  // C'est lui qui permet à la boîte de l'image d'épouser exactement l'image
  // affichée. Sans lui, le seul moyen d'agrandir une image en CSS est de lui
  // donner une largeur (`width: 100%`) et de la recentrer avec
  // `object-fit: contain` — mais la **boîte** occupe alors toute la largeur
  // disponible, et le vide de part et d'autre appartient à l'`<img>`. Cliquer
  // « à côté de l'image » ne fermait donc pas la visionneuse.
  const [ratio, setRatio] = useState(null);

  const measure = useCallback((img) => {
    if (img?.naturalWidth && img?.naturalHeight) {
      setRatio(img.naturalWidth / img.naturalHeight);
    }
  }, []);

  // Une image déjà en cache peut être `complete` avant que `onLoad` ne se
  // déclenche : on mesure aussi à l'attache de la ref.
  const imageRef = useCallback(
    (img) => {
      if (img?.complete) measure(img);
    },
    [measure]
  );

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

  // Fermer en cliquant « à côté » de l'image.
  //
  // Le test sur `currentTarget` limite la fermeture aux clics sur l'élément
  // lui-même, jamais sur un enfant. Le conteneur occupe désormais toute la
  // zone disponible (c'est ce qui permet à l'image de s'agrandir) : sans ce
  // même gestionnaire sur lui, la majeure partie du vide autour de l'image
  // aurait cessé de fermer la visionneuse.
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
      {/* Chrome hors du conteneur : fixé à la fenêtre, il ne prélève aucune
          hauteur sur l'image (cf. le commentaire d'en-tête du CSS). */}
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

      <div className="image-lightbox__container" onClick={handleBackdropClick}>
        {/* Image */}
        <img
          ref={imageRef}
          src={src}
          alt={alt}
          className="image-lightbox__image"
          style={ratio ? { '--ratio': ratio } : undefined}
          onLoad={(e) => measure(e.currentTarget)}
          onClick={(e) => e.stopPropagation()}
        />
      </div>

      {/* Légende */}
      {alt && <p className="image-lightbox__caption">{alt}</p>}

      {/* Aide */}
      <div className="image-lightbox__help">
        Appuyez sur <kbd>ESC</kbd> ou cliquez à l’extérieur pour fermer
      </div>
    </div>
  );
}
