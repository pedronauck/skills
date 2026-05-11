# Pal Analyze Reference

Expert guidance for using the Pal MCP analyze tool for comprehensive code and architecture analysis.

## When to Use

- **Before complex tasks:** Understand existing architecture and code structure before making changes
- **Architecture review:** Assess system design and identify architectural improvements
- **Performance analysis:** Identify bottlenecks and optimization opportunities
- **Security assessment:** Evaluate security posture and identify vulnerabilities
- **Technical debt:** Assess code quality and identify refactoring needs
- **System understanding:** Gain comprehensive understanding of codebase structure and patterns

## Analysis Scope

The analyze tool must examine:

- **Architecture patterns:** System design, component relationships, architectural decisions, design patterns
- **Code quality:** Maintainability, readability, complexity, code organization
- **Performance characteristics:** Algorithm efficiency, scalability, resource usage, optimization opportunities
- **Security posture:** Vulnerability patterns, security best practices, risk assessment
- **Technical debt:** Legacy patterns, deprecated code, refactoring needs, modernization opportunities
- **System structure:** Module boundaries, dependency graphs, interface contracts, integration points

## Required Parameters

```json
{
  "step": "Analyze architecture and code structure",
  "step_number": 1,
  "total_steps": 2,
  "next_step_required": true,
  "findings": "Initial analysis findings",
  "relevant_files": ["/absolute/path/to/file.ts"],
  "model": "anthropic/claude-opus-4.6"
}
```

## Analysis Types

Use `analysis_type` to specify focus:

- `"architecture"` - System design and architectural pattern analysis
- `"performance"` - Performance bottlenecks and optimization analysis
- `"security"` - Security-focused analysis and vulnerability assessment
- `"quality"` - Code quality, maintainability, and technical debt analysis
- `"general"` - Comprehensive multi-faceted analysis (default)

## Output Formats

Use `output_format` to control detail level:

- `"summary"` - High-level overview and key findings
- `"detailed"` - Comprehensive analysis with full context (default)
- `"actionable"` - Focused recommendations and improvement plans

## Relevant Files

- Include full absolute paths to files or directories to analyze
- Include related files that form part of the system architecture
- Include configuration files if analyzing system configuration
- Include test files to understand testing patterns and coverage

## Analysis Process

1. Start with `step_number: 1` and outline analysis strategy
2. Progressively build understanding through multiple steps
3. Document `findings` at each step covering architecture, performance, security, and quality
4. Update `confidence` as analysis deepens
5. Continue until comprehensive understanding is achieved (`next_step_required: false`)

## Critical Requirements

- **MANDATORY**: Use Pal MCP analyze tool **BEFORE INITIATING COMPLEX TASKS** or **WHEN NEEDING ARCHITECTURAL INSIGHTS**
- **TASK INVALIDATION**: Task will be invalidated if you skip using the analyze tool when required or don't complete ALL steps
- **NO EXCEPTIONS**: Complete the entire analyze workflow (all steps until `next_step_required: false`) before proceeding with implementation
- **COMPLETE ALL STEPS**: Never stop in the middle of steps - completing partial workflows invalidates the task
