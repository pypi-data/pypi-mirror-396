import { useState, useRef, useEffect, type ReactNode } from 'react'
import { cn } from '../../lib/cn'

interface DropdownMenuProps {
  trigger: ReactNode
  children: ReactNode
  align?: 'left' | 'right'
  className?: string
}

export function DropdownMenu({ trigger, children, align = 'right', className }: DropdownMenuProps) {
  const [open, setOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  // Close on click outside
  useEffect(() => {
    if (!open) return

    const handleClickOutside = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false)
      }
    }

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false)
    }

    document.addEventListener('mousedown', handleClickOutside)
    document.addEventListener('keydown', handleEscape)
    return () => {
      document.removeEventListener('mousedown', handleClickOutside)
      document.removeEventListener('keydown', handleEscape)
    }
  }, [open])

  return (
    <div className={cn('relative', className)} ref={menuRef}>
      <div onClick={() => setOpen(!open)}>{trigger}</div>
      {open && (
        <div
          className={cn(
            'absolute z-50 mt-1 min-w-[160px] py-1',
            'bg-surface-2 border border-border rounded-lg',
            'shadow-lg shadow-black/20',
            'animate-slide-in-from-top',
            align === 'right' ? 'right-0' : 'left-0'
          )}
          onClick={() => setOpen(false)}
        >
          {children}
        </div>
      )}
    </div>
  )
}

interface DropdownItemProps {
  children: ReactNode
  onClick?: () => void
  danger?: boolean
  disabled?: boolean
  className?: string
}

export function DropdownItem({ children, onClick, danger, disabled, className }: DropdownItemProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        'w-full px-3 py-2 text-left text-sm',
        'transition-colors duration-100',
        'disabled:opacity-50 disabled:cursor-not-allowed',
        danger
          ? [
              'text-status-error',
              'hover:bg-status-error-muted hover:text-status-error',
              'active:bg-status-error/20',
            ].join(' ')
          : [
              'text-text-secondary',
              'hover:bg-surface-3 hover:text-text-primary',
              'active:bg-surface',
            ].join(' '),
        className
      )}
    >
      {children}
    </button>
  )
}

export function DropdownSeparator() {
  return <div className="my-1 border-t border-border" />
}

// Convenience trigger button (three dots)
export function OverflowMenuTrigger({ className }: { className?: string }) {
  return (
    <button
      className={cn(
        'p-1.5 rounded',
        'text-text-tertiary',
        'transition-all duration-150',
        'hover:text-text-primary hover:bg-surface-3',
        'active:bg-surface-2 active:scale-95',
        className
      )}
      aria-label="More actions"
    >
      <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
        <circle cx="8" cy="3" r="1.5" />
        <circle cx="8" cy="8" r="1.5" />
        <circle cx="8" cy="13" r="1.5" />
      </svg>
    </button>
  )
}
