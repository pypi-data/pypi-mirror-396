import { useParams, Link, useNavigate } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState, useEffect, useCallback } from 'react'
import { getDataset, addScenarioToDataset, removeScenarioFromDataset, createDatasetRun, listExecutors, getHarnessDetail, getExecutorModels, listDrivers, createScenario, createJudge, updateJudge, listJudges, ExecutorInfo } from '../api'
import { PageHeader, Card, Table, Button, EmptyState, Dialog } from './ui'
import { ScenarioForm } from './ScenarioForm'

export default function DatasetDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const [showAddScenario, setShowAddScenario] = useState(false)
  const [showRunDialog, setShowRunDialog] = useState(false)
  const [selectedScenarioId, setSelectedScenarioId] = useState<string>('')
  
  // Scenario form state
  const [codeType, setCodeType] = useState('github')
  const [codeRef, setCodeRef] = useState('')
  const [prompt, setPrompt] = useState('')
  
  // Judge settings
  const [enableJudge, setEnableJudge] = useState(false)
  const [judgeGuidance, setJudgeGuidance] = useState('')
  const [autoJudge, setAutoJudge] = useState(true)
  
  const { data, isLoading } = useQuery({
    queryKey: ['dataset', id],
    queryFn: () => getDataset(Number(id!)),
  })

  const { data: executorsData } = useQuery({
    queryKey: ['executors'],
    queryFn: listExecutors,
  })

  const { data: driversData } = useQuery({
    queryKey: ['drivers'],
    queryFn: listDrivers,
  })

  const resetFormState = () => {
    setShowAddScenario(false)
    setSelectedScenarioId('')
    setPrompt('')
    setCodeRef('')
    setCodeType('github')
    setEnableJudge(false)
    setJudgeGuidance('')
    setAutoJudge(true)
  }

  const addScenarioMutation = useMutation({
    mutationFn: async (scenarioId: number) => {
      // Add scenario to dataset
      await addScenarioToDataset(Number(id!), scenarioId)
      
      // Create/update judge if enabled
      if (enableJudge && judgeGuidance.trim()) {
        try {
          const existingJudges = await listJudges(scenarioId)
          if (existingJudges.length > 0) {
            await updateJudge(existingJudges[0].id, {
              scenario_id: scenarioId,
              guidance: judgeGuidance.trim(),
              training_sample_ids: existingJudges[0].training_sample_ids,
              test_sample_ids: existingJudges[0].test_sample_ids,
            })
          } else {
            await createJudge({
              scenario_id: scenarioId,
              guidance: judgeGuidance.trim(),
              training_sample_ids: [],
              test_sample_ids: [],
            })
          }
        } catch (error) {
          console.error('Failed to create/update judge:', error)
        }
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dataset', id] })
      queryClient.invalidateQueries({ queryKey: ['datasets'] })
      queryClient.invalidateQueries({ queryKey: ['judges'] })
      resetFormState()
    },
  })

  const createScenarioMutation = useMutation({
    mutationFn: createScenario,
    onSuccess: async (scenario) => {
      // Add scenario to dataset
      await addScenarioToDataset(Number(id!), scenario.id)
      
      // Create judge if enabled
      if (enableJudge && judgeGuidance.trim()) {
        try {
          await createJudge({
            scenario_id: scenario.id,
            guidance: judgeGuidance.trim(),
            training_sample_ids: [],
            test_sample_ids: [],
          })
        } catch (error) {
          console.error('Failed to create judge:', error)
        }
      }
      
      queryClient.invalidateQueries({ queryKey: ['dataset', id] })
      queryClient.invalidateQueries({ queryKey: ['datasets'] })
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
      queryClient.invalidateQueries({ queryKey: ['judges'] })
      resetFormState()
    },
  })

  const removeScenarioMutation = useMutation({
    mutationFn: (scenarioId: number) => removeScenarioFromDataset(Number(id!), scenarioId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dataset', id] })
      queryClient.invalidateQueries({ queryKey: ['datasets'] })
    },
  })

  const runMutation = useMutation({
    mutationFn: (data: { executor_specs: string[], trials: number, minimal: boolean, timeout_seconds: number, driver: string }) => 
      createDatasetRun({ dataset_id: Number(id!), ...data }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['dataset', id] })
      queryClient.invalidateQueries({ queryKey: ['scenarios'] })
      queryClient.invalidateQueries({ queryKey: ['dataset-analytics', id] })
      setShowRunDialog(false)
      navigate(`/dataset/${id}/analytics`)
    },
  })

  if (isLoading) {
    return (
      <div>
        <PageHeader
          breadcrumbs={[{ label: 'Datasets', path: '/datasets' }, { label: `Dataset ${id}` }]}
          title={`Dataset ${id}`}
        />
        <div className="text-center py-12 text-text-tertiary">Loading...</div>
      </div>
    )
  }

  if (!data) {
    return (
      <div>
        <PageHeader
          breadcrumbs={[{ label: 'Datasets', path: '/datasets' }, { label: 'Not Found' }]}
          title="Dataset Not Found"
        />
        <EmptyState title="Dataset not found" description="The dataset you're looking for doesn't exist." />
      </div>
    )
  }

  const { dataset, scenarios } = data

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const getCodeRefDisplay = (scenario: any) => {
    if (!scenario.code_ref) return '—'
    if (scenario.code_type === 'github') {
      return `${scenario.code_ref.owner}/${scenario.code_ref.repo}`
    } else if (scenario.code_type === 'local') {
      return scenario.code_ref.path
    }
    return '—'
  }

  const handleAddScenario = () => {
    if (selectedScenarioId) {
      // Add existing scenario
      addScenarioMutation.mutate(Number(selectedScenarioId))
    } else {
      // Create new scenario from form data
      let code_ref: any = null
      if (codeType === 'github') {
        const [owner, repo] = codeRef.split('/')
        const parts = repo.split('@')
        code_ref = { owner, repo: parts[0], commit_sha: parts[1] || 'main' }
      } else if (codeType === 'local') {
        code_ref = { path: codeRef }
      }

      createScenarioMutation.mutate({
        code_type: codeType,
        code_ref,
        prompt,
      })
    }
  }

  const handleRemoveScenario = (scenarioId: number) => {
    removeScenarioMutation.mutate(scenarioId)
  }

  const datasetScenarioIds = scenarios.map(s => s.id)

  return (
    <div>
      <PageHeader
        breadcrumbs={[{ label: 'Datasets', path: '/datasets' }, { label: dataset.name }]}
        title={dataset.name}
        description={dataset.description}
        actions={
          <div className="flex gap-2">
            <Button onClick={() => setShowRunDialog(true)}>Run Dataset</Button>
            <Link to={`/dataset/${id}/analytics`}>
              <Button variant="secondary">View Analytics</Button>
            </Link>
          </div>
        }
      />

      <div className="mt-6 space-y-6">
        <Card>
          <Card.Header>
            <div className="flex items-center justify-between">
              <Card.Title>Scenarios ({scenarios.length})</Card.Title>
              <Button size="sm" onClick={() => setShowAddScenario(true)}>
                Add Scenario
              </Button>
            </div>
          </Card.Header>
          <Card.Content>
            {scenarios.length === 0 ? (
              <EmptyState
                title="No scenarios in dataset"
                description="Add scenarios to this dataset to get started."
                action={
                  <Button onClick={() => setShowAddScenario(true)}>Add Scenario</Button>
                }
              />
            ) : (
              <Table>
                <Table.Header>
                  <tr>
                    <Table.Head>ID</Table.Head>
                    <Table.Head>Prompt</Table.Head>
                    <Table.Head>Type</Table.Head>
                    <Table.Head>Code Reference</Table.Head>
                    <Table.Head>Created</Table.Head>
                    <Table.Head></Table.Head>
                  </tr>
                </Table.Header>
                <Table.Body>
                  {scenarios.map((scenario) => (
                    <Table.Row key={scenario.id}>
                      <Table.Cell mono className="text-text-tertiary text-xs">
                        {scenario.id}
                      </Table.Cell>
                      <Table.Cell>
                        <div className="max-w-md">
                          <Link to={`/scenario/${scenario.id}`} className="text-text-primary hover:text-accent">
                            {scenario.prompt.length > 80
                              ? `${scenario.prompt.substring(0, 80)}...`
                              : scenario.prompt}
                          </Link>
                        </div>
                      </Table.Cell>
                      <Table.Cell className="text-text-tertiary capitalize">
                        {scenario.code_type}
                      </Table.Cell>
                      <Table.Cell mono className="text-text-tertiary text-xs">
                        {getCodeRefDisplay(scenario)}
                      </Table.Cell>
                      <Table.Cell className="text-text-tertiary text-xs">
                        {formatDate(scenario.created_at)}
                      </Table.Cell>
                      <Table.Cell>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleRemoveScenario(scenario.id)}
                        >
                          Remove
                        </Button>
                      </Table.Cell>
                    </Table.Row>
                  ))}
                </Table.Body>
              </Table>
            )}
          </Card.Content>
        </Card>
      </div>

      {/* Add Scenario Dialog */}
      <Dialog open={showAddScenario} onClose={resetFormState}>
        <Dialog.Header>
          <Dialog.Title>Add Scenario to Dataset</Dialog.Title>
        </Dialog.Header>
        <Dialog.Content>
          <ScenarioForm
            selectedScenarioId={selectedScenarioId}
            onScenarioIdChange={setSelectedScenarioId}
            codeType={codeType}
            onCodeTypeChange={setCodeType}
            codeRef={codeRef}
            onCodeRefChange={setCodeRef}
            prompt={prompt}
            onPromptChange={setPrompt}
            showLoadFromExisting={true}
            excludeScenarioIds={datasetScenarioIds}
            // Judge settings
            showJudgeSettings={true}
            enableJudge={enableJudge}
            onEnableJudgeChange={setEnableJudge}
            judgeGuidance={judgeGuidance}
            onJudgeGuidanceChange={setJudgeGuidance}
            autoJudge={autoJudge}
            onAutoJudgeChange={setAutoJudge}
          />
        </Dialog.Content>
        <Dialog.Footer>
          <Button variant="ghost" onClick={resetFormState}>
            Cancel
          </Button>
          <Button
            onClick={handleAddScenario}
            disabled={
              (!selectedScenarioId && !prompt.trim()) ||
              addScenarioMutation.isPending ||
              createScenarioMutation.isPending
            }
          >
            {selectedScenarioId
              ? (addScenarioMutation.isPending ? 'Adding...' : 'Add')
              : (createScenarioMutation.isPending ? 'Creating...' : 'Create & Add')
            }
          </Button>
        </Dialog.Footer>
      </Dialog>

      {/* Run Dataset Dialog */}
      <DatasetRunDialog
        open={showRunDialog}
        onClose={() => setShowRunDialog(false)}
        onSubmit={(data) => runMutation.mutate(data)}
        isLoading={runMutation.isPending}
        executorsData={executorsData}
        driversData={driversData}
      />
    </div>
  )
}

