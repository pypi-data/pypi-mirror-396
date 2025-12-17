import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import { listResults, deleteResult, rerunResult } from '../api'
import { PageHeader, Table, StatusBadge, EmptyState, Button, ConfirmDialog, DropdownMenu, DropdownItem, DropdownSeparator, OverflowMenuTrigger, QualityBadge } from './ui'
import { useState } from 'react'

export default function Runs() {
  const queryClient = useQueryClient()
  const navigate = useNavigate()
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null)
  const [searchParams] = useSearchParams()
  const executorFilter = searchParams.get('executor')
  
  const { data: results, isLoading } = useQuery({
    queryKey: ['results', executorFilter || null],
    queryFn: () => listResults(executorFilter ? { executor: executorFilter } : undefined),
    // Poll every 3 seconds if any results are running/queued
    refetchInterval: (query) => {
      const data = query.state.data
      const hasRunning = data?.some(r => r.status === 'running' || r.status === 'queued')
      return hasRunning ? 3000 : false
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => deleteResult(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['results'] })
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
      setDeleteTarget(null)
    },
  })

  const rerunMutation = useMutation({
    mutationFn: (id: number) => rerunResult(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['results'] })
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
    },
  })

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatDuration = (ms: number | undefined) => {
    if (!ms) return '—'
    const seconds = Math.floor(ms / 1000)
    if (seconds < 60) return `${seconds}s`
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}m ${remainingSeconds}s`
  }

  if (isLoading) {
    return (
      <div>
        <PageHeader
          breadcrumbs={executorFilter ? [{ label: 'Executors', path: '/executors' }, { label: 'Runs' }] : [{ label: 'Runs' }]}
          title={executorFilter ? `Runs: ${executorFilter}` : 'All Runs'}
        />
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </div>
    )
  }

  const breadcrumbs = executorFilter
    ? [{ label: 'Executors', path: '/executors' }, { label: 'Runs' }]
    : [{ label: 'Runs' }]

  return (
    <div>
      <PageHeader
        breadcrumbs={breadcrumbs}
        title={executorFilter ? `Runs: ${executorFilter}` : 'All Runs'}
        description="Individual execution results across all scenarios"
        actions={
          executorFilter && (
            <Link to="/runs">
              <Button variant="ghost" size="sm">Clear Filter</Button>
            </Link>
          )
        }
      />

      {!results || results.length === 0 ? (
        <EmptyState
          title="No runs yet"
          description={executorFilter ? 'No runs found for this executor.' : 'Create a scenario and run it to see results here.'}
          action={
            <Link to="/run/create">
              <Button>Create Run</Button>
            </Link>
          }
        />
      ) : (
        <Table>
          <Table.Header>
            <tr>
              <Table.Head>ID</Table.Head>
              <Table.Head>Scenario</Table.Head>
              <Table.Head>Executor</Table.Head>
              <Table.Head>Driver</Table.Head>
              <Table.Head>Status</Table.Head>
              <Table.Head>Quality</Table.Head>
              <Table.Head>Duration</Table.Head>
              <Table.Head>Changes</Table.Head>
              <Table.Head>Cost</Table.Head>
              <Table.Head>Created</Table.Head>
              <Table.Head></Table.Head>
            </tr>
          </Table.Header>
          <Table.Body>
            {results.map((result) => (
              <Table.Row 
                key={result.id}
                className="cursor-pointer"
                onClick={() => navigate(`/result/${result.id}`)}
              >
                <Table.Cell mono className="text-text-tertiary text-xs">
                  {result.id}
                </Table.Cell>
                <Table.Cell>
                  <Link 
                    to={`/scenario/${result.scenario_id}`} 
                    className="text-accent hover:text-accent-hover text-sm"
                    onClick={(e) => e.stopPropagation()}
                  >
                    Scenario {result.scenario_id}
                  </Link>
                </Table.Cell>
                <Table.Cell mono className="text-text-secondary text-xs">
                  {result.harness}:{result.provider}:{result.model}
                </Table.Cell>
                <Table.Cell className="text-text-tertiary text-xs">
                  {result.driver || 'local'}
                </Table.Cell>
                <Table.Cell>
                  <StatusBadge status={result.status} isStale={result.is_stale} />
                </Table.Cell>
                <Table.Cell>
                  <QualityBadge quality={result.quality as 1|2|3|4|null} />
                </Table.Cell>
                <Table.Cell className="text-text-tertiary text-sm">
                  {formatDuration(result.duration_ms)}
                </Table.Cell>
                <Table.Cell className="text-sm">
                  {result.lines_added !== undefined && result.lines_removed !== undefined ? (
                    <span>
                      <span className="text-status-success">+{result.lines_added}</span>
                      <span className="text-text-tertiary">/</span>
                      <span className="text-status-error">-{result.lines_removed}</span>
                    </span>
                  ) : (
                    <span className="text-text-disabled">—</span>
                  )}
                </Table.Cell>
                <Table.Cell className="text-text-tertiary text-sm">
                  {result.cost_usd ? `$${result.cost_usd.toFixed(4)}` : '—'}
                </Table.Cell>
                <Table.Cell className="text-text-tertiary text-xs">
                  {formatDate(result.created_at)}
                </Table.Cell>
                <Table.Cell>
                  <div 
                    className="flex items-center justify-end"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <DropdownMenu trigger={<OverflowMenuTrigger />}>
                      <DropdownItem
                        onClick={() => rerunMutation.mutate(result.id)}
                        disabled={rerunMutation.isPending}
                      >
                        Rerun
                      </DropdownItem>
                      <DropdownSeparator />
                      <DropdownItem
                        danger
                        onClick={() => setDeleteTarget(result.id)}
                      >
                        Delete result
                      </DropdownItem>
                    </DropdownMenu>
                  </div>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      )}

      <ConfirmDialog
        open={deleteTarget !== null}
        onClose={() => setDeleteTarget(null)}
        onConfirm={() => {
          if (deleteTarget) {
            deleteMutation.mutate(deleteTarget)
          }
        }}
        title="Delete Result"
        description={deleteTarget ? `Are you sure you want to delete result ${deleteTarget}? This action cannot be undone.` : ''}
        confirmLabel="Delete"
        danger
        loading={deleteMutation.isPending}
      />
    </div>
  )
}
