# Pal Tracer Reference

Expert guidance for using the Pal MCP tracer tool for code execution flow and dependency analysis.

## When to Use

- **Before complex tasks:** Understand existing code structure and execution patterns
- **Debugging:** Trace execution flow to identify where issues occur
- **Refactoring:** Map dependencies before making architectural changes
- **Code review:** Understand complex code paths before reviewing
- **Onboarding:** Learn how a system works by tracing key flows

## Tracing Scope

The tracer must analyze:

- **Execution flow:** Method call chains, control flow, data flow through functions
- **Dependency relationships:** Imports, exports, module dependencies, class hierarchies
- **Call patterns:** How functions are invoked, callback chains, event handlers
- **Data transformations:** How data flows through the system, state changes
- **Integration points:** API boundaries, service boundaries, external dependencies
- **Architectural understanding:** Component relationships, system structure

## Required Parameters

```json
{
  "step": "Trace execution flow for feature X",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Initial trace findings",
  "target_description": "Trace how user authentication flows from login endpoint to database",
  "trace_mode": "precision",
  "model": "anthropic/claude-opus-4.6"
}
```

## Trace Mode Selection

- `"precision"` - Execution flow analysis (method calls, control flow, runtime behavior)
- `"dependencies"` - Structural analysis (imports, exports, static relationships, module structure)
- `"ask"` - Let the tool determine the appropriate mode based on context

## Target Description

Provide clear, specific description of what to trace:

- **Good:** "Trace how user authentication flows from login endpoint to database"
- **Good:** "Map dependencies for the payment processing module"
- **Bad:** "Trace the code" (too vague)

Include context about why tracing is needed (debugging, understanding architecture, refactoring planning).

## Relevant Files

- Include full absolute paths to files involved in the trace
- Start with entry points (main functions, API endpoints, component roots)
- Include related files that might be part of the execution path or dependency graph

## Critical Requirements

- **MANDATORY**: Use Pal MCP tracer tool **BEFORE INITIATING A TASK** or **WHEN DEBUGGING COMPLEX FLOWS**
- **TASK INVALIDATION**: Task will be invalidated if you skip using the tracer tool when required or don't complete ALL steps
- **NO EXCEPTIONS**: Complete the entire tracer workflow (all steps until `next_step_required: false`) before proceeding with implementation
- **COMPLETE ALL STEPS**: Never stop in the middle of steps - completing partial workflows invalidates the task
