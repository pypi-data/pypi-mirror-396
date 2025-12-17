import { forwardRef, type TextareaHTMLAttributes } from 'react'
import { cn } from '../../lib/cn'

export interface TextareaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string
  error?: string
  mono?: boolean
}

export const Textarea = forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, label, error, id, mono, ...props }, ref) => {
    const textareaId = id || label?.toLowerCase().replace(/\s+/g, '-')

    return (
      <div className="space-y-1.5">
        {label && (
          <label htmlFor={textareaId} className="block text-sm text-text-secondary">
            {label}
          </label>
        )}
        <textarea
          id={textareaId}
          className={cn(
            'w-full px-3 py-2 rounded text-sm',
            'bg-surface border border-border',
            'text-text-primary placeholder:text-text-tertiary',
            'transition-all duration-150',
            'resize-y min-h-[80px]',
            // Hover
            'hover:border-text-tertiary hover:bg-surface-2',
            // Focus
            'focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20 focus:bg-surface',
            // Disabled
            'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-surface disabled:hover:border-border',
            // Error state
            error && 'border-status-error focus:border-status-error focus:ring-status-error/20 hover:border-status-error',
            mono && 'font-mono',
            className
          )}
          ref={ref}
          {...props}
        />
        {error && (
          <p className="text-xs text-status-error">{error}</p>
        )}
      </div>
    )
  }
)

Textarea.displayName = 'Textarea'
