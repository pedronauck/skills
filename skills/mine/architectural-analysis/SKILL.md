---
name: architectural-analysis
description: Deep architectural audit focused on finding dead code, duplicated functionality, architectural anti-patterns, type confusion, and code smells. Use when user asks for architectural analysis, find dead code, identify duplication, or assess codebase health. Don't use for style/formatting issues, performance profiling, security audits, or feature-level code review.
metadata:
  author: Pedro Nauck
  github: https://github.com/pedronauck
  repository: https://github.com/pedronauck/skills
---
# Architectural Analysis

## Instructions

Perform comprehensive architectural audit focused on structural issues, dead code, duplication, and systemic problems.

### Phase 1: Discovery & Planning

#### Step 1: Map Codebase Structure
```bash
# Get directory structure
find . -type d -not -path "*/node_modules/*" -not -path "*/.git/*"

# Count files by type
find . -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" | wc -l
```

#### Step 2: Identify Entry Points
- Main application entry (`index.ts`, `main.ts`, `app.ts`)
- API routes/controllers
- Public exports (`index.ts` files)
- CLI entry points
- Test files

#### Step 3: Create Comprehensive File List
Use Glob to find all source files.
Create todo list with one item per file to analyze.

### Phase 2: Dead Code Detection

For EACH file in the todo list:

#### Step 1: Identify Exports
- What does this file export?
- Are exports functions, classes, types, constants?
- Is anything exported at all?

#### Step 2: Search for Usage

For each export, search if it's imported/used anywhere:
```bash
# Search for imports of this export
grep -r "import.*ExportName" . --include="*.ts" --include="*.tsx"
grep -r "from.*filename" . --include="*.ts" --include="*.tsx"

# Search for direct usage
grep -r "ExportName" . --include="*.ts" --include="*.tsx"
```

#### Step 3: Categorize Code

**Dead Code** (mark for removal):
- Exported but never imported
- Functions defined but never called
- Classes instantiated nowhere
- Types defined but never used
- Constants defined but never referenced
- Entire files with no imports from other files

**Possibly Dead** (needs verification):
- Only used in commented-out code
- Only used in dead code
- Only used in other unused exports
- Used only in tests for deprecated features

**Internal Dead Code**:
- Functions defined in file but never called (not exported)
- Variables assigned but never read
- Parameters accepted but never used

#### Step 4: Check for False Positives

Not dead if:
- Used in tests (may be public API)
- Dynamically imported/required
- Used via reflection/string references
- Part of public API (even if not used internally)
- Framework hooks (lifecycle methods, callbacks)
- Accessed via `window` or global scope

#### Step 5: Record Findings
```
File: path/to/file.ts
Status: [DEAD|POSSIBLY_DEAD|USED]
Exports: [list]
Dead Exports:
  - ExportName - No imports found
  - AnotherExport - Only used in test for deprecated feature
Confidence: [HIGH|MEDIUM|LOW]
```

#### Step 6: Mark Complete
Update todo list.

### Phase 3: Duplication Detection

#### Step 1: Identify Duplicated Logic Patterns

Search for common patterns that suggest duplication:
- Similar function names across files
- Repeated code blocks
- Multiple implementations of same concept

**Manual Pattern Recognition**:
- Read files in same directory
- Look for suspiciously similar code
- Compare utilities/helpers across modules
- Check for copy-pasted blocks

**Grep-Based Detection**:
```bash
# Find similar function signatures
grep -r "function validateEmail" . --include="*.ts"
grep -r "async.*fetch.*api" . --include="*.ts"
grep -r "export.*UserForm" . --include="*.tsx"
```

#### Step 2: Analyze Duplicated Functionality

For each potential duplication:
- Read both/all implementations
- Are they actually the same logic?
- Do they handle same cases?
- Could one replace the other?
- Are differences intentional or accidental?

#### Step 3: Categorize Duplication

**Exact Duplication** (CRITICAL):
- Identical or near-identical code in multiple places
- Copy-pasted functions
- Duplicated utility functions
- **Impact**: Bug fixes need multiple updates, maintenance burden

**Similar Logic** (HIGH):
- Same algorithm, different implementation
- Slightly different parameter handling
- Different names, same purpose
- **Impact**: Inconsistency risk, harder to maintain

**Conceptual Duplication** (MEDIUM):
- Multiple ways to do the same thing
- Competing implementations
- Overlapping utilities
- **Impact**: Confusion, decision paralysis

**Type Duplication** (HIGH):
- Same interface/type defined multiple times
- Similar types that should be unified
- Duplicate constants/enums
- **Impact**: Type inconsistency, refactoring difficulty

#### Step 4: Record Duplication
```
Duplication Group: Email Validation
Type: Exact Duplication
Instances:
  - src/utils/validators.ts:42 - validateEmail()
  - src/lib/email.ts:15 - isValidEmail()
  - src/components/forms/validation.ts:67 - checkEmailFormat()
Analysis: All three implement same regex check
Recommendation: Keep utils/validators.ts version, remove others
Impact: 3 places to update when logic changes
```

### Phase 4: Architectural Anti-Patterns

#### Step 1: Identify God Objects/Classes

