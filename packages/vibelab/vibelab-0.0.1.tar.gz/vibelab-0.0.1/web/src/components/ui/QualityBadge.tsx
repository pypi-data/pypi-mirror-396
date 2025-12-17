import { cn } from '../../lib/cn'

type Quality = 1 | 2 | 3 | 4 | null | undefined

interface QualityBadgeProps {
  quality: Quality
  size?: 'sm' | 'md'
  showLabel?: boolean
  className?: string
}

const qualityConfig = {
  4: { label: 'Perfect', color: 'bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30', icon: '★' },
  3: { label: 'Good', color: 'bg-sky-500/15 text-sky-600 dark:text-sky-400 border-sky-500/30', icon: '●' },
  2: { label: 'Workable', color: 'bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30', icon: '◐' },
  1: { label: 'Bad', color: 'bg-rose-500/15 text-rose-600 dark:text-rose-400 border-rose-500/30', icon: '✗' },
} as const

export function QualityBadge({ quality, size = 'sm', showLabel = true, className }: QualityBadgeProps) {
  if (quality === null || quality === undefined) {
    return (
      <span className={cn(
        'inline-flex items-center gap-1 rounded border',
        'bg-surface-2 text-text-disabled border-border-muted',
        size === 'sm' ? 'px-1.5 py-0.5 text-xs' : 'px-2 py-1 text-sm',
        className
      )}>
        <span className="opacity-50">—</span>
        {showLabel && <span>Unrated</span>}
      </span>
    )
  }

  const config = qualityConfig[quality as 1 | 2 | 3 | 4]
  
  return (
    <span className={cn(
      'inline-flex items-center gap-1 rounded border font-medium',
      config.color,
      size === 'sm' ? 'px-1.5 py-0.5 text-xs' : 'px-2 py-1 text-sm',
      className
    )}>
      <span>{config.icon}</span>
      {showLabel && <span>{config.label}</span>}
    </span>
  )
}

// Compact numeric display for tables
export function QualityScore({ quality, className }: { quality: Quality; className?: string }) {
  if (quality === null || quality === undefined) {
    return <span className={cn('text-text-disabled', className)}>—</span>
  }

  const config = qualityConfig[quality as 1 | 2 | 3 | 4]
  
  return (
    <span className={cn('font-medium', className)} title={config.label}>
      <span className={config.color.split(' ')[1]}>{config.icon}</span>
      <span className="ml-1 text-text-secondary">{quality}</span>
    </span>
  )
}

// Helper to get quality label
export function getQualityLabel(quality: Quality): string {
  if (quality === null || quality === undefined) return 'Unrated'
  return qualityConfig[quality as 1 | 2 | 3 | 4]?.label || 'Unknown'
}

// Helper to get quality color class
export function getQualityColor(quality: Quality): string {
  if (quality === null || quality === undefined) return 'text-text-disabled'
  const config = qualityConfig[quality as 1 | 2 | 3 | 4]
  // Extract just the text color class
  const match = config.color.match(/text-[\w-]+/)
  return match ? match[0] : 'text-text-primary'
}

