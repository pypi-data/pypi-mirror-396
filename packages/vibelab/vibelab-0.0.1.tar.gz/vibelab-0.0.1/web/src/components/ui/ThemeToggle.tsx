import { useEffect, useState } from 'react'
import { cn } from '../../lib/cn'

type Theme = 'light' | 'dark' | 'system'

function getSystemTheme(): 'light' | 'dark' {
  if (typeof window === 'undefined') return 'dark'
  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}

function getStoredTheme(): Theme {
  if (typeof window === 'undefined') return 'system'
  return (localStorage.getItem('vibelab-theme') as Theme) || 'system'
}

function applyTheme(theme: Theme) {
  const resolved = theme === 'system' ? getSystemTheme() : theme
  document.documentElement.setAttribute('data-theme', resolved)
}

export function ThemeToggle({ className }: { className?: string }) {
  const [theme, setTheme] = useState<Theme>('system')
  const [mounted, setMounted] = useState(false)

  // Initialize on mount
  useEffect(() => {
    const stored = getStoredTheme()
    setTheme(stored)
    applyTheme(stored)
    setMounted(true)
  }, [])

  // Listen for system theme changes
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    const handler = () => {
      if (theme === 'system') {
        applyTheme('system')
      }
    }
    mediaQuery.addEventListener('change', handler)
    return () => mediaQuery.removeEventListener('change', handler)
  }, [theme])

  const cycleTheme = () => {
    const next: Theme = theme === 'light' ? 'dark' : theme === 'dark' ? 'system' : 'light'
    setTheme(next)
    localStorage.setItem('vibelab-theme', next)
    applyTheme(next)
  }

  // Prevent hydration mismatch
  if (!mounted) {
    return (
      <button className={cn('p-2 rounded text-text-secondary', className)}>
        <span className="w-4 h-4 block" />
      </button>
    )
  }

  const icons = {
    light: '☀️',
    dark: '🌙',
    system: '💻',
  }

  const labels = {
    light: 'Light mode',
    dark: 'Dark mode',
    system: 'System theme',
  }

  return (
    <button
      onClick={cycleTheme}
      className={cn(
        'p-2 rounded text-sm flex items-center gap-1.5',
        'text-text-secondary',
        'transition-all duration-150',
        'hover:text-text-primary hover:bg-surface-3',
        'active:bg-surface-2 active:scale-95',
        className
      )}
      title={labels[theme]}
      aria-label={labels[theme]}
    >
      <span className="transition-transform duration-200 hover:scale-110">{icons[theme]}</span>
      <span className="text-xs hidden sm:inline">{theme === 'system' ? 'Auto' : theme === 'light' ? 'Light' : 'Dark'}</span>
    </button>
  )
}
