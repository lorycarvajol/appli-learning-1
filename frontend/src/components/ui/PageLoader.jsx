/**
 * Écran d'attente d'un morceau de code chargé à la demande (`React.lazy`).
 *
 * Réutilise `.route-guard` + `.loading-spinner`, déjà employés par la garde de
 * route pendant la résolution de l'identité : le chargement d'une page découpée
 * ressemble ainsi à celui d'une page protégée, plutôt que d'introduire un
 * troisième style d'attente.
 */
export default function PageLoader() {
  return (
    <div className="route-guard" role="status" aria-live="polite">
      <div className="loading-spinner" aria-hidden="true" />
      <span className="route-guard__text">Chargement…</span>
    </div>
  )
}
