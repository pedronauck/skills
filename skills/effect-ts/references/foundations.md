# Effect-TS Foundations

Foundational principles, setup, and import conventions for Effect-TS projects.

## Core Principles

1. **Effect is not just for async**: Use `Effect` for any fallible operation, even synchronous ones. Use `Either` and `Option` to describe **data**, not computations.

2. **Embrace immutability**: Use Effect's immutable data structure utilities from `Struct`, `Record`, `Array`, and `Chunk` modules.

3. **Type safety first**: Track errors and context in types. Avoid `any` and `unknown` at all costs. Use `Schema.Defect` for wrapping unknown errors from external libraries.

4. **Composition over inheritance**: Build programs by composing small, reusable Effects rather than using classes or OOP patterns.

## Project Setup

### Effect Language Service

Install the Effect Language Service for editor diagnostics and build-time type checking:

```bash
pnpm add -d @effect/language-service
```

Add the plugin to `tsconfig.json`:

```json
{
  "compilerOptions": {
    "plugins": [
      {
        "name": "@effect/language-service"
      }
    ]
  }
}
```

For VS Code or Cursor, add to `.vscode/settings.json`:

```json
{
  "typescript.tsdk": "./node_modules/typescript/lib",
  "typescript.enablePromptUseWorkspaceTsdk": true
}
```

Enable build-time diagnostics by adding to `package.json`:

```json
{
  "scripts": {
    "prepare": "effect-language-service patch"
  }
}
```

### TypeScript Configuration

#### For Bundled Apps (Vite, Webpack, esbuild)

```jsonc
{
  "compilerOptions": {
    // Build Performance
    "incremental": true,

    // Module System - for bundled apps
    "target": "ES2022",
    "module": "preserve",
    "moduleResolution": "bundler",
    "moduleDetection": "force",
    "noEmit": true,

    // Import Handling
    "verbatimModuleSyntax": true,

    // Type Safety
    "strict": true,
    "exactOptionalPropertyTypes": true,
    "noUnusedLocals": true,
    "noImplicitOverride": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,

    // Development
    "declarationMap": true,
    "sourceMap": true,
    "skipLibCheck": true,

    // Effect Integration
    "plugins": [{ "name": "@effect/language-service" }]
  }
}
```

#### For Libraries & Node.js Apps

```jsonc
{
  "compilerOptions": {
    // Build Performance
    "incremental": true,
    "composite": true,

    // Module System - for Node.js/libraries
    "target": "ES2022",
    "module": "NodeNext",
    "moduleDetection": "force",

    // Import Handling
    "verbatimModuleSyntax": true,
    "rewriteRelativeImportExtensions": true,

    // Type Safety
    "strict": true,
    "exactOptionalPropertyTypes": true,
    "noUnusedLocals": true,
    "noImplicitOverride": true,

    // Output
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "skipLibCheck": true,

    // Effect Integration
    "plugins": [{ "name": "@effect/language-service" }]
  }
}
```

**Rule of thumb:** Build tool compiling your code? Use `preserve` + `bundler`. TypeScript compiling your code? Use `NodeNext`.

## Module Import Convention

Always use `import * as` syntax to avoid conflicts with module names:

```typescript
// CORRECT
import * as Effect from "effect/Effect";
import * as Schema from "effect/Schema";
import * as Layer from "effect/Layer";
import * as Context from "effect/Context";
import * as Option from "effect/Option";
import * as Either from "effect/Either";
import * as Array from "effect/Array";
import * as Match from "effect/Match";
import { pipe, flow, identity } from "effect/Function";

// WRONG - avoid destructured imports
import { Effect, Schema } from "effect";
```

### Common Exports Pattern

Create a `common.ts` file for frequently used Effect modules:

```typescript
// common.ts
export * as Effect from "effect/Effect";
export * as Schema from "effect/Schema";
export * as Context from "effect/Context";
export * as Layer from "effect/Layer";
export * as Either from "effect/Either";
export * as Option from "effect/Option";
export * as Array from "effect/Array";
export * as Match from "effect/Match";
export { pipe, flow, identity } from "effect/Function";
```