interface DatasetRunDialogProps {
  open: boolean
  onClose: () => void
  onSubmit: (data: { executor_specs: string[], trials: number, minimal: boolean, timeout_seconds: number, driver: string }) => void
  isLoading: boolean
  executorsData?: { harnesses: ExecutorInfo[] }
  driversData?: { drivers: any[] }
}

function DatasetRunDialog({ open, onClose, onSubmit, isLoading, executorsData, driversData }: DatasetRunDialogProps) {
  const [executors, setExecutors] = useState<string[]>([''])
  const [trials, setTrials] = useState(1)
  const [minimal, setMinimal] = useState(false)
  const [timeout, setTimeout] = useState(1800)
  const [driver, setDriver] = useState('local')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const validExecutors = executors.filter(e => e.trim())
    if (validExecutors.length === 0) return
    
    onSubmit({
      executor_specs: validExecutors,
      trials,
      minimal,
      timeout_seconds: timeout,
      driver,
    })
  }

  return (
    <Dialog open={open} onClose={onClose}>
      <Dialog.Header>
        <Dialog.Title>Run Dataset</Dialog.Title>
      </Dialog.Header>
      <form onSubmit={handleSubmit}>
        <Dialog.Content>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-text-secondary mb-1.5">Executors</label>
              {executors.map((executor, idx) => (
                <ExecutorSelector
                  key={idx}
                  index={idx}
                  value={executor}
                  executorsData={executorsData}
                  onExecutorChange={setExecutors}
                  canRemove={executors.length > 1}
                />
              ))}
              <button
                type="button"
                onClick={() => setExecutors([...executors, ''])}
                className="text-sm text-accent hover:text-accent-hover mt-2"
              >
                + Add Executor
              </button>
            </div>

            <div>
              <label className="block text-sm text-text-secondary mb-1.5">Trials</label>
              <input
                type="number"
                value={trials}
                onChange={(e) => setTrials(Number(e.target.value))}
                min="1"
                className="w-full px-3 py-2 bg-surface border border-border rounded text-sm text-text-primary focus:outline-none focus:border-border-focus focus:ring-1 focus:ring-border-focus"
              />
              <p className="mt-1 text-xs text-text-tertiary">Number of runs per scenario-executor pair</p>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="minimal"
                checked={minimal}
                onChange={(e) => setMinimal(e.target.checked)}
                className="w-4 h-4"
              />
              <label htmlFor="minimal" className="text-sm text-text-secondary">
                Minimal mode (only run missing scenario-executor pairs)
              </label>
            </div>

            <div>
              <label className="block text-sm text-text-secondary mb-1.5">Timeout (seconds)</label>
              <input
                type="number"
                value={timeout}
                onChange={(e) => setTimeout(Number(e.target.value))}
                min="1"
                className="w-full px-3 py-2 bg-surface border border-border rounded text-sm text-text-primary focus:outline-none focus:border-border-focus focus:ring-1 focus:ring-border-focus"
              />
            </div>

            <div>
              <label className="block text-sm text-text-secondary mb-1.5">Driver</label>
              <select
                value={driver}
                onChange={(e) => setDriver(e.target.value)}
                className="w-full px-3 py-2 bg-surface border border-border rounded text-sm text-text-primary focus:outline-none focus:border-border-focus focus:ring-1 focus:ring-border-focus"
              >
                {(driversData?.drivers || []).map(d => (
                  <option key={d.id} value={d.id}>{d.name}</option>
                ))}
              </select>
            </div>
          </div>
        </Dialog.Content>
        <Dialog.Footer>
          <Button type="button" variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading || executors.filter(e => e.trim()).length === 0}>
            {isLoading ? 'Running...' : 'Run Dataset'}
          </Button>
        </Dialog.Footer>
      </form>
    </Dialog>
  )
}

