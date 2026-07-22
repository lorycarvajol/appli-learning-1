import LegalLayout, { Todo } from './LegalLayout'

export default function PrivacyPolicy() {
  return (
    <LegalLayout title="Politique de confidentialité" updated="22 juillet 2026">
      <p>
        La présente politique décrit comment la plateforme d’apprentissage
        CodeAcademy (ci-après « la plateforme ») collecte et traite les données
        personnelles de ses utilisateurs, conformément au Règlement général sur
        la protection des données (RGPD).
      </p>

      <h2>Responsable du traitement</h2>
      <p>
        Le responsable du traitement est <Todo>identité de l’organisme</Todo>,
        joignable à l’adresse{' '}
        <a href="mailto:lorycarvajolwebdev@gmail.com">
          lorycarvajolwebdev@gmail.com
        </a>.
      </p>
      <p>
        Délégué à la protection des données (DPO), le cas échéant :{' '}
        <Todo>nom et contact du DPO</Todo>.
      </p>

      <h2>Données que nous collectons</h2>
      <ul>
        <li>
          <strong>Identité et compte</strong> : adresse e-mail, prénom, nom,
          mot de passe (stocké de façon hachée, jamais en clair).
        </li>
        <li>
          <strong>Profil</strong> : biographie facultative, pseudo GitHub,
          avatar choisi, préférence de thème et de fuseau horaire.
        </li>
        <li>
          <strong>Progression pédagogique</strong> : leçons commencées et
          terminées, tentatives, scores aux quiz, temps passé, code soumis aux
          exercices.
        </li>
        <li>
          <strong>Gamification</strong> : points, niveau, badges obtenus, série
          de jours d’activité.
        </li>
        <li>
          <strong>Classe</strong> : rattachement éventuel à une classe et à un
          formateur.
        </li>
      </ul>
      <p>
        Nous ne collectons <strong>aucune donnée de navigation à des fins
        publicitaires</strong> et n’utilisons aucun traceur tiers.
      </p>

      <h2>Finalités et base légale</h2>
      <ul>
        <li>
          <strong>Fournir le service</strong> (compte, progression, suivi
          pédagogique) — base légale : exécution du contrat / consentement à
          l’inscription.
        </li>
        <li>
          <strong>Sécurité</strong> (limitation des tentatives de connexion,
          journal d’audit des actions d’administration) — base légale : intérêt
          légitime.
        </li>
        <li>
          <strong>Suivi par le formateur</strong> pour les apprenants rattachés
          à une classe — base légale : exécution du contrat pédagogique.
        </li>
      </ul>

      <h2>Cookies et stockage local</h2>
      <p>
        La plateforme n’utilise <strong>que des cookies et un stockage
        strictement nécessaires</strong> à son fonctionnement :
      </p>
      <ul>
        <li>
          des jetons d’authentification (JWT) conservés dans le stockage local
          (<code>localStorage</code>) de votre navigateur, pour vous garder
          connecté ;
        </li>
        <li>
          des cookies techniques de session et de protection anti-CSRF côté
          serveur.
        </li>
      </ul>
      <p>
        Ces éléments étant indispensables au service, ils ne requièrent pas de
        recueil de consentement préalable au sens des recommandations de la
        CNIL. Aucun cookie de mesure d’audience ou de publicité n’est déposé.
        Vous pouvez à tout moment les effacer via les réglages de votre
        navigateur ; vous serez alors déconnecté.
      </p>

      <h2>Durée de conservation</h2>
      <p>
        Les données sont conservées tant que le compte est actif. En cas de
        suppression (voir ci-dessous), les données d’identité sont
        immédiatement effacées ; les données de progression, anonymisées, sont
        conservées sous une forme ne permettant plus de vous identifier, afin
        de préserver l’intégrité des statistiques des classes.
      </p>

      <h2>Vos droits</h2>
      <p>Conformément au RGPD, vous disposez des droits suivants :</p>
      <ul>
        <li>
          <strong>Accès et portabilité</strong> : vous pouvez exporter
          l’ensemble de vos données à tout moment depuis votre page{' '}
          <strong>Profil → Mes données</strong> (fichier JSON).
        </li>
        <li>
          <strong>Rectification</strong> : vous pouvez modifier vos
          informations depuis votre page Profil.
        </li>
        <li>
          <strong>Effacement</strong> : vous pouvez supprimer votre compte
          vous-même depuis <strong>Profil → Mes données</strong>. L’opération
          est irréversible et efface vos données personnelles.
        </li>
        <li>
          <strong>Opposition et limitation</strong> : vous pouvez nous contacter
          à{' '}
          <a href="mailto:lorycarvajolwebdev@gmail.com">
            lorycarvajolwebdev@gmail.com
          </a>{' '}
          pour exercer ces droits.
        </li>
      </ul>
      <p>
        Vous pouvez également introduire une réclamation auprès de la CNIL
        (<a href="https://www.cnil.fr" target="_blank" rel="noreferrer">
          www.cnil.fr
        </a>).
      </p>

      <h2>Hébergement et sous-traitants</h2>
      <p>
        Les données sont hébergées par <Todo>nom et pays de l’hébergeur</Todo>.
        Les éventuels services tiers utilisés (envoi d’e-mails transactionnels,
        stockage) sont listés ici : <Todo>liste des sous-traitants</Todo>.
      </p>

      <h2>Sécurité</h2>
      <p>
        Les mots de passe sont hachés, les échanges chiffrés en HTTPS, l’accès
        aux données des apprenants est cloisonné par classe et toute action
        d’administration sensible est journalisée.
      </p>
    </LegalLayout>
  )
}
