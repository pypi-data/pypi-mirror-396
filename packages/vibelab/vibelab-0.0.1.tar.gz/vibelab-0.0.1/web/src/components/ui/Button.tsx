import { forwardRef, type ButtonHTMLAttributes } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '../../lib/cn'

const buttonVariants = cva(
  // Base styles with interaction states
  [
    'inline-flex items-center justify-center font-medium',
    'transition-all duration-150',
    'focus-ring',
    'disabled:opacity-50 disabled:pointer-events-none disabled:cursor-not-allowed',
    // Active/pressed state - scale down slightly
    'active:scale-[0.97]',
  ].join(' '),
  {
    variants: {
      variant: {
        primary: [
          'bg-accent text-on-accent',
          'hover:bg-accent-hover hover:shadow-md hover:shadow-accent/20',
          'active:bg-accent active:shadow-sm',
        ].join(' '),
        secondary: [
          'bg-surface-2 text-text-primary border border-border',
          'hover:bg-surface-3 hover:border-text-tertiary hover:shadow-sm',
          'active:bg-surface active:shadow-none',
        ].join(' '),
        ghost: [
          'text-text-secondary',
          'hover:text-text-primary hover:bg-surface-3',
          'active:bg-surface-2',
        ].join(' '),
        danger: [
          'bg-status-error text-white',
          'hover:bg-red-600 hover:shadow-md hover:shadow-status-error/20',
          'active:bg-red-700 active:shadow-sm',
        ].join(' '),
        success: [
          'bg-status-success text-white',
          'hover:bg-green-600 hover:shadow-md hover:shadow-status-success/20',
          'active:bg-green-700 active:shadow-sm',
        ].join(' '),
        link: [
          'text-accent underline-offset-4',
          'hover:text-accent-hover hover:underline',
          'active:text-accent',
        ].join(' '),
      },
      size: {
        sm: 'h-7 px-2.5 text-xs rounded-sm gap-1',
        md: 'h-8 px-3 text-sm rounded gap-1.5',
        lg: 'h-9 px-4 text-sm rounded gap-2',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
)

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)

Button.displayName = 'Button'
