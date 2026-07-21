import { useState } from 'react';
import ImageLightbox from './ImageLightbox';
import './MarkdownImage.css';

/**
 * MarkdownImage - Composant d'image cliquable pour ReactMarkdown
 * Affiche l'image avec un effet hover et ouvre un lightbox au clic
 */
export default function MarkdownImage(props) {
  // `node` est l'AST fourni par react-markdown : on l'extrait pour qu'il ne
  // finisse pas dans les attributs DOM via `...rest`, mais on ne s'en sert pas.
  // eslint-disable-next-line no-unused-vars
  const { src, alt, title, node, ...rest } = props;
  const [isLightboxOpen, setIsLightboxOpen] = useState(false);

  const handleImageClick = (e) => {
    e.preventDefault();
    setIsLightboxOpen(true);
  };

  const handleCloseLightbox = () => {
    setIsLightboxOpen(false);
  };

  return (
    <>
      <span className="markdown-image-wrapper" onClick={handleImageClick}>
        <img
          src={src}
          alt={alt || ''}
          title={title || ''}
          className="markdown-image"
          loading="lazy"
          {...rest}
        />

        {/* Indicateur de clic */}
        <span className="markdown-image__overlay">
          <svg
            className="markdown-image__icon"
            xmlns="http://www.w3.org/2000/svg"
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7" />
          </svg>
          <span className="markdown-image__text">Cliquer pour agrandir</span>
        </span>
      </span>

      {/* Lightbox */}
      {isLightboxOpen && (
        <ImageLightbox
          src={src}
          alt={alt || title || ''}
          onClose={handleCloseLightbox}
        />
      )}
    </>
  );
}
