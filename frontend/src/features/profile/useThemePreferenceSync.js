import { useEffect, useRef } from 'react'
import { useDispatch, useSelector } from 'react-redux'
import { useTheme } from '@/contexts/useTheme'
import { updateProfile } from '@/features/auth/authSlice'

/**
 * Rattache la préférence de thème au compte plutôt qu'au navigateur.
 *
 * Deux flux, volontairement asymétriques :
 *
 * - **Serveur → client**, à la connexion : la préférence enregistrée gagne sur
 *   celle du navigateur. C'est ce qui fait suivre le réglage d'un poste à
 *   l'autre, ce qui est tout l'intérêt de le stocker côté compte.
 * - **Client → serveur**, quand l'utilisateur bascule le thème lui-même.
 *
 * Le garde-fou contre la boucle est `syncedRef` : sans lui, l'écriture serveur
 * met à jour `user.profile.theme`, ce qui redéclenche l'effet de descente, qui
 * réécrit la préférence, qui redéclenche la remontée. On ne remonte donc que
 * si la valeur diffère réellement de celle déjà connue du serveur.
 */
export default function useThemePreferenceSync() {
  const dispatch = useDispatch()
  const { preference, setPreference } = useTheme()
  const savedTheme = useSelector((state) => state.auth.user?.profile?.theme)
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated)

  const appliedRef = useRef(null)

  // Descente : le compte impose sa préférence, une fois par valeur reçue.
  useEffect(() => {
    if (!savedTheme || appliedRef.current === savedTheme) return
    appliedRef.current = savedTheme
    setPreference(savedTheme)
  }, [savedTheme, setPreference])

  // Remontée : l'utilisateur a basculé le thème depuis l'en-tête.
  useEffect(() => {
    if (!isAuthenticated || !savedTheme) return
    if (preference === savedTheme) return
    // Évite de renvoyer ce qu'on vient tout juste d'appliquer.
    if (appliedRef.current === preference) return

    appliedRef.current = preference
    dispatch(updateProfile({ profile: { theme: preference } }))
  }, [preference, savedTheme, isAuthenticated, dispatch])
}
