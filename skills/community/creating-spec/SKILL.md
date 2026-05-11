---
name: creating-spec
description: Create comprehensive technical specs for SDK gaps, feature modules, or system centralization efforts. Use when writing specs, PRDs, gap analysis documents, or planning centralization of scattered functionality into a single module. Triggers on "create spec", "write spec", "gap spec", "centralize", "fill the gap".
---

# Creating Spec

Systematic workflow for creating comprehensive technical specifications that centralize scattered functionality, fill SDK gaps, or plan new feature modules. This skill encodes the proven process used to produce high-quality specs like session-management and tool-registry-bridge specs.

<critical_rules>

## MANDATORY WORKFLOW

You MUST follow these phases in order. Skipping phases or combining them will produce incomplete specs.

### Phase 1: DEEP EXPLORATION (output only, no writes)

**Goal**: Map the full landscape of existing code across ALL relevant codebases before proposing anything.

1. **Launch parallel exploration agents** (4-5 simultaneous) covering:
   - The target package where the spec will be implemented (e.g., `providers/sdk`)
   - The reference implementation that has the most complete version (e.g., `providers/runtime`)
   - Consumer codebases that have their own versions (e.g., `packages/electron/src/agents/`, `packages/electron/src/looper/`)
   - Any shared packages that contain related types or utilities (e.g., `packages/types`)

2. **Each explorer must report**:
   - File paths with key types/interfaces
   - How components connect and interact
   - What patterns are used (Effect services, Context.Tag, factories, etc.)
   - Duplication and fragmentation across codebases

3. **MANDATORY**: Read the key files directly after exploration to verify findings. Do NOT rely solely on explorer summaries for type signatures or API shapes.

