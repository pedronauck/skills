---
name: xstate
description: Comprehensive guide for XState v5 ecosystem including state machines, actors, @xstate/store, and TanStack Query integration. Use when implementing state machines, event-driven stores, client state management, or integrating XState with React and TanStack Query for data fetching orchestration.
allowed-tools: Read, Grep, Glob
---

# XState v5 Developer Guide

This skill provides comprehensive guidelines, patterns, and best practices for working with the XState v5 ecosystem in this project, including:

- **XState State Machines** - Finite state machines and actors for complex application logic
- **@xstate/store** - Simple event-driven stores for lightweight state management
- **XState + TanStack Query** - Integration patterns for data fetching orchestration

## Quick Reference

| Use Case | Tool | Reference |
|----------|------|-----------|
| Complex state flows, guards, hierarchical states | XState Machines | `references/machine-patterns.md` |
| Simple event-driven state, atoms, undo/redo | @xstate/store | `references/store-patterns.md` |
| Data fetching with state orchestration | XState + TanStack Query | `references/query-patterns.md` |

## Core Principles

### XState State Machines
- **Explicit States**: Model application logic as explicit finite states and events
- **Actor Model**: Embrace the actor model for complex orchestration
- **Impossible States**: Use statecharts to eliminate impossible states
- **Declarative Thinking**: Think declaratively about state transitions
- **Visualization**: Use Stately Editor for visual machine creation and debugging

### @xstate/store
- **Event-Driven Updates**: Use events for all state updates (never direct mutations)
- **Keep Stores Simple**: Focus on data management, not complex logic
- **Optimized Subscriptions**: Leverage selectors for efficient state access
- **Reactive State**: Use atoms for composable, reactive state
- **Upgrade Path**: Migrate to XState machines when complexity grows

### XState + TanStack Query Integration
- **XState for Orchestration**: Use XState machines for workflow orchestration
- **TanStack Query for Data**: Use TanStack Query for data fetching and caching
- **Actors as Bridges**: Wrap Query operations as XState actors
- **Cache Updates in Mutations**: Keep query cache updates in mutation callbacks

---

## XState State Machines

### Creating a Machine with setup() API

Always use the `setup()` API for type-safe machines:

```typescript
import { setup, createActor } from 'xstate';

export enum CounterEventType {
  INCREMENT = 'increment',
  DECREMENT = 'decrement',
}

const counterMachineSetup = setup({
  types: {
    context: {} as { count: number },
    events: {} as
      | { type: CounterEventType.INCREMENT }
      | { type: CounterEventType.DECREMENT },
    input: {} as { initialCount: number },
  },
  guards: {
    isPositive: ({ context }) => context.count > 0,
  },
});

// Define actions OUTSIDE setup using type-bound helpers
const incrementCount = counterMachineSetup.assign({
  count: ({ context }) => context.count + 1,
});

export const counterMachine = counterMachineSetup.createMachine({
  id: 'counter',
  context: ({ input }) => ({ count: input.initialCount }),
  initial: 'active',
  states: {
    active: {
      on: {
        [CounterEventType.INCREMENT]: {
          actions: incrementCount,
        },
      },
    },
  },
});
```

### React Integration

Use `useMachine()` for component-scoped machines and `.provide()` for action overrides:

```typescript
import { useMachine } from '@xstate/react';
import { useMemo } from 'react';

function Counter({ onExternalAction }) {
  const machine = useMemo(
    () =>
      counterMachine.provide({
        actions: {
          logEvent: () => onExternalAction(),
        },
      }),
    [onExternalAction]
  );

  const [state, send] = useMachine(machine);

  return (
    <button onClick={() => send({ type: CounterEventType.INCREMENT })}>
      Count: {state.context.count}
    </button>
  );
}
```

**For detailed patterns**: See `references/machine-patterns.md`

---

## @xstate/store

### Creating a Store

Define stores with clear initial context and event-based transitions:

```typescript
import { createStore } from '@xstate/store';

const userStore = createStore({
  context: {
    user: null as { id: string; name: string } | null,
    isLoading: false,
    error: null as string | null,
  },
  on: {
    setUser: (context, event: { user: { id: string; name: string } }) => ({
      ...context, // Always spread to preserve other properties
      user: event.user,
      error: null,
    }),
    setLoading: (context, event: { isLoading: boolean }) => ({
      ...context,
      isLoading: event.isLoading,
    }),
  },
});

// Use the trigger API for type-safe event sending
userStore.trigger.setUser({ user: { id: '1', name: 'John' } });
```

### React Integration

```typescript
import { useSelector, useStore } from '@xstate/store/react';

function Counter() {
  const store = useStore({
    context: { count: 0 },
    on: {
      increment: (context, event: { by: number }) => ({
        ...context,
        count: context.count + event.by,
      }),
    },
  });
  const count = useSelector(store, (state) => state.context.count);
  return <button onClick={() => store.trigger.increment({ by: 1 })}>{count}</button>;
}
```

### Undo/Redo Pattern

```typescript
import { createStore } from '@xstate/store';
import { undoRedo } from '@xstate/store/undo';

const editorStore = createStore(
  undoRedo({
    context: { text: '' },
    on: {
      insertText: (context, event: { text: string }) => ({
        ...context,
        text: context.text + event.text,
      }),
    },
  })
);

editorStore.trigger.undo();
editorStore.trigger.redo();
```

