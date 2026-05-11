---
name: sourcebot
description: Search external libraries and frameworks using Sourcebot MCP. Use when researching external code patterns, library APIs, framework examples, or documentation from repositories like Effect-TS/effect, vercel/ai, tanstack/query. NEVER use for local project code.
---

# Sourcebot Guide

Expert guidance for using Sourcebot MCP to search external libraries, frameworks, and code patterns.

## When to Use

- **External library research:** Finding code patterns in Effect-TS, TanStack, Vercel AI SDK, etc.
- **API discovery:** Understanding how external libraries implement specific features
- **Documentation examples:** Finding real-world usage examples from official repositories
- **Framework patterns:** Learning best practices from external framework codebases
- **Migration guidance:** Finding upgrade patterns and breaking changes in external libraries

## When NOT to Use

- **Local project code:** Use `codebase_search` or `osgrep search` instead
- **Local components:** Use local search tools for project files
- **Local utilities:** Never use Sourcebot for your own codebase

## Required Workflow

1. **First, call `list_repos`** to get available repository IDs
2. **Identify relevant repository ID(s)** for your search (e.g., "Effect-TS/effect" for EffectTS)
3. **Always include `filterByRepoIds`** when calling `search_code`
4. **Use `get_file_source`** to fetch specific file contents when needed

## Repository ID Format

- **CRITICAL**: Repository IDs must be in format `"owner/repo"` (e.g., `"Effect-TS/effect"`, `"vercel/ai"`)
- **DO NOT** include the `github.com/` prefix
- The `list_repos` tool returns IDs like `"github.com/owner/repo"` - strip the prefix when using in `filterByRepoIds`

## Usage Examples

### Searching EffectTS patterns

```json
{
  "query": "Effect.gen yield",
  "filterByRepoIds": ["Effect-TS/effect"],
  "includeCodeSnippets": true
}
```

### Searching AI SDK

```json
{
  "query": "streamText tool calling",
  "filterByRepoIds": ["vercel/ai"],
  "includeCodeSnippets": true
}
```

### Searching multiple repos

```json
{
  "query": "error handling patterns",
  "filterByRepoIds": ["Effect-TS/effect", "vercel/ai"],
  "includeCodeSnippets": true
}
```

## Best Practices

- Use descriptive queries (not just keywords, but full descriptions)
- Always specify `filterByRepoIds` to scope searches
- Set `includeCodeSnippets: true` when you need actual code examples
- Use `get_file_source` after finding relevant files to see full context

## Tool Hierarchy for Code Search

1. **Sourcebot** - For EXTERNAL libraries and frameworks only
2. **`codebase_search`** (if available) - For local project code
3. **`osgrep search`** - For local code when codebase_search unavailable
4. **`grep`/`find`** - Last resort for exact string matching

## Critical Requirements

- **MANDATORY**: Use Sourcebot MCP 5-7 times when researching external libraries
- **CRITICAL**: NEVER use Sourcebot to search local project code
- **CRITICAL**: Always use `filterByRepoIds` on EVERY `search_code` call
- **TASK INVALIDATION**: Task will be invalidated if you don't use Sourcebot 5-7 times when dealing with external libraries
- **AFTER SOURCEBOT**: Also use Perplexity and Context7 for updated information on external libraries