interface ExecutorSelectorProps {
  index: number
  value: string
  executorsData: { harnesses: ExecutorInfo[] } | undefined
  onExecutorChange: React.Dispatch<React.SetStateAction<string[]>>
  canRemove: boolean
}

function ExecutorSelector({ index, value, executorsData, onExecutorChange, canRemove }: ExecutorSelectorProps) {
  const [harness, setHarness] = useState('')
  const [provider, setProvider] = useState('')
  const [model, setModel] = useState('')

  // Parse initial value
  useEffect(() => {
    if (value) {
      const parts = value.split(':')
      if (parts.length >= 3) {
        setHarness(parts[0])
        setProvider(parts[1])
        setModel(parts[2])
      }
    }
  }, [value])

  // Load harness details to get providers and models
  const { data: harnessDetailData } = useQuery({
    queryKey: ['harness-detail', harness],
    queryFn: () => getHarnessDetail(harness),
    enabled: !!harness,
  })

  // Auto-select first provider when harness is selected
  useEffect(() => {
    if (harness && harnessDetailData && !provider) {
      const firstProvider = harnessDetailData.providers[0]
      if (firstProvider) {
        setProvider(firstProvider.id)
      }
    }
  }, [harness, harnessDetailData, provider])

  // Load models for selected harness/provider
  const { data: modelsData } = useQuery({
    queryKey: ['executor-models', harness, provider],
    queryFn: () => getExecutorModels(harness, provider),
    enabled: !!harness && !!provider,
  })

  // Auto-select first model when provider is selected
  useEffect(() => {
    if (provider && modelsData?.models && modelsData.models.length > 0 && !model) {
      const firstModel = modelsData.models[0]
      if (firstModel) {
        setModel(firstModel.id)
      }
    }
  }, [provider, modelsData, model])

  // Stable callback to update parent
  const updateParent = useCallback((newValue: string) => {
    onExecutorChange(prev => {
      const newExecutors = [...prev]
      newExecutors[index] = newValue
      return newExecutors
    })
  }, [index, onExecutorChange])

  // Sync local state to parent - compare before calling to prevent infinite loops
  useEffect(() => {
    const newValue = harness && provider && model ? `${harness}:${provider}:${model}` : ''
    if (newValue !== value) {
      updateParent(newValue)
    }
  }, [harness, provider, model, value, updateParent])

  const handleRemove = useCallback(() => {
    onExecutorChange(prev => prev.filter((_, i) => i !== index))
  }, [index, onExecutorChange])

  const selectedProviderModels = modelsData?.models || []

  return (
    <div className="flex gap-2 items-end mb-2">
      <div className="flex-1">
        <label className="block mb-1 text-xs text-text-tertiary">Harness</label>
        <select
          value={harness}
          onChange={(e) => {
            setHarness(e.target.value)
            setProvider('')
            setModel('')
          }}
          className="w-full px-3 py-2 bg-surface border border-border rounded text-sm text-text-primary focus:outline-none focus:border-border-focus focus:ring-1 focus:ring-border-focus"
        >
          <option value="">Select...</option>
          {executorsData?.harnesses.map((h) => (
            <option key={h.id} value={h.id}>
              {h.name}
            </option>
          ))}
        </select>
      </div>

      {harness && (
        <div className="flex-1">
          <label className="block mb-1 text-xs text-text-tertiary">Provider</label>
          <select
            value={provider}
            onChange={(e) => {
              setProvider(e.target.value)
              setModel('')
            }}
            className="w-full px-3 py-2 bg-surface border border-border rounded text-sm text-text-primary focus:outline-none focus:border-border-focus focus:ring-1 focus:ring-border-focus"
          >
            <option value="">Select...</option>
            {harnessDetailData?.providers.map((p) => (
              <option key={p.id} value={p.id}>
                {p.id}
              </option>
            ))}
          </select>
        </div>
      )}

      {provider && (
        <div className="flex-1">
          <label className="block mb-1 text-xs text-text-tertiary">Model</label>
          <select
            value={model}
            onChange={(e) => setModel(e.target.value)}
            className="w-full px-3 py-2 bg-surface border border-border rounded text-sm text-text-primary focus:outline-none focus:border-border-focus focus:ring-1 focus:ring-border-focus"
          >
            <option value="">Select...</option>
            {selectedProviderModels.map((m: any) => (
              <option key={m.id} value={m.id}>
                {m.name}
              </option>
            ))}
          </select>
        </div>
      )}

      {canRemove && (
        <Button
          type="button"
          variant="ghost"
          size="sm"
          onClick={handleRemove}
          className="text-status-error hover:text-status-error"
        >
          Remove
        </Button>
      )}
    </div>
  )
}
