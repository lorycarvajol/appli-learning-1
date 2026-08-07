import LegalLayout, { Todo } from './LegalLayout'

export default function LegalNotice() {
  return (
    <LegalLayout title="Mentions légales" updated="22 juillet 2026">
      <h2>Éditeur du site</h2>
      <p>
        Le site CodeAcademy est édité par <Todo>raison sociale / nom</Todo>,{' '}
        <Todo>forme juridique et capital le cas échéant</Todo>, dont le siège
        est situé <Todo>adresse</Todo>.
      </p>
      <ul>
        <li>Immatriculation (SIRET / RCS) : <Todo>numéro</Todo></li>
        <li>Numéro de TVA intracommunautaire : <Todo>numéro</Todo></li>
        <li>
          Contact :{' '}
          <a href="mailto:lorycarvajolwebdev@gmail.com">
            lorycarvajolwebdev@gmail.com
          </a>
        </li>
      </ul>

      <h2>Directeur de la publication</h2>
      <p><Todo>nom du directeur de la publication</Todo></p>

      <h2>Hébergement</h2>
      <p>
        Le site est hébergé par <Todo>nom de l’hébergeur</Todo>,{' '}
        <Todo>adresse de l’hébergeur</Todo>.
      </p>

      <h2>Propriété intellectuelle</h2>
      <p>
        L’ensemble des contenus pédagogiques, textes, logos et éléments
        graphiques présents sur la plateforme sont, sauf mention contraire, la
        propriété de l’éditeur ou de ses partenaires. Toute reproduction sans
        autorisation est interdite.
      </p>

      {/*
        Attribution des visages d'avatar. Quatre des sept familles sont sous
        licence CC BY 4.0, qui **impose** de nommer l'auteur et la licence :
        ce n'est pas une politesse mais une obligation. Cette page est publique,
        donc l'attribution est consultable sans compte — le bon régime. La liste
        double celle du sélecteur d'avatar, où le crédit accompagne l'œuvre là
        où elle est utilisée.

        ⚠️ Toute famille ajoutée à `features/profile/avatarCatalog.js` doit
        apparaître ici. `npm run avatars` vérifie les auteurs et les licences
        contre les métadonnées de DiceBear, mais il ne sait pas lire cette page.
      */}
      <h2>Crédits et licences</h2>
      <p>
        Les visages proposés au choix comme avatar sont issus de la
        bibliothèque <a href="https://www.dicebear.com/" target="_blank" rel="noreferrer noopener">DiceBear</a>.
        Ils sont générés et hébergés par la plateforme elle-même : aucune
        requête n’est adressée à un service tiers lors de leur affichage.
      </p>
      <ul>
        <li>
          <em>Notionists</em> par Zoish —{' '}
          <a href="https://creativecommons.org/publicdomain/zero/1.0/" target="_blank" rel="noreferrer noopener">CC0 1.0</a>
        </li>
        <li>
          <em>Adventurer</em> et <em>Adventurer Neutral</em> par Lisa Wischofsky —{' '}
          <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noreferrer noopener">CC BY 4.0</a>
        </li>
        <li>
          <em>Avataaars</em> par Pablo Stanley —{' '}
          <a href="https://avataaars.com/" target="_blank" rel="noreferrer noopener">libre d’usage personnel et commercial</a>
        </li>
        <li>
          <em>Big Smile</em> par Ashley Seo —{' '}
          <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noreferrer noopener">CC BY 4.0</a>
        </li>
        <li>
          <em>Bottts</em> par Pablo Stanley —{' '}
          <a href="https://bottts.com/" target="_blank" rel="noreferrer noopener">libre d’usage personnel et commercial</a>
        </li>
        <li>
          <em>ToonHead</em> par Johan Melin —{' '}
          <a href="https://creativecommons.org/licenses/by/4.0/" target="_blank" rel="noreferrer noopener">CC BY 4.0</a>
        </li>
      </ul>

      <h2>Contact</h2>
      <p>
        Pour toute question relative au site, vous pouvez écrire à{' '}
        <a href="mailto:lorycarvajolwebdev@gmail.com">
          lorycarvajolwebdev@gmail.com
        </a>.
      </p>
    </LegalLayout>
  )
}
