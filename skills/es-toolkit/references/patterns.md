# es-toolkit Patterns and Best Practices

This document contains comprehensive patterns and best practices for using the es-toolkit utility library in this project.

## Core Principles

- **MANDATORY**: Always use `es-toolkit` instead of custom implementations or native methods
- **NEVER** implement custom utility functions that es-toolkit already provides
- **ALWAYS** check es-toolkit documentation before writing utility code
- **PREFER** es-toolkit over native methods for consistency and performance

## Import Patterns

Always import from specific modules for optimal tree-shaking:

```typescript
// Good: Import from specific modules
import { compact } from "es-toolkit/array";
import { merge, clone } from "es-toolkit/object";
import { trim } from "es-toolkit/string";
import { invariant } from "es-toolkit/util";

// Bad: Import from root (larger bundle)
import { compact } from "es-toolkit";
```

## Common Use Cases

### Array Operations

```typescript
import { compact, head, last, take, drop, uniq } from "es-toolkit/array";

// Filter empty values
const cleaned = compact([1, null, 2, undefined, 3]); // [1, 2, 3]

// Get first/last element
const first = head(array); // safer than array[0]
const lastItem = last(array); // safer than array[array.length - 1]

// Take/drop elements
const first3 = take(array, 3);
const withoutFirst3 = drop(array, 3);

// Remove duplicates
const unique = uniq([1, 2, 2, 3]); // [1, 2, 3]
```

### Object Operations

```typescript
import { merge, mergeWith, clone, cloneDeep, pick, omit } from "es-toolkit/object";

// Deep merge objects
const merged = merge({}, obj1, obj2);
const merged = mergeWith({}, obj1, obj2, customizer);

// Clone objects
const cloned = clone(obj); // shallow clone
const deepCloned = cloneDeep(obj); // deep clone

// Pick/omit properties
const picked = pick(obj, ["a", "b"]);
const omitted = omit(obj, ["c", "d"]);
```

### String Operations

```typescript
import { trim, trimStart, trimEnd, kebabCase, camelCase } from "es-toolkit/string";

const cleaned = trim("  hello  "); // "hello"
const kebab = kebabCase("HelloWorld"); // "hello-world"
const camel = camelCase("hello-world"); // "helloWorld"
```

### Utility Functions

```typescript
import { invariant } from "es-toolkit/util";
import { debounce, throttle, memoize } from "es-toolkit/function";

// Runtime assertions
invariant(condition, "Error message");

// Function utilities
const debounced = debounce(fn, 100);
const throttled = throttle(fn, 100);
const memoized = memoize(fn);
```

## When to Use es-toolkit

### Always Use es-toolkit For:

- **Array operations**: `compact`, `head`, `last`, `take`, `drop`, `uniq`, `chunk`, `flatten`
- **Object operations**: `merge`, `mergeWith`, `clone`, `cloneDeep`, `pick`, `omit`
- **String operations**: `trim`, `trimStart`, `trimEnd`, `kebabCase`, `camelCase`, `snakeCase`
- **Function utilities**: `debounce`, `throttle`, `memoize`, `once`
- **Runtime assertions**: `invariant` from `es-toolkit/util`
- **Type guards**: `isNil`, `isNotNil`, `isPlainObject`, `isPrimitive`

### When Native Methods Are Acceptable:

- Simple operations that don't have es-toolkit equivalents
- Operations where native performance is sufficient and es-toolkit doesn't add value
- Operations that are already optimized in the runtime (e.g., `Array.map`, `Array.filter` for simple cases)

## Migration Checklist

When refactoring existing code:

- [ ] Replace custom merge functions with `merge`/`mergeWith`
- [ ] Replace `array[0]` with `head(array)`
- [ ] Replace `array[array.length - 1]` with `last(array)`
- [ ] Replace `.filter(Boolean)` with `compact()`
- [ ] Replace spread operators for deep merging with `merge`
- [ ] Replace custom clone functions with `clone`/`cloneDeep`
- [ ] Replace `.trim()` with `trim` from es-toolkit
- [ ] Replace custom debounce/throttle with es-toolkit versions
- [ ] Replace `throw new Error()` assertions with `invariant()`

## Validation Checklist

Before finishing a task involving utility functions:

- [ ] Check that es-toolkit is used instead of custom implementations
- [ ] Verify imports are from specific modules (e.g., `es-toolkit/array`)
- [ ] Ensure no custom merge/clone functions exist
- [ ] Ensure no native array indexing for first/last elements
- [ ] Run type checks (`pnpm run typecheck`) and tests (`pnpm run test`)

## Documentation

- **Official Docs**: https://es-toolkit.dev/
- **GitHub**: https://github.com/toss/es-toolkit
