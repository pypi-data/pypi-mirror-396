import { Badge } from './Badge'

export type ResultStatus = 'pending' | 'running' | 'completed' | 'failed' | 'timeout' | 'stale'

interface StatusBadgeProps {
  status: ResultStatus | string
  isStale?: boolean
  className?: string
}

const statusConfig: Record<string, { variant: 'success' | 'error' | 'warning' | 'info' | 'stale' | 'pending'; label: string }> = {
  completed: { variant: 'success', label: 'Completed' },
  failed: { variant: 'error', label: 'Failed' },
  infra_failure: { variant: 'error', label: 'Infra Failure' },
  timeout: { variant: 'warning', label: 'Timeout' },
  running: { variant: 'info', label: 'Running' },
  pending: { variant: 'pending', label: 'Pending' },
  stale: { variant: 'stale', label: 'Stale' },
}

export function StatusBadge({ status, isStale, className }: StatusBadgeProps) {
  const effectiveStatus = isStale ? 'stale' : status
  const config = statusConfig[effectiveStatus] || statusConfig.pending

  return (
    <Badge variant={config.variant} className={className}>
      {config.label}
    </Badge>
  )
}

