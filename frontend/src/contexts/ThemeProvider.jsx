import { useCallback, useEffect, useMemo, useState } from 'react';
import { ThemeContext } from './themeContext';

/**
 * Thème de l'interface.
 *
 * On distingue la **préférence** (`AUTO` / `LIGHT` / `DARK`) du **thème
 * appliqué** (`light` / `dark`). `AUTO` n'est pas un troisième thème : c'est
 * l'absence de choix, qui laisse le système d'exploitation décider et doit
 * continuer à le suivre s'il change en cours de session. Confondre les deux
 * empêchait de revenir à ce comportement une fois un choix fait.
 *
 * ⚠️ Ce contexte est monté **au-dessus du store Redux** (`main.jsx`) : il ne
 * peut donc pas lire le profil de l'utilisateur. La synchronisation avec le
 * compte est faite dans l'autre sens par `useThemePreferenceSync`, monté à
 * l'intérieur de l'application.
 */

const STORAGE_KEY = 'theme-preference';
const PREFERENCES = ['AUTO', 'LIGHT', 'DARK'];

function storedPreference() {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (PREFERENCES.includes(stored)) return stored;

  // Reprise de l'ancien format (`theme` + `theme-explicit`), pour ne pas
  // renvoyer en clair tous les utilisateurs qui avaient déjà choisi.
  const legacy = localStorage.getItem('theme');
  if (localStorage.getItem('theme-explicit') && (legacy === 'light' || legacy === 'dark')) {
    return legacy.toUpperCase();
  }
  return 'AUTO';
}

function systemTheme() {
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

export function ThemeProvider({ children }) {
  const [preference, setPreferenceState] = useState(storedPreference);
  const [system, setSystem] = useState(systemTheme);

  // En `AUTO`, un changement de thème système doit être suivi en direct.
  useEffect(() => {
    const media = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (event) => setSystem(event.matches ? 'dark' : 'light');
    media.addEventListener('change', handleChange);
    return () => media.removeEventListener('change', handleChange);
  }, []);

  const theme = preference === 'AUTO' ? system : preference.toLowerCase();

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const setPreference = useCallback((next) => {
    if (!PREFERENCES.includes(next)) return;
    localStorage.setItem(STORAGE_KEY, next);
    setPreferenceState(next);
  }, []);

  const value = useMemo(
    () => ({
      theme,
      preference,
      setPreference,
      /** Bascule clair ↔ sombre, en figeant le choix (on quitte `AUTO`). */
      toggleTheme: () => setPreference(theme === 'dark' ? 'LIGHT' : 'DARK'),
    }),
    [theme, preference, setPreference]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}
