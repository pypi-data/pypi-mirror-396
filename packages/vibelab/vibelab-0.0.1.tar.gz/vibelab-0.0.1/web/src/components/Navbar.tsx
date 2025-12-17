import { Link, useLocation } from 'react-router-dom'
import { Button, ThemeToggle } from './ui'
import { cn } from '../lib/cn'

export default function Navbar() {
  const location = useLocation()
  
  const isActive = (path: string) => {
    if (path === '/') {
      return location.pathname === '/'
    }
    return location.pathname.startsWith(path)
  }

  const navLinkClasses = (path: string) =>
    cn(
      'px-3 py-1.5 text-sm rounded transition-colors',
      isActive(path)
        ? 'bg-surface-3 text-text-primary'
        : 'text-text-tertiary hover:text-text-secondary'
    )

  return (
    <nav className="border-b border-border bg-surface">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-14">
          <div className="flex items-center gap-8">
            <Link to="/" className="text-lg font-semibold text-text-primary hover:text-accent transition-colors">
              VibeLab
            </Link>
            
            <div className="flex items-center gap-1">
              <Link to="/" className={navLinkClasses('/')}>
                Dashboard
              </Link>
              <Link to="/scenarios" className={navLinkClasses('/scenarios')}>
                Scenarios
              </Link>
              <Link to="/datasets" className={navLinkClasses('/datasets')}>
                Datasets
              </Link>
              <Link to="/runs" className={navLinkClasses('/runs')}>
                Runs
              </Link>
              <Link to="/judgements" className={navLinkClasses('/judgements')}>
                Judgements
              </Link>
              <Link to="/report" className={navLinkClasses('/report')}>
                Report
              </Link>
              <Link to="/executors" className={navLinkClasses('/executors')}>
                Executors
              </Link>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <Link to="/run/create">
              <Button size="sm">New Run</Button>
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}
