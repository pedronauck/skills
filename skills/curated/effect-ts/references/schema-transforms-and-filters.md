# Schema Transformations and Filters

Schema transformations for converting between types, filters for custom validation, and built-in refinements.

## Table of Contents

- [Schema.transform](#schematransform)
- [Schema.transformOrFail](#schematransformorfail)
- [Built-in Filters (Refinements)](#built-in-filters)
- [Custom Filters with Schema.filter](#custom-filters)
- [Composing Schemas](#composing-schemas)

## Schema.transform

Create a new schema that converts data between a source and target schema. Use when the transformation always succeeds:

```typescript
import * as Schema from "effect/Schema";

// Convert "on"/"off" to boolean
const BooleanFromString = Schema.transform(
  Schema.Literal("on", "off"), // Source: "on" | "off"
  Schema.Boolean,              // Target: boolean
  {
    strict: true,
    decode: (literal) => literal === "on",
    encode: (bool) => (bool ? "on" : "off"),
  }
);
// Schema<boolean, "on" | "off">

Schema.decodeUnknownSync(BooleanFromString)("on"); // true
Schema.encodeSync(BooleanFromString)(false);        // "off"
```

### Array to Set

```typescript
const ReadonlySetFromArray = <A, I, R>(
  itemSchema: Schema.Schema<A, I, R>
): Schema.Schema<ReadonlySet<A>, ReadonlyArray<I>, R> =>
  Schema.transform(
    Schema.Array(itemSchema),
    Schema.ReadonlySetFromSelf(Schema.typeSchema(itemSchema)),
    {
      strict: true,
      decode: (items) => new Set(items),
      encode: (set) => Array.from(set.values()),
    }
  );
```

### Composing Transformations

You can compose transformation schemas (source and/or target are themselves transformations):

```typescript
// NumberFromString: string -> number
// BooleanFromString: "on"|"off" -> boolean
// Composed: string -> boolean
const BooleanFromNumericString = Schema.transform(
  Schema.NumberFromString,  // string -> number
  BooleanFromString,        // "on"|"off" -> boolean
  {
    strict: true,
    decode: (n) => (n > 0 ? "on" : "off"),
    encode: (s) => (s === "on" ? 1 : -1),
  }
);

Schema.decodeUnknownSync(BooleanFromNumericString)("100"); // true
```

### Non-strict Mode

Use `strict: false` when types don't exactly align but the transformation is correct:

```typescript
const Clamped = (min: number, max: number) =>
  Schema.transform(Schema.Number, Schema.Number, {
    strict: false,
    decode: (n) => Math.min(Math.max(n, min), max),
    encode: (n) => n,
  });
```

## Schema.transformOrFail

Like `transform` but `decode`/`encode` return `Effect`, allowing failures:

```typescript
import * as Effect from "effect/Effect";
import * as ParseResult from "effect/ParseResult";

const StringToNumber = Schema.transformOrFail(
  Schema.String,
  Schema.Number,
  {
    strict: true,
    decode: (s, _, ast) => {
      const n = Number(s);
      return Number.isNaN(n)
        ? ParseResult.fail(new ParseResult.Type(ast, s, "Not a number"))
        : ParseResult.succeed(n);
    },
    encode: (n) => ParseResult.succeed(String(n)),
  }
);
```

### Async Transformations

`transformOrFail` supports async decode/encode:

```typescript
const UsernameFromId = Schema.transformOrFail(Schema.String, Schema.String, {
  strict: true,
  decode: (id, _, ast) =>
    Effect.tryPromise({
      try: () => fetchUsername(id),
      catch: () => new ParseResult.Type(ast, id, "Failed to fetch username"),
    }),
  encode: (name) => ParseResult.succeed(name),
});
```

## Built-in Filters

Effect provides many built-in refinement combinators. These add validation without changing the type:

### String Filters

```typescript
Schema.String.pipe(Schema.minLength(1));        // Non-empty
Schema.String.pipe(Schema.maxLength(255));       // Max length
Schema.String.pipe(Schema.length(10));           // Exact length
Schema.String.pipe(Schema.pattern(/^[a-z]+$/));  // Regex match
Schema.String.pipe(Schema.startsWith("https"));  // Prefix check
Schema.String.pipe(Schema.endsWith(".com"));     // Suffix check
Schema.String.pipe(Schema.includes("@"));        // Contains check
Schema.String.pipe(Schema.trimmed());            // No leading/trailing whitespace
Schema.String.pipe(Schema.lowercased());         // Must be lowercase
Schema.String.pipe(Schema.uppercased());         // Must be uppercase
Schema.NonEmptyString;                           // Shorthand for minLength(1)
```

### Number Filters

```typescript
Schema.Number.pipe(Schema.int());               // Integer only
Schema.Number.pipe(Schema.positive());           // > 0
Schema.Number.pipe(Schema.negative());           // < 0
Schema.Number.pipe(Schema.nonPositive());        // <= 0
Schema.Number.pipe(Schema.nonNegative());        // >= 0
Schema.Number.pipe(Schema.between(1, 100));      // Inclusive range
Schema.Number.pipe(Schema.greaterThan(0));       // > value
Schema.Number.pipe(Schema.lessThan(100));        // < value
Schema.Number.pipe(Schema.greaterThanOrEqualTo(0)); // >= value
Schema.Number.pipe(Schema.lessThanOrEqualTo(100));  // <= value
Schema.Number.pipe(Schema.multipleOf(5));        // Divisible by
Schema.Int;                                      // Shorthand for int()
```

### Array Filters

```typescript
Schema.Array(Schema.String).pipe(Schema.minItems(1));   // Non-empty array
Schema.Array(Schema.String).pipe(Schema.maxItems(10));   // Max items
Schema.Array(Schema.String).pipe(Schema.itemsCount(5));  // Exact count
Schema.NonEmptyArray(Schema.String);                     // Shorthand
```

### Combining with Branded Types

Filters compose naturally with branding:

```typescript
const Email = Schema.String.pipe(
  Schema.pattern(/^[^\s@]+@[^\s@]+\.[^\s@]+$/),
  Schema.brand("Email")
);
type Email = typeof Email.Type;

const Port = Schema.Int.pipe(
  Schema.between(1, 65535),
  Schema.brand("Port")
);
type Port = typeof Port.Type;

const Slug = Schema.String.pipe(
  Schema.pattern(/^[a-z0-9]+(?:-[a-z0-9]+)*$/),
  Schema.maxLength(128),
  Schema.brand("Slug")
);
type Slug = typeof Slug.Type;
```

## Custom Filters

Use `Schema.filter` for validation logic beyond built-in filters:

```typescript
const EvenNumber = Schema.Number.pipe(
  Schema.filter((n) => n % 2 === 0 || "must be even")
);

// Return type can be: true | undefined (pass), false (fail, no message),
// string (fail with message), or ParseResult.ParseIssue
```

### Multi-field Validation with Error Paths

Associate errors with specific fields in a struct:

```typescript
const PasswordForm = Schema.Struct({
  password: Schema.String.pipe(Schema.minLength(8)),
  confirm: Schema.String,
}).pipe(
  Schema.filter((form) => {
    if (form.password !== form.confirm) {
      return {
        path: ["confirm"],
        issue: "Passwords must match",
      };
    }
  })
);
```

### Multiple Validation Errors

Return an array to report multiple issues:

```typescript
const StrongPassword = Schema.String.pipe(
  Schema.filter((s) => {
    const errors: string[] = [];
    if (s.length < 8) errors.push("must be at least 8 characters");
    if (!/[A-Z]/.test(s)) errors.push("must contain uppercase letter");
    if (!/[0-9]/.test(s)) errors.push("must contain a digit");
    return errors.length > 0 ? errors : undefined;
  })
);
```

### Annotations for JSON Schema

Add metadata to custom filters for JSON Schema generation:

```typescript
const LongString = Schema.String.pipe(
  Schema.filter(
    (s) => s.length >= 10 || "must be at least 10 characters",
    {
      identifier: "LongString",
      jsonSchema: { minLength: 10 },
      description: "A string with at least 10 characters",
    }
  )
);
```

## Composing Schemas

### Schema.compose

Chain two schemas where the output of the first feeds the input of the second:

```typescript
// string -> number -> positive number
const PositiveFromString = Schema.compose(
  Schema.NumberFromString,
  Schema.Number.pipe(Schema.positive())
);
```

### Schema.attachPropertySignature

Add a constant property to a schema (useful for discriminated unions):

```typescript
const Circle = Schema.Struct({ radius: Schema.Number }).pipe(
  Schema.attachPropertySignature("kind", "circle")
);
// Decodes: { radius: 5 } -> { kind: "circle", radius: 5 }
// Encodes: { kind: "circle", radius: 5 } -> { radius: 5 }
```

### Common Built-in Transforms

Effect provides many pre-built transformation schemas:

```typescript
Schema.NumberFromString;       // string -> number
Schema.BooleanFromString;      // "true"/"false" -> boolean
Schema.Date;                   // string -> Date (ISO 8601)
Schema.DateFromSelf;           // Date -> Date (validates)
Schema.BigIntFromString;       // string -> BigInt
Schema.Trim;                   // string -> trimmed string
Schema.Lowercase;              // string -> lowercased string
Schema.Uppercase;              // string -> uppercased string
Schema.split(",");             // "a,b,c" -> ["a", "b", "c"]
Schema.parseJson(innerSchema); // JSON string -> parsed + validated
```
