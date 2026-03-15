# Pal Code Review Reference

Expert guidance for using the Pal MCP codereview tool for comprehensive code review.

## When to Use

- **AFTER FINISHING A TASK** - Mandatory code review before considering task complete
- When reviewing code changes for quality and correctness
- Before submitting pull requests
- When validating implementation against project standards

## Review Scope

The review must cover:

- **Project standards compliance:** Coding style, naming conventions, architecture patterns
- **Potential issues:** Bugs, edge cases, error handling gaps, race conditions
- **Performance improvements:** Inefficient algorithms, unnecessary re-renders, memory leaks, optimization opportunities
- **Code smells:** Duplication, long methods, complex conditionals, god objects, tight coupling
- **Security vulnerabilities:** Injection risks, authentication flaws, data exposure
- **Maintainability concerns:** Hardcoded values, magic numbers, unclear abstractions, technical debt
- **Type safety issues:** Unsafe type assertions, missing null checks, incorrect type usage
- **Test coverage gaps:** Untested edge cases, missing error scenarios

## Required Parameters

```json
{
  "step": "Review implementation for quality and correctness",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Initial review findings",
  "relevant_files": ["/absolute/path/to/file.ts"],
  "model": "anthropic/claude-opus-4.6"
}
```

## Review Configuration

- Use `review_type: "full"` for comprehensive analysis
- Use `severity_filter: "all"` to catch all severity levels
- Specify `focus_on` areas if specific concerns exist (e.g., "performance", "security", "type-safety")
- Include project standards in `standards` parameter when available

## Relevant Files

- Include full absolute paths to files that were changed or reviewed
- Include related files that might be affected by the changes
- Include test files to verify coverage

## Report All Findings

Present all issues found regardless of severity - don't filter out recommendations that seem unrelated to the immediate task.

## Critical Requirements

- **MANDATORY**: Use Pal MCP codereview tool **AFTER FINISH A TASK** to perform comprehensive code review
- **TASK INVALIDATION**: Task will be invalidated if you skip using the codereview tool after finishing a task or don't complete ALL steps
- **NO EXCEPTIONS**: Complete the entire codereview workflow (all steps until `next_step_required: false`) before considering the task complete
- **COMPLETE ALL STEPS**: Never stop in the middle of steps - completing partial workflows invalidates the task