Search for files that do too much:
- Files over 500 lines
- Classes with 10+ methods
- Files with many responsibilities
- Modules that import from everywhere

```bash
# Find large files
find . -name "*.ts" -exec wc -l {} + | sort -rn | head -20
```

Analyze large files:
- What does this file do?
- Does it have single responsibility?
- Should it be split?

#### Step 2: Detect Circular Dependencies

Look for:
- File A imports from B, B imports from A
- Circular chains: A → B → C → A
- Module coupling cycles

Use grep to trace import chains:
```bash
# Check what file imports
grep "^import.*from" src/services/auth.ts

# Check what imports this file
grep -r "from.*auth" src/ --include="*.ts"
```

#### Step 3: Find Tight Coupling

Identify:
- High-level modules depending on low-level modules
- Business logic depending on infrastructure
- Core logic depending on framework specifics
- Modules that import from many other modules

#### Step 4: Spot Layer Violations

Check architecture layers:
- Do components import directly from database layer?
- Do models import from views?
- Do utilities import from business logic?
- Is there proper separation of concerns?

#### Step 5: Identify Other Anti-Patterns

**Singleton Abuse**:
- Global state everywhere
- Module-level mutable state
- Static class methods accessing shared state

**Anemic Domain Models**:
- Data classes with no behavior
- All logic in services, models just have getters/setters

**Shotgun Surgery**:
- Single feature change requires touching many files
- Indicates poor cohesion

**Feature Envy**:
- Methods that use more data from other classes than their own

### Phase 5: Type Issues Analysis

#### Step 1: Find Type Abuse

Search for problematic type usage:
```bash
# Find 'any' usage
grep -r ": any" . --include="*.ts" --include="*.tsx" -n

# Find 'unknown' usage
grep -r ": unknown" . --include="*.ts" -n

# Find type assertions
grep -r "as any" . --include="*.ts" -n
grep -r "as unknown" . --include="*.ts" -n

# Find @ts-ignore
grep -r "@ts-ignore" . --include="*.ts" -n
grep -r "@ts-expect-error" . --include="*.ts" -n
```

#### Step 2: Analyze Type Confusion

For each file with type issues:
- Why is `any` used?
- Could proper type be defined?
- Is type assertion hiding a real type error?
- Are @ts-ignore comments masking actual problems?

#### Step 3: Find Type Duplication

Look for:
- Same interface defined in multiple files
- Similar types that could be unified
- Types that could extend from common base
- Constants/enums duplicated across files

#### Step 4: Identify Missing Types

Check for:
- Implicit `any` from missing type annotations
- Functions without return type
- Callbacks without proper typing
- Generic types that should be specific

### Phase 6: Code Smells Detection

#### Step 1: Long Methods/Functions
```bash
# Find functions with many lines
# (manual inspection of large files)
```

Flag functions over 50 lines - likely doing too much.

#### Step 2: Long Parameter Lists

Search for functions with 4+ parameters:
- Could use object parameter instead?
- Are parameters related (should be grouped)?

#### Step 3: Complex Conditionals

Look for:
- Deeply nested if statements (3+ levels)
- Long boolean expressions
- Switch statements with 10+ cases
- Complex ternary operators

#### Step 4: Magic Numbers/Strings

Search for:
- Hardcoded numbers with unclear meaning
- String literals used repeatedly
- Unexplained constants

Should be named constants.

#### Step 5: Commented-Out Code

```bash
# Find commented code blocks
grep -r "^[[:space:]]*//.*function\|class\|const" . --include="*.ts"
```

Commented code should be deleted (use git history).

#### Step 6: Poor Naming

Look for:
- Single letter variables (outside loops)
- Abbreviations without context (`usr`, `msg`, `tmp`)
- Misleading names
- Names that don't reflect purpose

### Phase 7: Generate Report

Read `assets/report-template.md` and write the populated report to `.audits/architectural-analysis-[timestamp].md`. Replace every placeholder (X, Y, Z, file paths, line numbers) with findings from Phases 2-6. Keep every section present even if a finding count is zero — note "None found" rather than deleting headings.

### Phase 8: Summary for User

Read `assets/summary-template.md` and emit the populated summary inline in chat after writing the full report. Replace placeholders and link to the full report at the end.

## Critical Principles

- **NEVER EDIT FILES** - This is analysis only, not cleanup
- **NEVER SKIP FILES** - Analyze entire codebase systematically
- **BE THOROUGH** - Dead code detection requires checking all imports
- **VERIFY DUPLICATES** - Don't just match names, check if logic is same
- **UNDERSTAND ARCHITECTURE** - See the big picture, not just individual files
- **QUANTIFY IMPACT** - Count lines, estimate cleanup potential
- **BE CONFIDENT** - Mark confidence level (HIGH/MEDIUM/LOW) for findings
- **TRACK PROGRESS** - Use todo list for file-by-file analysis

## Success Criteria

A complete architectural analysis includes:
- All files analyzed for dead code
- All exports checked for usage
- Duplication groups identified and cataloged
- Architectural anti-patterns found and explained
- Type issues located and categorized
- Code smells flagged
- Impact assessment quantified
- Structured report generated
