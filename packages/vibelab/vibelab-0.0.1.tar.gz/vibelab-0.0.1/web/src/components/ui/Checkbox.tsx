import { forwardRef, type InputHTMLAttributes } from 'react'
import { cn } from '../../lib/cn'

export interface CheckboxProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string
}

export const Checkbox = forwardRef<HTMLInputElement, CheckboxProps>(
  ({ className, label, id, ...props }, ref) => {
    const checkboxId = id || label?.toLowerCase().replace(/\s+/g, '-')

    const checkbox = (
      <input
        type="checkbox"
        id={checkboxId}
        className={cn(
          'h-4 w-4 rounded cursor-pointer',
          'bg-surface border-2 border-border',
          'transition-all duration-150',
          // Hover
          'hover:border-text-tertiary hover:bg-surface-2',
          // Checked state
          'checked:bg-accent checked:border-accent',
          'checked:hover:bg-accent-hover checked:hover:border-accent-hover',
          // Focus
          'focus:ring-2 focus:ring-accent/30 focus:ring-offset-0 focus:ring-offset-canvas',
          // Active/pressed
          'active:scale-90',
          className
        )}
        ref={ref}
        {...props}
      />
    )

    if (label) {
      return (
        <label htmlFor={checkboxId} className="flex items-center gap-2 cursor-pointer group">
          {checkbox}
          <span className="text-sm text-text-secondary group-hover:text-text-primary transition-colors">
            {label}
          </span>
        </label>
      )
    }

    return checkbox
  }
)

Checkbox.displayName = 'Checkbox'
