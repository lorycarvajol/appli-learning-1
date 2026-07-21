import { createContext } from 'react';

/**
 * Contexte du thème, isolé dans son propre module.
 *
 * Ce n'est pas de la sur-découpe : Vite ne sait rafraîchir un module à chaud
 * que s'il n'exporte que des composants. Garder l'objet de contexte et le hook
 * aux côtés de `ThemeProvider` remontait tout l'état de l'application à chaque
 * sauvegarde de fichier.
 *
 * Consommer via `useTheme()`, jamais directement.
 */
export const ThemeContext = createContext(null);
