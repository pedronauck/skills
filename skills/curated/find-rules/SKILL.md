---
name: find-rules
description: Discover and understand project rules, coding standards, and architectural guidelines before starting a task. Use when you need to know the constraints, patterns, or compliance requirements for a feature, file, or technology.
---

# Find Rules

This skill helps you discover and understand the specific rules, conventions, and guidelines that apply to your current task. It systematically explores project documentation to ensure compliance with project standards.

## Instructions

Follow this workflow to identify applicable rules:

### 1. Understand Context

First, analyze the task to determine:

- **Task Type**: PRD creation, Technical Spec, Feature Implementation, Refactoring, Bugfix, etc.
- **Technologies**: React, Elysia, Tailwind, Drizzle, etc.
- **Aspects**: Architecture, Testing, Styling, Naming, etc.

### 2. Pattern-Based Discovery

**REQUIRED:** Use `Glob` and `Grep` tools for local code discovery to find relevant rule files and guidelines.

**EXECUTION STRATEGY:** Execute 3+ tools simultaneously in the FIRST action for efficiency. Never execute tools sequentially when they can run in parallel.

**MANDATORY STEPS:**

1.  **Find Rule Files (run in parallel)**: Use multiple `Glob` patterns simultaneously.

    ```
    # Primary rules
    Glob pattern=".cursor/rules/*.mdc"
    Glob pattern="**/CLAUDE.md"
    Glob pattern="**/AGENTS.md"

    # Secondary rules
    Glob pattern="**/CONTRIBUTING.md"
    Glob pattern="**/ARCHITECTURE.md"
    Glob pattern="**/STYLEGUIDE.md"

    # Alternative AI tool locations
    Glob pattern=".windsurf/rules/*"
    Glob pattern=".cursorrules"
    Glob pattern=".copilot/*"

    # Configuration files
    Glob pattern="**/.eslintrc*"
    Glob pattern="**/tsconfig.json"
    Glob pattern="**/biome.json"
    ```

2.  **Search by Content**: Use `Grep` to find rules mentioning specific technologies or concepts.

    ```
    Grep pattern="react" path=".cursor/rules"
    Grep pattern="CRITICAL|MANDATORY" path=".cursor/rules" output_mode="content"
    Grep pattern="testing" glob="*.md"
    Grep pattern="must|should|never" glob="*.mdc" -i=true
    ```

3.  **Search Locations Priority**:
    - `.cursor/rules/*.mdc` - Technology-specific rules (highest priority)
    - `CLAUDE.md` - General project guidelines
    - `AGENTS.md` - Agent-specific instructions
    - `.windsurf/rules/`, `.cursorrules` - Alternative AI tool rules
    - `docs/` - Documentation directory
    - Configuration files - Implicit rules from tooling

### 3. Extract and Categorize Rules

Once you identify the relevant files:

1.  **Read**: Use the `Read` tool to examine the full content of the identified rule files (e.g., `.cursor/rules/react.mdc`).

2.  **Categorize Each Rule**:
    For each rule found, determine:
    - **Category**: Domain area (e.g., Authentication, Testing, Security, Performance, Styling, Architecture)
    - **Content**: The actual rule or guideline text
    - **Source File**: File path where the rule was found
    - **Enforcement Level**: CRITICAL, MANDATORY, RECOMMENDED, or SUGGESTED

3.  **Analyze**:
    - Look for **CRITICAL** or **MANDATORY** requirements first
    - Identify naming conventions, file structures, and required patterns
    - Note any conflicts or specific instructions for the technologies involved
    - Check for keywords: "must", "should", "never", "always", "required", "forbidden"

### 4. Present Findings

Summarize the rules you found in a clear, actionable format:

- **Rule/Guideline**: The specific standard.
- **Source**: File path and section where it is defined.
- **Enforcement Level**: CRITICAL, MANDATORY, RECOMMENDED.
- **Applicability**: Why it applies to this task.

## Documentation Sources

### Primary Rule Locations

- **.cursor/rules/\*.mdc**: Technology-specific rules (React, Backend, Tailwind, etc.)
- **CLAUDE.md**: General AI assistant guidelines and project context
- **AGENTS.md**: Agent-specific instructions and workflows

### Secondary Rule Locations

- **CONTRIBUTING.md**: Contribution guidelines and processes
- **CODE_OF_CONDUCT.md**: Community and code standards
- **ARCHITECTURE.md**: Architectural decisions and patterns
- **STYLEGUIDE.md**: Code style conventions
- **CODING_STANDARDS.md**: Programming standards

### Alternative AI Tool Locations

- **.windsurf/rules/**: Windsurf-specific rules
- **.cursorrules**: Cursor rules file
- **.copilot/**: GitHub Copilot configuration
- **.codeium/**: Codeium configuration

### Configuration Files (Implicit Rules)

- **.eslintrc.\*, .eslintrc.json**: Linting rules
- **.prettierrc.\*, .prettierrc.json**: Formatting rules
- **tsconfig.json**: TypeScript compiler options
- **.oxlintrc.json**: Oxlint configuration
- **biome.json**: Biome formatter/linter rules

### Documentation Directories

- **docs/**: Project documentation
- **.github/**: GitHub-specific templates and workflows

## Enforcement Levels

- 🚨 **CRITICAL**: Must be followed strictly; violation leads to task rejection.
- ⚠️ **MANDATORY**: Required standards that should not be skipped.
- ✅ **RECOMMENDED**: Best practices that should be followed when applicable.
- 💡 **SUGGESTED**: Nice-to-have guidelines.

## Common Rule Categories

When categorizing rules, use these common domain areas:

- **Architecture**: Design patterns, module boundaries, dependencies
- **Testing**: Test requirements, coverage, patterns
- **Security**: Authentication, authorization, input validation
- **Performance**: Optimization requirements, caching, lazy loading
- **Styling**: CSS/Tailwind conventions, component styling
- **Naming**: File naming, variable naming, function naming
- **Code Quality**: Linting, formatting, type safety
- **API**: Endpoint patterns, request/response handling
- **State Management**: Redux, Context, hooks patterns
- **Error Handling**: Exception handling, error boundaries

## Examples

**User**: "I need to create a new React component."
**Skill Action**:

1.  **Context**: Feature development, React, component structure.
2.  **Discovery**:
    - Use Glob: `Glob pattern=".cursor/rules/*.mdc"` to find rule files.
    - Use Grep: `Grep pattern="react" path=".cursor/rules"` to find React-related rules.
    - Result points to `.cursor/rules/react.mdc`.
3.  **Extraction**: Read `.cursor/rules/react.mdc`.
4.  **Findings**:
    - 🚨 **CRITICAL**: Use functional components exclusively.
    - ⚠️ **MANDATORY**: File naming must be `kebab-case.tsx`.
    - ⚠️ **MANDATORY**: Use hooks for state management.

**User**: "How do I write a backend endpoint?"
**Skill Action**:

1.  **Context**: Backend, API, implementation.
2.  **Discovery**:
    - Use Glob: `Glob pattern=".cursor/rules/*.mdc"` to list available rules.
    - Use Grep: `Grep pattern="backend|endpoint|elysia" path=".cursor/rules"` to find backend rules.
    - Result points to `.cursor/rules/elysia.mdc` and `.cursor/rules/data-fetch.mdc`.
3.  **Extraction**: Read relevant files.
4.  **Findings**:
    - 🚨 **CRITICAL**: Follow Elysia handler patterns.
    - ⚠️ **MANDATORY**: Use specific data fetching wrappers.
