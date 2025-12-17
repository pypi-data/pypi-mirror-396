import { type ReactNode, useEffect } from 'react'
import { cn } from '../../lib/cn'

interface DialogProps {
  open: boolean
  onClose: () => void
  children: ReactNode
  className?: string
}

export function Dialog({ open, onClose, children, className }: DialogProps) {
  // Close on escape key
  useEffect(() => {
    if (!open) return

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [open, onClose])

  // Prevent body scroll when open
  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden'
    } else {
      document.body.style.overflow = ''
    }
    return () => {
      document.body.style.overflow = ''
    }
  }, [open])

  if (!open) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60"
        onClick={onClose}
        aria-hidden="true"
      />
      {/* Dialog content */}
      <div
        className={cn(
          'relative bg-surface-2 border border-border rounded-lg shadow-xl max-w-md w-full mx-4',
          className
        )}
        role="dialog"
        aria-modal="true"
      >
        {children}
      </div>
    </div>
  )
}

interface DialogHeaderProps {
  children: ReactNode
  className?: string
}

Dialog.Header = function DialogHeader({ children, className }: DialogHeaderProps) {
  return (
    <div className={cn('px-5 pt-5 pb-3', className)}>
      {children}
    </div>
  )
}

interface DialogTitleProps {
  children: ReactNode
  className?: string
}

Dialog.Title = function DialogTitle({ children, className }: DialogTitleProps) {
  return (
    <h2 className={cn('text-lg font-semibold text-text-primary', className)}>
      {children}
    </h2>
  )
}

interface DialogDescriptionProps {
  children: ReactNode
  className?: string
}

Dialog.Description = function DialogDescription({ children, className }: DialogDescriptionProps) {
  return (
    <p className={cn('mt-2 text-sm text-text-secondary', className)}>
      {children}
    </p>
  )
}

interface DialogContentProps {
  children: ReactNode
  className?: string
}

Dialog.Content = function DialogContent({ children, className }: DialogContentProps) {
  return (
    <div className={cn('px-5 py-3', className)}>
      {children}
    </div>
  )
}

interface DialogFooterProps {
  children: ReactNode
  className?: string
}

Dialog.Footer = function DialogFooter({ children, className }: DialogFooterProps) {
  return (
    <div className={cn('px-5 pb-5 pt-3 flex justify-end gap-2', className)}>
      {children}
    </div>
  )
}

