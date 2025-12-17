import { forwardRef, type SelectHTMLAttributes } from 'react'
import { cn } from '../../lib/cn'

export interface SelectProps extends SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
  options?: Array<{ value: string; label: string }>
}

export const Select = forwardRef<HTMLSelectElement, SelectProps>(
  ({ className, label, error, id, options, children, ...props }, ref) => {
    const selectId = id || label?.toLowerCase().replace(/\s+/g, '-')

    return (
      <div className="space-y-1.5">
        {label && (
          <label htmlFor={selectId} className="block text-sm text-text-secondary">
            {label}
          </label>
        )}
        <select
          id={selectId}
          className={cn(
            'w-full px-3 py-2 rounded text-sm',
            'bg-surface border border-border',
            'text-text-primary',
            'transition-all duration-150 cursor-pointer',
            // Hover
            'hover:border-text-tertiary hover:bg-surface-2',
            // Focus
            'focus:outline-none focus:border-accent focus:ring-2 focus:ring-accent/20 focus:bg-surface',
            // Disabled
            'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-surface disabled:hover:border-border',
            // Error state
            error && 'border-status-error focus:border-status-error focus:ring-status-error/20 hover:border-status-error',
            className
          )}
          ref={ref}
          {...props}
        >
          {options
            ? options.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))
            : children}
        </select>
        {error && (
          <p className="text-xs text-status-error">{error}</p>
        )}
      </div>
    )
  }
)

Select.displayName = 'Select'
