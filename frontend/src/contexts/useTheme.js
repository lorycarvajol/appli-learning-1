import { useContext } from 'react';
import { ThemeContext } from './themeContext';

/**
 * Accès au thème courant et à la préférence de l'utilisateur.
 *
 * Ce hook vit dans son propre fichier pour que `ThemeProvider.jsx` n'exporte
 * que des composants : mélanger composants et fonctions dans un module casse
 * le rafraîchissement à chaud de Vite, qui remonte alors l'état à chaque
 * sauvegarde.
 */
export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme doit être utilisé à l\'intérieur de ThemeProvider');
  }
  return context;
}
