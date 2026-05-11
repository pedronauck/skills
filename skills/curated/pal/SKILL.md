---
name: pal
description: Comprehensive Pal MCP toolkit for code analysis, debugging, planning, refactoring, code review, and execution tracing. Provides systematic workflows with expert validation for complex development tasks.
---

# Pal MCP Toolkit

The Pal MCP toolkit provides specialized tools for comprehensive code analysis and development workflows. Each tool follows a multi-step workflow pattern with expert validation.

## Quick Reference: Tool Selection

| Task Type | Tool | Reference |
|-----------|------|-----------|
| Architecture & code analysis before complex tasks | `mcp__zen__analyze` | [analyze.md](references/analyze.md) |
| Bug investigation & root cause analysis | `mcp__zen__debug` | [debug.md](references/debug.md) |
| Strategic planning & task breakdown | `mcp__zen__planner` | [planner.md](references/planner.md) |
| Code smell detection & refactoring | `mcp__zen__refactor` | [refactor.md](references/refactor.md) |
| Code review after completing tasks | `mcp__zen__codereview` | [review.md](references/review.md) |
| Execution flow & dependency tracing | `mcp__zen__tracer` | [tracer.md](references/tracer.md) |

## Critical Workflow Requirements

<critical>

### Mandatory Completion Rules

- **NEVER** stop a workflow before `next_step_required: false` is returned
- **ALWAYS** increment `step_number` and call the tool again when `next_step_required: true`
- **TASK INVALIDATION**: Incomplete workflows result in immediate task rejection
- **NO EXCEPTIONS**: Even if analysis seems complete after step 1, you MUST complete all steps

### Model Requirement

- **MANDATORY**: Always use `model: "anthropic/claude-opus-4.6"` for ALL Pal MCP tool calls
- **NEVER** use any other model when calling Pal MCP tools

### Workflow Validation Checklist

1. Check `next_step_required` in every response
2. If `true`, call the tool again with incremented `step_number`
3. Never proceed with implementation while `next_step_required: true`
4. Workflow is complete ONLY when `next_step_required: false`

</critical>

## Tool Overview

### Analyze (`mcp__zen__analyze`)

**When to Use:**
- Before complex tasks to understand existing architecture
- Architecture review and system design assessment
- Performance, security, and technical debt analysis

**Key Parameters:**
- `analysis_type`: `"architecture"` | `"performance"` | `"security"` | `"quality"` | `"general"`
- `output_format`: `"summary"` | `"detailed"` | `"actionable"`

See [references/analyze.md](references/analyze.md) for complete documentation.

---

### Debug (`mcp__zen__debug`)

**When to Use:**
- Bug investigation and root cause analysis
- Performance issues, memory leaks, race conditions
- Integration failures and service communication problems

**Key Parameters:**
- `hypothesis`: Current theory about the root cause
- `confidence`: `"exploring"` | `"low"` | `"medium"` | `"high"` | `"very_high"` | `"almost_certain"` | `"certain"`

See [references/debug.md](references/debug.md) for complete documentation.

---

### Planner (`mcp__zen__planner`)

**When to Use:**
- Breaking down complex tasks into manageable steps
- System design and architectural decisions
- Migration planning and implementation strategies

**Key Parameters:**
- `is_step_revision`: For refining previous steps
- `is_branch_point`: For exploring alternative approaches
- `branch_id`: Naming alternative approaches

See [references/planner.md](references/planner.md) for complete documentation.

---

### Refactor (`mcp__zen__refactor`)

**When to Use:**
- Addressing code smells and technical debt
- Decomposing large modules or classes
- Modernizing legacy patterns

**Key Parameters:**
- `refactor_type`: `"codesmells"` | `"decompose"` | `"modernize"` | `"organization"`
- `focus_areas`: `["performance", "readability", "maintainability", "security"]`

See [references/refactor.md](references/refactor.md) for complete documentation.

---

### Code Review (`mcp__zen__codereview`)

**When to Use:**
- After completing a task (MANDATORY)
- Before submitting pull requests
- Validating implementation against project standards

**Key Parameters:**
- `review_type`: `"full"` for comprehensive analysis
- `severity_filter`: `"all"` to catch all severity levels
- `focus_on`: Specific areas like "performance", "security", "type-safety"

See [references/review.md](references/review.md) for complete documentation.

---

### Tracer (`mcp__zen__tracer`)

**When to Use:**
- Understanding code execution paths
- Mapping dependencies before refactoring
- Debugging complex flows

**Key Parameters:**
- `trace_mode`: `"precision"` (execution flow) | `"dependencies"` (structural analysis) | `"ask"`
- `target_description`: Clear description of what to trace and why

See [references/tracer.md](references/tracer.md) for complete documentation.

## Common Required Parameters

All Pal MCP tools require these base parameters:

```json
{
  "step": "Description of current step",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Findings from this step",
  "model": "anthropic/claude-opus-4.6"
}
```

## File Path Requirements

- **ALWAYS** use full absolute paths for `relevant_files`
- Include files directly involved in the analysis
- Include related files that provide context
- Include test files when relevant

## Typical Workflow Pattern

1. **Start**: Call the tool with `step_number: 1` and initial strategy
2. **Iterate**: Increment `step_number` and refine findings based on previous step
3. **Continue**: Keep calling until `next_step_required: false`
4. **Complete**: Only proceed with implementation after workflow completes

## Violation Examples (Task Rejection)

- Calling a Pal tool once and proceeding to implementation
- Skipping steps because analysis seems complete
- Starting implementation before `next_step_required: false`
- Using a model other than `anthropic/claude-opus-4.6`
