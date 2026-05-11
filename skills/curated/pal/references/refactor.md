# Pal Refactor Reference

Expert guidance for using the Pal MCP refactor tool for code refactoring analysis.

## When to Use

- Refactoring existing code to improve quality
- Addressing code smells and technical debt
- Decomposing large modules or classes
- Modernizing legacy patterns
- Reorganizing code structure

## Refactoring Scope

The refactor tool must analyze:

- **Code smells:** Duplication, long methods, complex conditionals, god objects, tight coupling
- **Decomposition opportunities:** Extracting functions, splitting classes, modularizing components
- **Modernization needs:** Updating patterns, adopting new language features, improving APIs
- **Organization improvements:** File structure, module boundaries, dependency management

## Required Parameters

```json
{
  "step": "Analyze code for refactoring opportunities",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Initial analysis findings",
  "model": "anthropic/claude-opus-4.6"
}
```

## Refactoring Types

Use `refactor_type` to specify focus:

- `"codesmells"` - Identify and address code smells
- `"decompose"` - Break down large modules/classes
- `"modernize"` - Update to modern patterns
- `"organization"` - Improve file/module structure

## Focus Areas

Specify `focus_areas` for specific concerns:

```json
{
  "focus_areas": ["performance", "readability", "maintainability", "security"]
}
```

## Style Guide Examples

Include reference files for target patterns:

```json
{
  "style_guide_examples": ["/absolute/path/to/reference-file.ts"]
}
```

## Relevant Files

- Include full absolute paths to files requiring refactoring
- Include related files that might be affected by the refactoring
- Include reference files that demonstrate target patterns or styles

## Greenfield Approach

This project is in alpha - prioritize quality over backwards compatibility:

- Supporting old and new patterns introduces unnecessary complexity
- Never sacrifice quality for backwards compatibility

## Implementation Principles

- **NEVER** use workarounds - always prefer good and well-designed solutions
- **ALWAYS** follow the rules from `.cursor/rules` and double-check which rules apply before starting
- **ALWAYS** check dependent file APIs before writing tests to avoid incorrect code

## Critical Requirements

- **MANDATORY**: Use Pal MCP refactor tool to find the best approach for refactoring
- **TASK INVALIDATION**: Task will be invalidated if you skip using the refactor tool when required or don't complete ALL steps
- **NO EXCEPTIONS**: Complete the entire refactor workflow (all steps until `next_step_required: false`) before proceeding with implementation
- **COMPLETE ALL STEPS**: Never stop in the middle of steps - completing partial workflows invalidates the task