4. **Present findings FIRST** — show the user:
   - A cross-codebase comparison table (what exists where)
   - A duplication map (what's doing the same thing in multiple places)
   - What should be centralized vs. what should stay where it is
   - Clear identification of gaps

**FORBIDDEN**: Writing any files during Phase 1. Output analysis to chat only.

### Phase 2: CLARIFICATION (ask questions before writing)

**Goal**: Resolve design decisions that affect the spec's architecture.

1. **Use the AskUserQuestion tool** to ask 2-4 focused questions about:
   - Scope decisions (full replacement vs. building blocks vs. thin wrapper)
   - Automation level (fully automatic vs. manual vs. hybrid)
   - Backward compatibility concerns (native support vs. consumer handles)
   - What to include vs. exclude from the centralized module

2. **Question format**:
   - Each question should have 2-3 concrete options with descriptions
   - Mark the recommended option with "(Recommended)"
   - Options should represent genuinely different architectural choices, not trivial preferences

3. **MANDATORY**: Wait for user answers before proceeding. Do NOT assume defaults.

**FORBIDDEN**: Asking more than 4 questions at once. Keep it focused on decisions that materially affect the spec.

### Phase 3: SPEC WRITING

**Goal**: Write a comprehensive specification at the right level of abstraction — behavioral contracts and architectural decisions, not implementation code.

1. **Check existing spec format** — Read any previous specs in the same directory (e.g., `tasks/prd-sdk/1_*.md`, `tasks/prd-sdk/2_*.md`) to match the established style and structure.

2. **Write the spec** following the template structure below.

3. **MANDATORY sections** (all must be present):
   - Problem Statement (what's broken/duplicated, what it costs today)
   - Design overview (architecture diagram in ASCII, high-level flow)
   - New files (directory structure)
   - Detailed API specifications (interfaces, types, service tags)
   - What this replaces (file-by-file mapping of what changes where)
   - Interaction with existing systems (how it coexists with what's already there)
   - Public API surface (explicit exports list)
   - High-Level Implementation Overview (consumer-facing code examples)
   - Testing strategy (unit + integration test plans)
   - Implementation order (numbered steps with dependencies and parallelization)
   - Migration path (phased rollout for existing consumers)
   - What does NOT move (explicit exclusion list with reasons)

### Phase 3b: EFFECT-TS COMPLIANCE CHECK

**Goal**: Verify all code snippets in the spec follow Effect-TS patterns before presenting to the user.

**MANDATORY**: After writing the spec, audit every code snippet against the `effect-ts` and `effect-ts` skills. Check:

1. **Import patterns**: Must use `import * as Module from "effect/Module"`, never `import { X } from "effect"`
2. **Branded types**: All domain primitives (IDs, keys, names) must be branded via `Schema.String.pipe(Schema.brand("X"))`. Check existing `protocol/branded.ts` for established patterns.
3. **Schema class patterns**: `Schema.Class` for records, `Schema.TaggedClass` for discriminated variants (events, status types). Check how existing events in `protocol/events.ts` are defined and match exactly.
4. **No `Schema.Unknown`**: Use `JsonValue`, `JsonObject` (from `protocol/shared.ts`), or `Schema.Defect` (for wrapping external errors). Never `Schema.Unknown` or bare `unknown` in types.
5. **No `Schema.Enums`**: Use `Schema.Literal("a", "b", "c")` for string literal unions. `Schema.Enums` is only for TypeScript `enum` types.
6. **No `Schema.suspend`**: Only for recursive types. Not needed for referencing other schemas.
7. **Service pattern**: Services must use `Context.Tag` with static factory methods and static `layer`. Never module-scoped functions for service logic or layer factories.
8. **Static helpers**: Helper/utility functions must be static methods on a helper class (e.g., `MyHelpers.resolve()`), not module-scoped `export const` functions.
9. **`Effect.fn` tracing**: All service method implementations must specify `Effect.fn("ServiceName.methodName")` for observability. Note this requirement explicitly in the spec.
10. **Error handling**: Domain errors use `Schema.TaggedError`. Unknown external errors wrapped with `Schema.Defect`. No `unknown` in error channels.
11. **Secrets**: API keys and sensitive values use `Redacted.Redacted`, not plain `string`.
12. **Testability**: Use `Clock.currentTimeMillis` instead of `Date.now()` or raw `clock` callbacks. Effect's `TestClock` handles test time control.
13. **Immutable state**: Service state must be held in `Ref` or `SynchronizedRef`, not mutable `Map`/`Set`. Prefer `HashMap.HashMap` from Effect.
14. **Schema.Class construction**: When returning instances of `Schema.Class` types, always use `new ClassName({...})` constructors, not plain object literals.

### Phase 3c: CROSS-SPEC CONSISTENCY CHECK

**Goal**: Ensure the new spec doesn't contradict or duplicate definitions from other specs.

**MANDATORY**: Before finalizing, check against all existing specs in the same directory:

1. **No duplicate definitions**: If a type, constant, or function is already defined in another spec, import it — don't redefine. Common sources of duplication:
   - Provider family resolution functions
   - Provider metadata key fallback maps
   - Type definitions that span multiple concerns
2. **Consistent naming**: Same concept must have the same name across all specs. If Spec N defines `ProviderFamilyId`, Spec N+1 must not call it `OpenResponsesProviderFamily`.
3. **Compatible types**: If two specs extend the same interface (e.g., `CompozyCallProviderOptions`), list ALL fields from all specs, not just yours.
4. **Implementation ordering**: If your spec depends on a type expansion from another spec (e.g., `ProviderId` growing from 3 to 11 values), document this dependency explicitly in the Implementation Order section.
5. **Canonical ownership**: Each type/function/constant must have ONE canonical source file. The spec that defines it is the owner. All other specs that need it must say "Import from `src/path/file.ts` (defined in Spec N)".

### Phase 4: HIGH-LEVEL IMPLEMENTATION (iterate if asked)

**Goal**: Show concrete consumer-facing API examples that demonstrate how the final result works.

1. **Include in the spec** a "High-Level Implementation Overview" section with:
   - Setup / configuration code
   - Registration / initialization code
   - Usage during streaming or execution
   - Direct utility usage (codec, helpers, etc.)
   - Custom provider / extension example
   - Before/after dependency graph (ASCII)

2. **If user asks for this separately**, present it as a concise chat response with annotated code blocks.

</critical_rules>

<spec_template>

## Spec Document Structure

Follow this structure for every spec. Sections are numbered for cross-referencing.

```markdown
# [Feature Name] for [Target Package]

## Problem Statement
- What systems currently exist (list each with location)
- What duplication exists (table format: concern | location A | location B | location C)
- What this costs today (concrete pain points, not abstract)

## Design: [Design Name]
- Architecture diagram (ASCII art showing data flow)
- Key principle (e.g., "fully automatic", "opt-in", "plug-in")

## New Files
- Directory tree of new files to create

## 1-N. Detailed Specifications
- Each major component gets its own numbered section
- Include full TypeScript interfaces with JSDoc
- Show Effect service tags, Layer factories
- Specify error types

## N+1. What This Replaces
- Table: Current File | What Moves | What's Eliminated
- Separate tables per codebase (runtime, agents, looper)

## N+2. Interaction With Existing Systems
- How new code coexists with existing services
- What changes vs. what stays the same

## N+3. Public API Surface
- Explicit export lists from sub-path and main entry

## N+4. High-Level Implementation Overview
- Consumer-facing code examples (setup, usage, customization)
- Before/after dependency graph

## N+5. Testing Strategy
- Unit test plan per module
- Integration test plan
- Migrated tests from existing codebases

## N+6. Implementation Order
- Numbered steps with dependency column and parallelization notes
- Table format: Step | What | Depends On | Parallelizable

## N+7. Migration Path
- Phased rollout (Phase 1, 2, 3...)
- Each phase: what changes, what re-exports, what gets deleted

## N+8. What Does NOT Move
- Table: Concern | Location | Why It Stays
- Be explicit about boundaries
```

</spec_template>

<quality_standards>

## Quality Checklist

Before considering a spec complete, verify:

- [ ] **Cross-codebase exploration** was done (not just the target package)
- [ ] **Duplication map** clearly shows what's duplicated where
- [ ] **All design decisions** were confirmed with the user via AskUserQuestion
- [ ] **TypeScript interfaces** are complete (not pseudocode)
- [ ] **Effect-TS compliance** — all code snippets pass Phase 3b checks (branded types, Schema patterns, service patterns, Effect.fn, no Schema.Unknown)
- [ ] **Cross-spec consistency** — no duplicate definitions, consistent naming, compatible type extensions (Phase 3c)
- [ ] **Canonical ownership** — every type/function/constant has ONE owning spec, all others import
- [ ] **Effect patterns** follow project conventions (Context.Tag, Layer, Schema.TaggedError)
- [ ] **Implementation order** has clear dependency chains (including cross-spec dependencies)
- [ ] **Migration path** is phased (not big-bang)
- [ ] **What does NOT move** section explicitly excludes consumer concerns
- [ ] **High-level implementation** shows real consumer-facing code
- [ ] **File path** follows the existing spec naming convention (e.g., `tasks/prd-sdk/N_feature-name.md`)
- [ ] **Not over-specified** — passes the Spec-vs-Implementation test (see below)

## Writing Style

- Use tables for comparisons and mappings (not prose)
- Use ASCII art for architecture diagrams (not mermaid)
- Use TypeScript code blocks for interfaces (not pseudocode)
- Be concrete: file paths, function names, type names (not "the service" or "the module")
- Show the "what it costs today" with specific line counts and file names
- Every section should answer "what changes and what stays the same"

## Spec-vs-Implementation Test (Anti-Bloat)

Specs must describe WHAT the system does and WHY, not HOW it does it line-by-line. Apply this test to every code block:

### APPROPRIATE in a spec (keep these):
- **Type/schema definitions** — these ARE the contract (e.g., `Schema.Class`, interfaces, branded types)
- **Interface signatures** — public API surface with JSDoc
- **Short behavioral pseudocode** (< 15 lines) — key algorithm steps at a high level
- **Decision tables** — provider → config → behavior mappings
- **ASCII diagrams** — architecture, data flow, before/after dependency graphs
- **One example per pattern** — show the pattern once, note "apply same pattern for X, Y, Z"

### NOT appropriate in a spec (replace these):
- **Full function bodies** (> 15 lines) — replace with behavioral description: "When X happens, the system should Y"
- **Repetitive implementations** (same pattern shown N times) — show once, use a table for variations
- **Internal state types** — internal data structures are implementation details, describe behavior instead
- **Exact variable names and loop structures** — over-constrains the implementer
- **Copy-paste-ready production code** — if an implementer would copy rather than interpret, it's too detailed

### How to fix bloated sections:
1. **Extract the architectural decision** from the code and state it in prose ABOVE the code
2. **Replace implementation code** with: behavioral contract, mapping table, or interface signature
3. **Move to appendix** if reference code is truly needed — label it "Reference Implementation Sketch (non-normative)"
4. **One example rule**: Show one concrete example (e.g., one env builder), then use a table for the rest

### Example transformation:

**BLOATED** (131 lines of 8 env builders):
```typescript
export const buildZaiEnvVars = (config: ZaiConfig): Record<string, string> => {
  const env: Record<string, string> = {};
  env.ANTHROPIC_BASE_URL = "https://api.zai.com/v1";
  if (config.apiKey) env.ANTHROPIC_AUTH_TOKEN = config.apiKey;
  // ... 15 more lines
};
export const buildOpenRouterEnvVars = (config: OpenRouterConfig): ... => { ... };
// ... 6 more builders, same pattern
```

**CORRECT** (table + 1 example):

> **Key decision**: Env vars are built fresh per-request (not pre-computed at construction).

| Provider | Base URL | Auth Var | Extra Vars | Clears API_KEY? |
|----------|----------|----------|------------|-----------------|
| zai | `https://api.zai.com/v1` | `ANTHROPIC_AUTH_TOKEN` | — | Yes |
| openrouter | `https://openrouter.ai/api/v1` | `ANTHROPIC_AUTH_TOKEN` | — | Yes |
| ... | ... | ... | ... | ... |

All builders follow the same pattern. Reference: `buildZaiEnvVars` (shown above).

</quality_standards>

<anti_patterns>

## What NOT To Do

### Workflow Anti-Patterns
- **Do NOT write the spec without exploring first** — you will miss duplication and context
- **Do NOT skip the clarification phase** — design decisions affect every section
- **Do NOT skip Phase 3b (Effect-TS check)** — every spec we wrote without this phase had 5-7 violations
- **Do NOT skip Phase 3c (cross-spec check)** — specs 2 and 5 independently defined the same 3 functions with different signatures, causing 3 Critical contradictions
- **Do NOT write the spec without reading previous specs** — format consistency AND type consistency matter
- **Do NOT ask more than 4 clarification questions** — focus on architectural decisions only

### Content Anti-Patterns
- **Do NOT write vague interfaces** — include full type signatures with Effect patterns
- **Do NOT propose big-bang migrations** — always use phased rollout
- **Do NOT include consumer concerns in the SDK** — approval gates, UI streaming, prompt injection stay in consumers
- **Do NOT skip the "What does NOT move" section** — explicit boundaries prevent scope creep
- **Do NOT present high-level overview without concrete code** — show setup, registration, usage, and customization

### Bloat Anti-Patterns (from real audit findings)
- **Do NOT write full function implementations** — specs with 100+ line function bodies (env builders, adapters, drivers) bury architectural decisions in code walls. Use behavioral descriptions + tables instead.
- **Do NOT repeat the same pattern N times** — show once, table the variations. One env builder shown 8 times = 131 wasted lines; a table + 1 example = 20 lines with better clarity.
- **Do NOT specify internal state types** — `RegistryState` with exact `Map` key formats is an implementation detail. Describe the behavioral contract ("caches bridges by tool-set signature").
- **Do NOT write copy-paste-ready production code** — if an implementer would copy your code verbatim, you've written an implementation, not a spec. Specs should require interpretation.
- **Do NOT bury key decisions in code** — the "dual role of request.model" decision was invisible inside a 99-line class body. State decisions in prose BEFORE any code.

### Effect-TS Anti-Patterns (from real audit findings)
- **Do NOT use `Schema.Unknown`** — use `JsonValue`, `JsonObject`, or `Schema.Defect`
- **Do NOT use plain type aliases for IDs** — use branded schemas: `Schema.String.pipe(Schema.brand("X"))`
- **Do NOT use `Schema.Class` for events** — discriminated variants (events with `type` field) must use `Schema.TaggedClass`
- **Do NOT use `Schema.Enums` for string literals** — use `Schema.Literal("a", "b", "c")`
- **Do NOT define module-scoped functions** — use static methods on helper/service classes
- **Do NOT return plain objects from Schema.Class factories** — use `new ClassName({...})` constructors
- **Do NOT use raw callbacks for testable operations** — use Effect services (e.g., `Clock` instead of `clock?: () => number`)
- **Do NOT use `as unknown as X` double casts** — use spread syntax or `Schema.encode`

### Cross-Spec Anti-Patterns (from real audit findings)
- **Do NOT redefine a function that another spec already defines** — import it. Common trap: utility functions like `resolveProviderMetadata` get independently spec'd by multiple gap specs.
- **Do NOT give the same concept different names** — `ProviderFamilyId` vs `OpenResponsesProviderFamily` caused confusion. Pick one name and use it everywhere.
- **Do NOT silently drop fields when extending a shared type** — if Spec 1 adds `apiKey` to an options type and Spec 2 extends that type, include `apiKey` or explicitly note its removal.
- **Do NOT assume implementation order** — if your spec depends on type expansions from another spec (e.g., `ProviderId` growing from 3 to 11 values), document the dependency in your Implementation Order section.

</anti_patterns>