**For detailed patterns**: See `references/store-patterns.md`

---

## XState + TanStack Query Integration

### Query Subscriptions with QueryObserver

Use `fromCallback` with `QueryObserver` for reactive subscriptions:

```typescript
import { fromCallback } from "xstate";
import { QueryObserver, type QueryClient } from "@tanstack/react-query";

const subscribeToQuery = fromCallback(({ input, sendBack }) => {
  const { queryClient, entityId } = input as {
    queryClient: QueryClient;
    entityId: string;
  };

  const observer = new QueryObserver(queryClient, {
    queryKey: ["data", entityId],
    queryFn: async () => { /* fetch logic */ },
  });

  const unsubscribe = observer.subscribe((result) => {
    if (result.data) {
      sendBack({ type: "REMOTE_UPDATE", data: result.data });
    }
  });

  // Emit current result immediately
  const currentResult = observer.getCurrentResult();
  if (currentResult.data) {
    sendBack({ type: "REMOTE_UPDATE", data: currentResult.data });
  }

  return () => unsubscribe();
});
```

### Mutations with useMutation

Wrap `useMutation` hooks as `fromPromise` actors and provide via `.provide()`:

```typescript
const machine = useMemo(
  () =>
    createDataMachine().provide({
      actors: {
        saveData: fromPromise(async ({ input }) => {
          return await saveMutation.mutateAsync(input.data);
        }),
      },
    }),
  [saveMutation]
);
```

**For detailed patterns**: See `references/query-patterns.md`

---

## Essential Patterns (All Tools)

1. **Use `setup()` for all machines** - provides superior type inference
2. **Use enums for event types** - UPPER_SNAKE_CASE convention
3. **Define actions outside `setup()`** - use type-bound helpers like `setup().assign()`
4. **Use `enqueueActions()` for sequential actions** - group related actions together
5. **Use `.provide()` for React integration** - override actions with external methods
6. **Initialize context from `input`** - use function form for dynamic initialization
7. **Always spread `...context` in stores** - preserve other properties
8. **Clean up subscriptions** - return cleanup functions from callback actors

---

## When to Use Each Tool

### Use XState State Machines When:
- Need finite states with specific transitions
- Need guards and conditional transition logic
- Need invoked actors for async orchestration
- Need hierarchical or parallel states
- Building complex multi-step workflows

### Use @xstate/store When:
- Simple global or local state management
- Event-driven state updates without complex flows
- Need undo/redo functionality
- Want a lightweight alternative with upgrade path to XState

### Use XState + TanStack Query When:
- Need to orchestrate data fetching with UI state
- Building real-time features with cache synchronization
- Managing complex async workflows with server state

---

## Common Pitfalls to Avoid

### All XState Tools
- Don't use generic parameters; use `setup()` instead
- Don't define actions inside `setup()`; define them outside using type-bound helpers
- Don't use string literals for event types; use enums instead
- Don't mutate context directly; always use `assign()` or return new objects
- Don't make guards impure or with side effects
- Don't use deprecated v4 APIs (`interpret()`, `cond`, etc.)
- Don't forget to `.start()` actors

### @xstate/store Specific
- Never forget to spread `...context` in returns
- Never subscribe without cleanup
- Never use stores for complex state machines (migrate to XState)

### TanStack Query Integration
- Don't create QueryObserver outside callback actors
- Don't update query cache inside machine actions
- Don't pass mutation hooks directly to actors (wrap in `fromPromise`)
- Don't access QueryClient from closure; pass through context

---

## Validation Checklist

Before finishing any task involving XState ecosystem:

### For State Machines
- [ ] Machine uses `setup()` API for type safety
- [ ] Event types are defined using enums
- [ ] Actions are defined outside `setup()` using type-bound helpers
- [ ] Context is initialized from `input` using function form
- [ ] Guards are pure functions without side effects
- [ ] React components use `useMachine()` or `useActorRef()`

### For @xstate/store
- [ ] Always spread `...context` in transition return values
- [ ] Use `trigger` API for type-safe event sending
- [ ] Create selectors for optimized subscriptions
- [ ] Clean up subscriptions in React components

### For TanStack Query Integration
- [ ] QueryObserver subscriptions are wrapped in `fromCallback`
- [ ] Mutations are wrapped in `fromPromise` and provided via `.provide()`
- [ ] Query cache updates happen in mutation callbacks, not machine actions
- [ ] Cleanup functions are returned from callback actors
- [ ] QueryClient is passed through machine input/context

### Always
- [ ] Run type checks (`pnpm run typecheck`)
- [ ] Run tests (`pnpm run test`)

---

## Detailed Reference Documentation

For comprehensive patterns, examples, and in-depth guidance, consult these reference files:

- **`references/machine-patterns.md`** - Complete XState machine patterns including hierarchical states, parallel states, actors, testing, and migration from v4
- **`references/store-patterns.md`** - Full @xstate/store patterns including selectors, atoms, effects, undo/redo, and when to migrate to machines
- **`references/query-patterns.md`** - Complete TanStack Query integration patterns with QueryObserver, mutations, and full machine examples
