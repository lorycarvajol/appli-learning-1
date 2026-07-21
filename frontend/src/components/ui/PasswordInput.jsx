import { useState } from 'react'

/**
 * Champ mot de passe avec bouton d'affichage.
 *
 * Le petit singe indique l'état *actuel* du champ, pas l'action du bouton :
 * 🙈 les yeux couverts = le mot de passe est masqué, 🐵 les yeux ouverts = il
 * est lisible. L'action, elle, est portée par l'`aria-label`, qui dit bien ce
 * que fera le clic — un lecteur d'écran ne voit pas l'emoji.
 *
 * Reprend les classes `auth-form__*` : le champ reste visuellement identique
 * aux autres, seul le padding droit change pour laisser la place au bouton.
 */
export default function PasswordInput({ id, className = '', ...inputProps }) {
  const [visible, setVisible] = useState(false)

  return (
    <div className="password-field">
      <input
        id={id}
        type={visible ? 'text' : 'password'}
        className={`auth-form__input password-field__input ${className}`.trim()}
        {...inputProps}
      />
      <button
        type="button"
        className="password-field__toggle"
        onClick={() => setVisible((shown) => !shown)}
        aria-label={visible ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
        aria-pressed={visible}
        aria-controls={id}
        title={visible ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
      >
        <span aria-hidden="true">{visible ? '🐵' : '🙈'}</span>
      </button>
    </div>
  )
}
