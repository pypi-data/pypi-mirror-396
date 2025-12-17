import { useQuery } from '@tanstack/react-query'
import { Link, useNavigate } from 'react-router-dom'
import { useState, useMemo } from 'react'
import { listExecutors, getHarnessDetail } from '../api'
import { PageHeader, Table, Button, EmptyState, Select, Input, Checkbox } from './ui'

interface ExecutorTuple {
  harness: string
  harnessName: string
  provider: string
  modelId: string
  modelName: string
  executorSpec: string
}

export default function Executors() {
  const navigate = useNavigate()
  const [selectedExecutors, setSelectedExecutors] = useState<Set<string>>(new Set())
  const [filterHarness, setFilterHarness] = useState<string>('')
  const [filterProvider, setFilterProvider] = useState<string>('')
  const [filterModel, setFilterModel] = useState<string>('')

  const { data: executorsData, isLoading } = useQuery({
    queryKey: ['executors'],
    queryFn: listExecutors,
  })

  const harnessIds = executorsData?.harnesses.map((h: any) => h.id) || []
  const harnessDetailsQueries = useQuery({
    queryKey: ['harness-details', harnessIds],
    queryFn: async () => {
      if (!executorsData) return []
      const details = await Promise.all(
        executorsData.harnesses.map((h: any) => getHarnessDetail(h.id))
      )
      return details
    },
    enabled: !!executorsData && harnessIds.length > 0,
  })

  const executorTuples = useMemo<ExecutorTuple[]>(() => {
    if (!executorsData || !harnessDetailsQueries.data) return []

    const tuples: ExecutorTuple[] = []
    for (let i = 0; i < executorsData.harnesses.length; i++) {
      const harness = executorsData.harnesses[i]
      const detail = harnessDetailsQueries.data[i]
      if (!detail) continue

      for (const providerDetail of detail.providers) {
        for (const model of providerDetail.models) {
          tuples.push({
            harness: harness.id,
            harnessName: harness.name,
            provider: providerDetail.id,
            modelId: model.id,
            modelName: model.name,
            executorSpec: `${harness.id}:${providerDetail.id}:${model.id}`,
          })
        }
      }
    }
    return tuples
  }, [executorsData, harnessDetailsQueries.data])

  const filteredTuples = useMemo(() => {
    return executorTuples.filter((tuple) => {
      if (filterHarness && tuple.harness !== filterHarness) return false
      if (filterProvider && tuple.provider !== filterProvider) return false
      if (filterModel && !tuple.modelId.toLowerCase().includes(filterModel.toLowerCase()) && 
          !tuple.modelName.toLowerCase().includes(filterModel.toLowerCase())) return false
      return true
    })
  }, [executorTuples, filterHarness, filterProvider, filterModel])

  const toggleExecutor = (executorSpec: string) => {
    const newSelected = new Set(selectedExecutors)
    if (newSelected.has(executorSpec)) {
      newSelected.delete(executorSpec)
    } else {
      newSelected.add(executorSpec)
    }
    setSelectedExecutors(newSelected)
  }

  const toggleAll = () => {
    if (selectedExecutors.size === filteredTuples.length) {
      setSelectedExecutors(new Set())
    } else {
      setSelectedExecutors(new Set(filteredTuples.map(t => t.executorSpec)))
    }
  }

  const handleStartRun = () => {
    if (selectedExecutors.size === 0) return
    const executorSpecs = Array.from(selectedExecutors).join(',')
    navigate(`/run/create?executors=${executorSpecs}`)
  }

  const uniqueHarnesses = useMemo(() => {
    const harnesses = new Set(executorTuples.map(t => t.harness))
    return Array.from(harnesses).map(id => {
      const tuple = executorTuples.find(t => t.harness === id)
      return { value: id, label: tuple?.harnessName || id }
    })
  }, [executorTuples])

  const uniqueProviders = useMemo(() => {
    const providers = new Set(executorTuples.map(t => t.provider))
    return Array.from(providers).map(p => ({ value: p, label: p }))
  }, [executorTuples])

  if (isLoading || harnessDetailsQueries.isLoading) {
    return (
      <div>
        <PageHeader breadcrumbs={[{ label: 'Executors' }]} title="Executors" />
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </div>
    )
  }

  return (
    <div>
      <PageHeader
        breadcrumbs={[{ label: 'Executors' }]}
        title="Executors"
        description="Available harness, provider, and model combinations"
        actions={
          <Button 
            onClick={handleStartRun}
            disabled={selectedExecutors.size === 0}
          >
            Start Run{selectedExecutors.size > 0 ? ` (${selectedExecutors.size})` : ''}
          </Button>
        }
      />

      {/* Filters */}
      <div className="bg-surface border border-border rounded-lg p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Select
            label="Harness"
            value={filterHarness}
            onChange={(e) => setFilterHarness(e.target.value)}
            options={[{ value: '', label: 'All Harnesses' }, ...uniqueHarnesses]}
          />
          <Select
            label="Provider"
            value={filterProvider}
            onChange={(e) => setFilterProvider(e.target.value)}
            options={[{ value: '', label: 'All Providers' }, ...uniqueProviders]}
          />
          <Input
            label="Model"
            value={filterModel}
            onChange={(e) => setFilterModel(e.target.value)}
            placeholder="Search models..."
          />
        </div>
      </div>

      {filteredTuples.length === 0 ? (
        <EmptyState
          title="No executors match the filters"
          description="Try adjusting your filter criteria."
        />
      ) : (
        <Table>
          <Table.Header>
            <tr>
              <Table.Head className="w-10">
                <Checkbox
                  checked={selectedExecutors.size === filteredTuples.length && filteredTuples.length > 0}
                  onChange={toggleAll}
                />
              </Table.Head>
              <Table.Head>Harness</Table.Head>
              <Table.Head>Provider</Table.Head>
              <Table.Head>Model ID</Table.Head>
              <Table.Head>Model Name</Table.Head>
              <Table.Head></Table.Head>
            </tr>
          </Table.Header>
          <Table.Body>
            {filteredTuples.map((tuple) => (
              <Table.Row
                key={tuple.executorSpec}
                selected={selectedExecutors.has(tuple.executorSpec)}
              >
                <Table.Cell>
                  <Checkbox
                    checked={selectedExecutors.has(tuple.executorSpec)}
                    onChange={() => toggleExecutor(tuple.executorSpec)}
                  />
                </Table.Cell>
                <Table.Cell>
                  <span className="text-text-primary font-medium">{tuple.harnessName}</span>
                  <span className="text-text-disabled font-mono text-xs ml-2">({tuple.harness})</span>
                </Table.Cell>
                <Table.Cell mono className="text-text-secondary text-sm">
                  {tuple.provider}
                </Table.Cell>
                <Table.Cell mono className="text-text-secondary text-sm">
                  {tuple.modelId}
                </Table.Cell>
                <Table.Cell className="text-text-tertiary text-sm">
                  {tuple.modelName}
                </Table.Cell>
                <Table.Cell>
                  <Link to={`/runs?executor=${encodeURIComponent(tuple.executorSpec)}`}>
                    <Button variant="ghost" size="sm">View Runs</Button>
                  </Link>
                </Table.Cell>
              </Table.Row>
            ))}
          </Table.Body>
        </Table>
      )}
    </div>
  )
}
