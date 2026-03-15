---
name: es-toolkit
description: Use when implementing utility functions, array operations, object manipulation, or string operations. ALWAYS use es-toolkit instead of custom implementations or native methods.
allowed-tools: Read, Grep, Glob
---

# es-toolkit Usage Guide

This skill provides guidelines and best practices for using the es-toolkit utility library in this project.

## Quick Reference

**MANDATORY**: Always use `es-toolkit` instead of custom implementations or native methods.

For detailed patterns, examples, and checklists, see:
- [references/patterns.md](references/patterns.md) - Complete usage patterns and migration guides

## Key Categories

| Category | Module | Common Functions |
|----------|--------|------------------|
| Array | `es-toolkit/array` | `compact`, `head`, `last`, `take`, `drop`, `uniq`, `chunk`, `flatten` |
| Object | `es-toolkit/object` | `merge`, `mergeWith`, `clone`, `cloneDeep`, `pick`, `omit` |
| String | `es-toolkit/string` | `trim`, `trimStart`, `trimEnd`, `kebabCase`, `camelCase`, `snakeCase` |
| Function | `es-toolkit/function` | `debounce`, `throttle`, `memoize`, `once` |
| Util | `es-toolkit/util` | `invariant` |

## Import Pattern

Always import from specific modules for optimal tree-shaking:

```typescript
// Good: Import from specific modules
import { compact } from "es-toolkit/array";
import { merge } from "es-toolkit/object";

// Bad: Import from root (larger bundle)
import { compact } from "es-toolkit";
```

## Documentation

- **Official Docs**: https://es-toolkit.dev/
- **GitHub**: https://github.com/toss/es-toolkit
