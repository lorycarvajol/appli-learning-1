import {
  initialsOf,
  initialsPalette,
  motifShapes,
  paletteColors,
  parseAvatarKey,
} from '@/features/profile/avatars'

/**
 * Avatar d'un utilisateur : motif choisi au catalogue, ou initiales colorées.
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
  const palette = parsed ? parsed.palette : initialsPalette(user?.email || '')
  const colors = paletteColors(palette)
  const gradientId = `av-${palette}-${parsed ? parsed.motif : 'initials'}`

  const accessibility = label
    ? { role: 'img', 'aria-label': label }
    : { 'aria-hidden': 'true', focusable: 'false' }

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
        ? motifShapes(parsed.motif).map((shape, index) => {
            const Tag = shape.type
            return (
              <Tag
                key={index}
                fill={colors.ink}
                stroke={colors.ink}
                strokeWidth={0}
                {...shape.props}
              />
            )
          })
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
    </svg>
  )
}
