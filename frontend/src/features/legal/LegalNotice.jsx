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
