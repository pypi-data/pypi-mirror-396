import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Dialog, Button, Textarea, Select, Card, Checkbox, QualityBadge } from './ui'
import { listJudges, createJudge, updateJudge, trainJudge, Result } from '../api'

interface JudgeFormProps {
  scenarioId: number
  results: Result[]
  open: boolean
  onClose: () => void
}

export default function JudgeForm({ scenarioId, results, open, onClose }: JudgeFormProps) {
  const queryClient = useQueryClient()
  const [guidance, setGuidance] = useState('')
  const [trainingSampleIds, setTrainingSampleIds] = useState<Set<number>>(new Set())
  const [testSampleIds, setTestSampleIds] = useState<Set<number>>(new Set())
  const [judgeProvider, setJudgeProvider] = useState('anthropic')
  const [judgeModel, setJudgeModel] = useState('claude-sonnet-4-20250514')

  // Get existing judge for this scenario
  const { data: existingJudge } = useQuery({
    queryKey: ['judges', scenarioId],
    queryFn: () => listJudges(scenarioId),
    enabled: open,
    select: (judges) => judges[0], // Get latest judge
  })

  // Load existing judge data if available
  useEffect(() => {
    if (existingJudge && open) {
      setGuidance(existingJudge.guidance)
      setTrainingSampleIds(new Set(existingJudge.training_sample_ids))
      setTestSampleIds(new Set(existingJudge.test_sample_ids))
    } else if (open) {
      // Reset form for new judge
      setGuidance('')
      setTrainingSampleIds(new Set())
      setTestSampleIds(new Set())
    }
  }, [existingJudge, open])

  const createMutation = useMutation({
    mutationFn: (data: { guidance: string, training_sample_ids: number[], test_sample_ids: number[] }) => {
      if (existingJudge) {
        return updateJudge(existingJudge.id, { scenario_id: scenarioId, ...data })
      }
      return createJudge({ scenario_id: scenarioId, ...data })
    },
    onSuccess: (judge) => {
      queryClient.invalidateQueries({ queryKey: ['judges', scenarioId] })
      queryClient.invalidateQueries({ queryKey: ['scenario-judgements', scenarioId] })
      // Auto-train if there are test samples
      if (judge.test_sample_ids.length > 0) {
        trainMutation.mutate({ judgeId: judge.id })
      } else {
        onClose()
      }
    },
  })

  const trainMutation = useMutation({
    mutationFn: ({ judgeId }: { judgeId: number }) =>
      trainJudge(judgeId, judgeProvider, judgeModel),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['judges', scenarioId] })
      queryClient.invalidateQueries({ queryKey: ['scenario-judgements', scenarioId] })
      onClose()
    },
  })

  const [formError, setFormError] = useState<string | null>(null)

  const handleSubmit = () => {
    setFormError(null)
    
    if (!guidance.trim()) {
      setFormError('Please provide guidance for the judge')
      return
    }

    if (trainingSampleIds.size === 0) {
      setFormError('Please select at least one training sample')
      return
    }

    createMutation.mutate({
      guidance,
      training_sample_ids: Array.from(trainingSampleIds),
      test_sample_ids: Array.from(testSampleIds),
    })
  }

  const toggleTrainingSample = (resultId: number) => {
    const newSet = new Set(trainingSampleIds)
    if (newSet.has(resultId)) {
      newSet.delete(resultId)
      // Also remove from test samples if it was there
      const newTestSet = new Set(testSampleIds)
      newTestSet.delete(resultId)
      setTestSampleIds(newTestSet)
    } else {
      newSet.add(resultId)
    }
    setTrainingSampleIds(newSet)
  }

  const toggleTestSample = (resultId: number) => {
    const newSet = new Set(testSampleIds)
    if (newSet.has(resultId)) {
      newSet.delete(resultId)
    } else {
      // Can't be both training and test
      const newTrainingSet = new Set(trainingSampleIds)
      newTrainingSet.delete(resultId)
      setTrainingSampleIds(newTrainingSet)
      newSet.add(resultId)
    }
    setTestSampleIds(newSet)
  }

  // Filter to only completed results with human scores
  const scorableResults = results.filter(r => 
    r.status === 'completed' && (r.quality !== null && r.quality !== undefined)
  )

  return (
    <Dialog open={open} onClose={onClose}>
      <Dialog.Header>
        <Dialog.Title>{existingJudge ? 'Update Judge' : 'Create Judge'}</Dialog.Title>
      </Dialog.Header>
      <Dialog.Content>
        <div className="space-y-4">
        <Textarea
          label="Guidance"
          value={guidance}
          onChange={(e) => setGuidance(e.target.value)}
          placeholder="Provide guidance for the judge on how to evaluate results. This will be used as the system prompt along with few-shot examples."
          rows={6}
        />

        <div>
          <label className="block text-sm text-text-secondary mb-2">
            Judge Provider & Model
          </label>
          <div className="grid grid-cols-2 gap-2">
            <Select
              value={judgeProvider}
              onChange={(e) => setJudgeProvider(e.target.value)}
              options={[
                { value: 'anthropic', label: 'Anthropic' },
                { value: 'openai', label: 'OpenAI' },
              ]}
            />
            <Select
              value={judgeModel}
              onChange={(e) => setJudgeModel(e.target.value)}
              options={
                judgeProvider === 'anthropic'
                  ? [
                      { value: 'claude-sonnet-4-20250514', label: 'Claude Sonnet 4' },
                      { value: 'claude-opus-4-20250514', label: 'Claude Opus 4' },
                    ]
                  : [
                      { value: 'gpt-4o', label: 'GPT-4o' },
                      { value: 'gpt-4-turbo', label: 'GPT-4 Turbo' },
                    ]
              }
            />
          </div>
        </div>

        {scorableResults.length === 0 ? (
          <Card className="border-status-warning/30 bg-status-warning-muted">
            <Card.Content className="pt-4">
              <p className="text-sm text-text-secondary">
                No results with human quality scores found. Please score some results first before creating a judge.
              </p>
            </Card.Content>
          </Card>
        ) : (
          <>
            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Training Samples (Few-shot Examples)
                <span className="ml-2 text-xs font-normal text-text-tertiary">
                  {trainingSampleIds.size} selected
                </span>
              </label>
              <div className="max-h-52 overflow-y-auto border border-border rounded-lg bg-surface divide-y divide-border-muted">
                {scorableResults.map((result) => (
                  <div
                    key={result.id}
                    onClick={() => toggleTrainingSample(result.id)}
                    className="flex items-center gap-3 p-3 hover:bg-surface-2 cursor-pointer transition-colors"
                  >
                    <Checkbox
                      checked={trainingSampleIds.has(result.id)}
                      onChange={() => toggleTrainingSample(result.id)}
                    />
                    <div className="flex-1 min-w-0">
                      <div className="text-sm text-text-primary">
                        Result {result.id}
                      </div>
                      <div className="text-xs text-text-tertiary font-mono truncate">
                        {result.harness}:{result.provider}:{result.model}
                      </div>
                    </div>
                    <QualityBadge quality={result.quality as 1|2|3|4|null} size="sm" />
                  </div>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-text-secondary mb-2">
                Test Samples (For Alignment)
                <span className="ml-2 text-xs font-normal text-text-tertiary">
                  {testSampleIds.size} selected
                </span>
              </label>
              <div className="max-h-52 overflow-y-auto border border-border rounded-lg bg-surface divide-y divide-border-muted">
                {scorableResults.map((result) => {
                  const isDisabled = trainingSampleIds.has(result.id)
                  return (
                    <div
                      key={result.id}
                      onClick={() => !isDisabled && toggleTestSample(result.id)}
                      className={`flex items-center gap-3 p-3 transition-colors ${
                        isDisabled 
                          ? 'opacity-50 cursor-not-allowed bg-surface-2' 
                          : 'hover:bg-surface-2 cursor-pointer'
                      }`}
                    >
                      <Checkbox
                        checked={testSampleIds.has(result.id)}
                        onChange={() => toggleTestSample(result.id)}
                        disabled={isDisabled}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="text-sm text-text-primary">
                          Result {result.id}
                          {isDisabled && (
                            <span className="ml-2 text-xs text-text-disabled">(in training set)</span>
                          )}
                        </div>
                        <div className="text-xs text-text-tertiary font-mono truncate">
                          {result.harness}:{result.provider}:{result.model}
                        </div>
                      </div>
                      <QualityBadge quality={result.quality as 1|2|3|4|null} size="sm" />
                    </div>
                  )
                })}
              </div>
            </div>

            {existingJudge && existingJudge.alignment_score !== null && existingJudge.alignment_score !== undefined && (
              <div className="text-sm text-text-secondary">
                Current alignment score: <span className="font-medium text-text-primary">{existingJudge.alignment_score.toFixed(3)}</span>
              </div>
            )}
          </>
        )}

        {formError && (
          <div className="px-3 py-2 rounded-lg bg-status-error-muted border border-status-error/30 text-sm text-status-error">
            {formError}
          </div>
        )}

        <div className="flex gap-2 justify-end pt-4 border-t border-border">
          <Button variant="ghost" onClick={onClose} disabled={createMutation.isPending || trainMutation.isPending}>
            Cancel
          </Button>
          <Button
            onClick={handleSubmit}
            disabled={createMutation.isPending || trainMutation.isPending || scorableResults.length === 0}
          >
            {createMutation.isPending ? 'Creating...' : trainMutation.isPending ? 'Training...' : existingJudge ? 'Update & Retrain' : 'Create & Train'}
          </Button>
        </div>
      </div>
      </Dialog.Content>
    </Dialog>
  )
}

