import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '../../lib/cn'

const badgeVariants = cva(
  'inline-flex items-center font-medium',
  {
    variants: {
      variant: {
        default: 'bg-surface-3 text-text-secondary',
        success: 'bg-status-success-muted text-status-success',
        error: 'bg-status-error-muted text-status-error',
        warning: 'bg-status-warning-muted text-status-warning',
        info: 'bg-status-info-muted text-status-info',
        stale: 'bg-status-stale-muted text-status-stale',
        pending: 'bg-status-pending-muted text-text-tertiary',
      },
      size: {
        sm: 'px-1.5 py-0.5 text-xs rounded-sm',
        md: 'px-2 py-0.5 text-xs rounded',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLSpanElement>,
    VariantProps<typeof badgeVariants> {}

export function Badge({ className, variant, size, ...props }: BadgeProps) {
  return (
    <span className={cn(badgeVariants({ variant, size, className }))} {...props} />
  )
}
