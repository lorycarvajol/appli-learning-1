/**
 * Validation d'une destination de navigation fournie par l'utilisateur.
 *
 * Le paramètre `?next=` du parcours de connexion sert au rattachement par
 * invitation : quelqu'un qui a déjà un compte doit revenir sur le lien après
 * s'être connecté. Cette valeur vient donc de l'URL, donc de n'importe qui.
 *
 * ## Pourquoi une liste blanche, et pas une liste de motifs interdits
 *
 * Le contrôle d'origine — « commence par `/` mais pas par `//` » — bloquait
 * l'URL absolue et la forme protocole-relatif, mais **pas l'antislash**.
 * `/\evil.com` commence bien par un seul `/` : il passait, et les navigateurs
 * le réinterprètent comme `//evil.com`, donc comme un site tiers. C'est
 * exactement le contournement décrit par l'avis de sécurité de React Router
 * (« Open redirect via backslash in `<Link>` and `useNavigate` »).
 *
 * On valide donc ce qui est **autorisé** plutôt que d'énumérer ce qui ne
 * l'est pas : un chemin interne commence par `/`, ne contient ni antislash ni
 * caractère de contrôle, et n'est pas protocole-relatif.
 *
 * ⚠️ Cette vérification est volontairement **indépendante de la version du
 * routeur**. Elle protège même si la bibliothèque régresse — et les avis en
 * cours se contredisent assez pour qu'on ne s'en remette pas à elle seule.
 */

/** Repli utilisé dès que la destination demandée n'est pas sûre. */
export const DEFAULT_REDIRECT = '/dashboard';

/**
 * Y a-t-il un caractère de contrôle dans la chaîne ?
 *
 * Écrit avec une comparaison de codes plutôt qu'une expression régulière :
 * une classe de caracteres de controle écrite littéralement place de vrais octets de
 * contrôle dans le fichier source, qui devient illisible en revue et que
 * `grep` traite comme un binaire.
 */
function contientCaractereDeControle(chaine) {
  for (const caractere of chaine) {
    const code = caractere.codePointAt(0);
    if (code < 0x20 || code === 0x7f) return true;
  }
  return false;
}

/**
 * Une destination est-elle un chemin **interne** sûr ?
 *
 * @param {unknown} chemin valeur brute, typiquement `searchParams.get('next')`
 * @returns {boolean}
 */
export function isSafeInternalPath(chemin) {
  if (typeof chemin !== 'string' || chemin === '') return false;

  // Un espace ou une tabulation en tête est ignoré par les navigateurs lors de
  // la résolution d'URL : « //evil.com » précédé d'un blanc redirigerait
  // malgré le contrôle sur `//`.
  if (chemin !== chemin.trim()) return false;
  if (contientCaractereDeControle(chemin)) return false;

  // L'antislash est le contournement documenté : les navigateurs le traitent
  // comme un `/` au moment de résoudre l'URL.
  if (chemin.includes('\\')) return false;

  if (!chemin.startsWith('/')) return false;
  if (chemin.startsWith('//')) return false;

  return true;
}

/**
 * Rend la destination demandée si elle est sûre, sinon {@link DEFAULT_REDIRECT}.
 */
export function safeRedirectPath(chemin, repli = DEFAULT_REDIRECT) {
  return isSafeInternalPath(chemin) ? chemin : repli;
}
