import {
  avatarFaceUri,
  bordureTraits,
  initialsOf,
  initialsPalette,
  paletteColors,
  parseAvatarKey,
} from '@/features/profile/avatars'
import './Avatar.css'

/**
 * Avatar d'un utilisateur : visage choisi au catalogue, ou initiales colorées.
 *
 * Le repli sur les initiales n'est pas un pis-aller — c'est l'état par défaut
 * de tout compte, et il doit rester lisible. Sa couleur est dérivée du nom,
 * donc stable d'une session à l'autre.
 *
 * Décoratif par défaut (`aria-hidden`) : l'avatar accompagne presque toujours
 * le nom écrit juste à côté, et le doubler à l'oral n'apporte rien. Passer
 * `label` quand il apparaît seul.
 */
export default function Avatar({ user, size = 40, label, className = '' }) {
  const parsed = parseAvatarKey(user?.profile?.avatar_key)
  // La graine de couleur retombe sur le nom d'affichage quand il n'y a pas
  // d'email : c'est le cas du classement, qui n'en transmet aucun. Sans ce
  // repli, toutes les lignes à initiales partageraient la même couleur.
  const palette = parsed
    ? parsed.palette
    : initialsPalette(user?.email || user?.display_name || '')
  const colors = paletteColors(palette)
  const gradientId = `av-${palette}-${parsed ? parsed.visage : 'initials'}`

  const accessibility = label
    ? { role: 'img', 'aria-label': label }
    : { 'aria-hidden': 'true', focusable: 'false' }

  // La bordure s'applique aussi bien au visage qu'aux initiales : c'est un
  // choix de vignette, pas un accessoire du dessin.
  const traits = bordureTraits(user?.profile?.avatar_border)

  return (
    <svg
      className={`avatar ${className}`}
      width={size}
      height={size}
      viewBox="0 0 100 100"
      {...accessibility}
    >
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stopColor={colors.from} />
          <stop offset="100%" stopColor={colors.to} />
        </linearGradient>
      </defs>

      <rect width="100" height="100" rx="28" fill={`url(#${gradientId})`} />

      {parsed
        ? (
          /*
            Le visage est posé en image et non injecté en balisage : un SVG
            référencé par `<image>` est rendu en mode image, sans script ni
            requête sortante. Pas de `dangerouslySetInnerHTML` à surveiller.
          */
          <image
            href={avatarFaceUri(parsed.visage)}
            x="0"
            y="0"
            width="100"
            height="100"
            preserveAspectRatio="xMidYMid slice"
          />
        )
        : (
          <text
            x="50"
            y="50"
            textAnchor="middle"
            dominantBaseline="central"
            fill={colors.ink}
            fontSize="38"
            fontWeight="700"
            fontFamily="system-ui, sans-serif"
          >
            {initialsOf(user)}
          </text>
        )}

      {/*
        Les anneaux passent **après** le visage : dessinés avant, l'image les
        recouvrirait entièrement. Le rayon suit celui du fond, diminué de
        l'inset, sans quoi les coins seraient plus carrés que la vignette.
      */}
      {traits.map((trait) => (
        <rect
          key={`${trait.inset}-${trait.epaisseur}`}
          x={trait.inset}
          y={trait.inset}
          width={100 - trait.inset * 2}
          height={100 - trait.inset * 2}
          rx={28 - trait.inset}
          fill="none"
          stroke={trait.couleur}
          strokeWidth={trait.epaisseur}
        />
      ))}
    </svg>
  )
}
