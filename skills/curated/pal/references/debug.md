# Pal Debug Reference

Expert guidance for using the Pal MCP debug tool for systematic debugging and root cause analysis.

## When to Use

- **Bug investigation:** Systematic root cause analysis for reported bugs
- **Performance issues:** Debugging slow operations, memory leaks, or resource exhaustion
- **Integration failures:** Investigating API failures, service communication problems
- **Race conditions:** Identifying concurrency issues and timing problems
- **Before complex tasks:** Understanding existing issues before making changes

## Debugging Scope

The debug tool must analyze:

- **Root cause identification:** Systematic investigation of error sources, failure points, and contributing factors
- **Error patterns:** Recurring issues, exception types, error propagation paths
- **State analysis:** Data inconsistencies, state corruption, race conditions
- **Execution anomalies:** Unexpected behavior, performance degradation, memory issues
- **Integration problems:** API failures, service communication issues, external dependency failures
- **Hypothesis testing:** Systematic validation of theories about the issue

## Required Parameters

```json
{
  "step": "Investigate reported issue",
  "step_number": 1,
  "total_steps": 3,
  "next_step_required": true,
  "findings": "Initial investigation findings",
  "hypothesis": "Initial theory about the root cause",
  "confidence": "exploring",
  "model": "anthropic/claude-opus-4.6"
}
```

## Debugging Approach

- Provide clear description of the issue or problem to investigate
- Include `hypothesis` if you have initial theories about the root cause
- Specify `relevant_context` (methods, functions, or components involved)
- Use `confidence` levels to track investigation progress

## Confidence Levels

Track investigation progress with confidence levels:

1. `"exploring"` - Starting investigation
2. `"low"` - Early theories, limited evidence
3. `"medium"` - Some evidence supports hypothesis
4. `"high"` - Strong evidence for root cause
5. `"very_high"` - Very confident in findings
6. `"almost_certain"` - Nearly confirmed
7. `"certain"` - Root cause definitively identified

## Relevant Files

- Include full absolute paths to files where the issue manifests
- Include related files that might be involved in the problem
- Include test files that reproduce or verify the issue
- Include configuration files if the issue might be configuration-related

## Investigation Process

1. Start with `step_number: 1` and provide initial findings
2. Progressively refine `hypothesis` based on evidence gathered
3. Update `confidence` as investigation progresses
4. Document all `findings` at each step
5. Continue until root cause is identified (`next_step_required: false`)

## Critical Requirements

- **MANDATORY**: Use Pal MCP debug tool **WHEN DEBUGGING ISSUES** or **BEFORE INITIATING COMPLEX TASKS**
- **TASK INVALIDATION**: Task will be invalidated if you skip using the debug tool when debugging issues or don't complete ALL steps
- **NO EXCEPTIONS**: Complete the entire debug workflow (all steps until `next_step_required: false`) before proceeding with fixes or implementation
- **COMPLETE ALL STEPS**: Never stop in the middle of steps - completing partial workflows invalidates the task
