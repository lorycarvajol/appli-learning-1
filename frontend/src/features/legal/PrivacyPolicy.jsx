import LegalLayout, { Todo } from './LegalLayout'

export default function PrivacyPolicy() {
  return (
    <LegalLayout title="Politique de confidentialité" updated="7 août 2026">
      <p>
        La présente politique décrit comment la plateforme d’apprentissage
        CodeAcademy (ci-après « la plateforme ») collecte et traite les données
        personnelles de ses utilisateurs, conformément au Règlement général sur
        la protection des données (RGPD).
      </p>

      <h2>Responsable du traitement</h2>
      <p>
        Le responsable du traitement est <strong>Lory Carvajol</strong>,
        éditant sous le nom <strong>lorycarvajol.dev</strong>, joignable à
        l’adresse{' '}
        <a href="mailto:lorycarvajolwebdev@gmail.com">
          lorycarvajolwebdev@gmail.com
        </a>.
      </p>
      {/*
        Le DPO n'est obligatoire que dans trois cas (autorité publique, suivi
        systématique à grande échelle, données sensibles à grande échelle) —
        aucun ne s'applique ici. Le dire est plus utile qu'un champ vide : un
        lecteur qui ne voit pas de DPO doit savoir à qui s'adresser.
      */}
      <p>
        Aucun délégué à la protection des données n’est désigné : la structure
        ne relève d’aucun des cas où le RGPD l’impose. Toute demande relative à
        vos données se fait à l’adresse ci-dessus.
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
        Les données sont hébergées par <strong>OVH SAS</strong> (2 rue
        Kellermann, 59100 Roubaix, France), dans des centres de données situés
        en <strong>France</strong>. Aucune donnée n’est transférée hors de
        l’Union européenne.
      </p>
      {/*
        Cette liste est courte, et c'est un choix technique assumé : aucun
        traceur, aucune police ni image chargée depuis un tiers, les avatars
        sont générés à la construction et servis par la plateforme. C'est ce
        qui permet de se passer de bannière de consentement — cf. la section
        « Cookies et stockage local » plus haut. Ajouter un service tiers
        oblige à mettre cette liste à jour **et** à réexaminer cette
        conclusion.
      */}
      <p>
        En dehors de l’hébergeur, la plateforme ne fait appel à{' '}
        <strong>aucun service tiers</strong> : ni outil de mesure d’audience,
        ni réseau de diffusion, ni police ou image chargée depuis un autre
        domaine. Le seul sous-traitant supplémentaire prévu est le{' '}
        <Todo>prestataire d’envoi d’e-mails, une fois choisi</Todo>, utilisé
        uniquement pour la réinitialisation de mot de passe.
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
