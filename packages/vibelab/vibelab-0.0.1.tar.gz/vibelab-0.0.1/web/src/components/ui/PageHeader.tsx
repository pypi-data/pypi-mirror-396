import { type ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { cn } from '../../lib/cn'

interface BreadcrumbItem {
  label: string
  path?: string
}

interface PageHeaderProps {
  breadcrumbs?: BreadcrumbItem[]
  title: string
  description?: string
  actions?: ReactNode
  className?: string
}

export function PageHeader({ breadcrumbs, title, description, actions, className }: PageHeaderProps) {
  return (
    <div className={cn('mb-6', className)}>
      {/* Always render breadcrumb container for consistent spacing */}
      <nav className="mb-3 min-h-[20px]">
        {breadcrumbs && breadcrumbs.length > 0 && (
          <ol className="flex items-center gap-1.5 text-sm">
            {breadcrumbs.map((item, index) => (
              <li key={index} className="flex items-center gap-1.5">
                {index > 0 && <span className="text-text-disabled">/</span>}
                {item.path && index < breadcrumbs.length - 1 ? (
                  <Link
                    to={item.path}
                    className="text-text-tertiary hover:text-text-secondary transition-colors"
                  >
                    {item.label}
                  </Link>
                ) : (
                  <span className={index === breadcrumbs.length - 1 ? 'text-text-secondary' : 'text-text-tertiary'}>
                    {item.label}
                  </span>
                )}
              </li>
            ))}
          </ol>
        )}
      </nav>
      <div className="flex items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-semibold text-text-primary">{title}</h1>
          {description && (
            <p className="mt-1 text-sm text-text-secondary">{description}</p>
          )}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    </div>
  )
}
