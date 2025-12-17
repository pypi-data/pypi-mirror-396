import { type ReactNode } from 'react'
import { cn } from '../../lib/cn'

interface CardProps {
  children: ReactNode
  className?: string
  interactive?: boolean
  onClick?: () => void
}

export function Card({ children, className, interactive, onClick }: CardProps) {
  return (
    <div
      className={cn(
        'bg-surface border border-border rounded-lg',
        'transition-all duration-150',
        interactive && [
          'cursor-pointer',
          'hover:border-text-tertiary hover:shadow-md hover:shadow-black/10',
          'active:shadow-sm active:scale-[0.99]',
        ],
        className
      )}
      onClick={onClick}
    >
      {children}
    </div>
  )
}

interface CardHeaderProps {
  children: ReactNode
  className?: string
}

Card.Header = function CardHeader({ children, className }: CardHeaderProps) {
  return (
    <div className={cn('px-4 py-3 border-b border-border', className)}>
      {children}
    </div>
  )
}

interface CardTitleProps {
  children: ReactNode
  className?: string
}

Card.Title = function CardTitle({ children, className }: CardTitleProps) {
  return (
    <h3 className={cn('text-sm font-semibold text-text-primary', className)}>
      {children}
    </h3>
  )
}

interface CardContentProps {
  children: ReactNode
  className?: string
}

Card.Content = function CardContent({ children, className }: CardContentProps) {
  return (
    <div className={cn('px-4 py-3', className)}>
      {children}
    </div>
  )
}
