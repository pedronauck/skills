# XState v5 Patterns and Best Practices

This document provides comprehensive guidelines, patterns, and best practices for working with XState v5 state machines and actors.

## Table of Contents

1. [Machine Setup and Type Safety](#machine-setup-and-type-safety)
2. [Event Type Definitions](#event-type-definitions)
3. [Actions and Assign](#actions-and-assign)
4. [Guards](#guards)
5. [Context and Input](#context-and-input)
6. [Hierarchical States](#hierarchical-states)
7. [Parallel States](#parallel-states)
8. [Actors and Async Operations](#actors-and-async-operations)
9. [React Integration](#react-integration)
10. [Testing](#testing)
11. [Migration from v4](#migration-from-v4)

---

## Machine Setup and Type Safety

### Always Use the `setup()` API

The `setup()` API provides superior type inference and should be used for all machines:

```typescript
import { setup, createActor } from 'xstate';

export enum CounterEventType {
  INCREMENT = 'increment',
  DECREMENT = 'decrement',
  RESET = 'reset',
}

const counterMachineSetup = setup({
  types: {
    context: {} as { count: number; maxCount: number },
    events: {} as
      | { type: CounterEventType.INCREMENT }
      | { type: CounterEventType.DECREMENT }
      | { type: CounterEventType.RESET },
    input: {} as { initialCount?: number; maxCount?: number },
  },
  guards: {
    canIncrement: ({ context }) => context.count < context.maxCount,
    canDecrement: ({ context }) => context.count > 0,
  },
});

// Define actions OUTSIDE setup using type-bound helpers
const incrementCount = counterMachineSetup.assign({
  count: ({ context }) => context.count + 1,
});

const decrementCount = counterMachineSetup.assign({
  count: ({ context }) => context.count - 1,
});

const resetCount = counterMachineSetup.assign({
  count: 0,
});

export const counterMachine = counterMachineSetup.createMachine({
  id: 'counter',
  context: ({ input }) => ({
    count: input.initialCount ?? 0,
    maxCount: input.maxCount ?? 100,
  }),
  initial: 'active',
  states: {
    active: {
      on: {
        [CounterEventType.INCREMENT]: {
          guard: 'canIncrement',
          actions: incrementCount,
        },
        [CounterEventType.DECREMENT]: {
          guard: 'canDecrement',
          actions: decrementCount,
        },
        [CounterEventType.RESET]: {
          actions: resetCount,
        },
      },
    },
  },
});
```

### Type Inference Benefits

Using `setup()` provides:
- Automatic type inference for context, events, and input
- Type-safe guards and actions
- IDE autocompletion support
- Compile-time error checking

---

## Event Type Definitions

### Use Enums for Event Types

Always define event types using enums with UPPER_SNAKE_CASE naming:

```typescript
export enum FormEventType {
  INPUT_CHANGE = 'input.change',
  FIELD_BLUR = 'field.blur',
  FORM_SUBMIT = 'form.submit',
  FORM_RESET = 'form.reset',
  VALIDATION_ERROR = 'validation.error',
  SUBMIT_SUCCESS = 'submit.success',
  SUBMIT_FAILURE = 'submit.failure',
}

type FormEvent =
  | { type: FormEventType.INPUT_CHANGE; field: string; value: string }
  | { type: FormEventType.FIELD_BLUR; field: string }
  | { type: FormEventType.FORM_SUBMIT }
  | { type: FormEventType.FORM_RESET }
  | { type: FormEventType.VALIDATION_ERROR; errors: Record<string, string> }
  | { type: FormEventType.SUBMIT_SUCCESS; data: unknown }
  | { type: FormEventType.SUBMIT_FAILURE; error: Error };
```

### Event Payload Typing

Include payload types directly in the event union for type safety:

```typescript
type AuthEvent =
  | { type: 'auth.login'; credentials: { email: string; password: string } }
  | { type: 'auth.logout' }
  | { type: 'auth.refresh'; token: string }
  | { type: 'auth.error'; error: Error };
```

---

## Actions and Assign

### Define Actions Outside `setup()`

Always define actions outside the `setup()` call using type-bound helpers:

```typescript
const machineSetup = setup({
  types: {
    context: {} as { items: string[]; selectedIndex: number },
    events: {} as
      | { type: 'ADD_ITEM'; item: string }
      | { type: 'SELECT'; index: number },
  },
});

// Correct: Actions defined outside setup using type-bound helpers
const addItem = machineSetup.assign({
  items: ({ context, event }) => {
    if (event.type === 'ADD_ITEM') {
      return [...context.items, event.item];
    }
    return context.items;
  },
});

const selectItem = machineSetup.assign({
  selectedIndex: ({ event }) => {
    if (event.type === 'SELECT') {
      return event.index;
    }
    return 0;
  },
});
```

### Using `enqueueActions()` for Sequential Actions

Group related actions together using `enqueueActions()`:

```typescript
import { enqueueActions } from 'xstate';

const handleSubmit = enqueueActions(({ context, enqueue }) => {
  enqueue.assign({ isSubmitting: true });
  enqueue.assign({ error: null });

  if (context.formData.email) {
    enqueue({ type: 'logFormSubmission' });
  }
});
```

### Raise Actions

Use `raise()` to trigger internal events:

```typescript
import { raise } from 'xstate';

const machine = setup({
  // ...
}).createMachine({
  states: {
    idle: {
      on: {
        TRIGGER: {
          actions: raise({ type: 'INTERNAL_EVENT' }),
        },
        INTERNAL_EVENT: {
          target: 'processing',
        },
      },
    },
  },
});
```

---

## Guards

### Pure Guard Functions

Guards must be pure functions without side effects:

```typescript
const machineSetup = setup({
  types: {
    context: {} as { count: number; items: string[] },
    events: {} as { type: 'INCREMENT' } | { type: 'ADD_ITEM'; item: string },
  },
  guards: {
    // Good: Pure function
    canIncrement: ({ context }) => context.count < 100,

    // Good: Check based on context
    hasItems: ({ context }) => context.items.length > 0,

    // Good: Parameterized guard
    isGreaterThan: ({ context }, params: { value: number }) =>
      context.count > params.value,
  },
});
```

### Parameterized Guards

Use guard parameters for reusable logic:

```typescript
const machine = machineSetup.createMachine({
  states: {
    active: {
      on: {
        INCREMENT: {
          guard: { type: 'isGreaterThan', params: { value: 50 } },
          target: 'maxReached',
        },
      },
    },
  },
});
```

### Combining Guards

Use `and()`, `or()`, and `not()` for complex conditions:

```typescript
import { and, or, not } from 'xstate';

const machineSetup = setup({
  guards: {
    isAuthenticated: ({ context }) => context.user !== null,
    hasPermission: ({ context }) => context.permissions.includes('admin'),
    isNotBlocked: ({ context }) => !context.blocked,
  },
});

const machine = machineSetup.createMachine({
  states: {
    checking: {
      always: [
        {
          guard: and(['isAuthenticated', 'hasPermission', 'isNotBlocked']),
          target: 'authorized',
        },
        {
          guard: or(['isAuthenticated', 'hasPermission']),
          target: 'partialAccess',
        },
        {
          target: 'unauthorized',
        },
      ],
    },
  },
});
```

---

## Context and Input

### Initialize Context from Input

Always use the function form for dynamic context initialization:

```typescript
const machine = setup({
  types: {
    context: {} as { userId: string; preferences: UserPreferences },
    input: {} as { userId: string; preferences?: UserPreferences },
  },
}).createMachine({
  context: ({ input }) => ({
    userId: input.userId,
    preferences: input.preferences ?? defaultPreferences,
  }),
  // ...
});
```

### Creating Actors with Input

```typescript
const actor = createActor(machine, {
  input: {
    userId: 'user-123',
    preferences: { theme: 'dark' },
  },
});

actor.start();
```

---

## Hierarchical States

### Nested State Structure

Use hierarchical states to reduce duplication and organize related states:

```typescript
export enum LoadingEventType {
  FETCH = 'fetch',
  SUCCESS = 'success',
  FAILURE = 'failure',
  RETRY = 'retry',
  CANCEL = 'cancel',
}

const dataMachine = setup({
  types: {
    context: {} as { data: unknown; error: Error | null; retryCount: number },
    events: {} as
      | { type: LoadingEventType.FETCH }
      | { type: LoadingEventType.SUCCESS; data: unknown }
      | { type: LoadingEventType.FAILURE; error: Error }
      | { type: LoadingEventType.RETRY }
      | { type: LoadingEventType.CANCEL },
  },
}).createMachine({
  id: 'data',
  initial: 'idle',
  states: {
    idle: {
      on: {
        [LoadingEventType.FETCH]: 'loading',
      },
    },
    loading: {
      initial: 'fetching',
      states: {
        fetching: {
          invoke: {
            src: 'fetchData',
            onDone: {
              target: '#data.success',
              actions: 'setData',
            },
            onError: 'retrying',
          },
        },
        retrying: {
          after: {
            1000: 'fetching',
          },
        },
      },
      on: {
        [LoadingEventType.CANCEL]: 'idle',
      },
    },
    success: {
      on: {
        [LoadingEventType.FETCH]: 'loading',
      },
    },
    failure: {
      on: {
        [LoadingEventType.RETRY]: 'loading',
        [LoadingEventType.FETCH]: 'loading',
      },
    },
  },
});
```

---

## Parallel States

### Orthogonal Concerns

Use parallel states for independent, concurrent concerns:

```typescript
export enum UIEventType {
  TOGGLE_SIDEBAR = 'ui.toggleSidebar',
  TOGGLE_MODAL = 'ui.toggleModal',
  SET_THEME = 'ui.setTheme',
}

const uiMachine = setup({
  types: {
    context: {} as { theme: 'light' | 'dark' },
    events: {} as
      | { type: UIEventType.TOGGLE_SIDEBAR }
      | { type: UIEventType.TOGGLE_MODAL }
      | { type: UIEventType.SET_THEME; theme: 'light' | 'dark' },
  },
}).createMachine({
  id: 'ui',
  type: 'parallel',
  context: { theme: 'light' },
  states: {
    sidebar: {
      initial: 'closed',
      states: {
        open: {
          on: { [UIEventType.TOGGLE_SIDEBAR]: 'closed' },
        },
        closed: {
          on: { [UIEventType.TOGGLE_SIDEBAR]: 'open' },
        },
      },
    },
    modal: {
      initial: 'hidden',
      states: {
        visible: {
          on: { [UIEventType.TOGGLE_MODAL]: 'hidden' },
        },
        hidden: {
          on: { [UIEventType.TOGGLE_MODAL]: 'visible' },
        },
      },
    },
    theme: {
      initial: 'light',
      states: {
        light: {
          on: {
            [UIEventType.SET_THEME]: {
              guard: ({ event }) => event.theme === 'dark',
              target: 'dark',
            },
          },
        },
        dark: {
          on: {
            [UIEventType.SET_THEME]: {
              guard: ({ event }) => event.theme === 'light',
              target: 'light',
            },
          },
        },
      },
    },
  },
});
```

---

## Actors and Async Operations

### Promise Actors with `fromPromise()`

```typescript
import { fromPromise, setup } from 'xstate';

interface User {
  id: string;
  name: string;
  email: string;
}

const fetchUser = fromPromise(async ({ input }: { input: { userId: string } }): Promise<User> => {
  const response = await fetch(`/api/users/${input.userId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch user');
  }
  return response.json();
});

const userMachineSetup = setup({
  types: {
    context: {} as { user: User | null; error: Error | null },
    events: {} as { type: 'FETCH'; userId: string },
    input: {} as { userId?: string },
  },
  actors: {
    fetchUser,
  },
});

const userMachine = userMachineSetup.createMachine({
  id: 'user',
  initial: 'idle',
  context: { user: null, error: null },
  states: {
    idle: {
      on: {
        FETCH: 'loading',
      },
    },
    loading: {
      invoke: {
        src: 'fetchUser',
        input: ({ event }) => ({ userId: event.userId }),
        onDone: {
          target: 'success',
          actions: userMachineSetup.assign({
            user: ({ event }) => event.output,
          }),
        },
        onError: {
          target: 'failure',
          actions: userMachineSetup.assign({
            error: ({ event }) => event.error as Error,
          }),
        },
      },
    },
    success: {
      on: {
        FETCH: 'loading',
      },
    },
    failure: {
      on: {
        FETCH: 'loading',
      },
    },
  },
});
```

### Callback Actors with `fromCallback()`

```typescript
import { fromCallback } from 'xstate';

const websocketActor = fromCallback(({ sendBack, receive, input }) => {
  const socket = new WebSocket(input.url);

  socket.onmessage = (event) => {
    sendBack({ type: 'MESSAGE', data: JSON.parse(event.data) });
  };

  socket.onerror = () => {
    sendBack({ type: 'ERROR' });
  };

  socket.onclose = () => {
    sendBack({ type: 'DISCONNECTED' });
  };

  receive((event) => {
    if (event.type === 'SEND') {
      socket.send(JSON.stringify(event.data));
    }
  });

  return () => {
    socket.close();
  };
});
```

### Observable Actors with `fromObservable()`

```typescript
import { fromObservable } from 'xstate';
import { interval } from 'rxjs';
import { map } from 'rxjs/operators';

const timerActor = fromObservable(({ input }) =>
  interval(input.interval).pipe(map((count) => ({ type: 'TICK', count })))
);
```

### Spawning Child Actors

```typescript
import { spawn, setup } from 'xstate';

const parentMachine = setup({
  types: {
    context: {} as { childRef: ActorRef<typeof childMachine> | null },
    events: {} as { type: 'SPAWN_CHILD' } | { type: 'STOP_CHILD' },
  },
  actors: {
    child: childMachine,
  },
}).createMachine({
  context: { childRef: null },
  on: {
    SPAWN_CHILD: {
      actions: assign({
        childRef: ({ spawn }) => spawn('child', { id: 'myChild' }),
      }),
    },
    STOP_CHILD: {
      actions: stopChild('myChild'),
    },
  },
});
```

---

## React Integration

### Using `useMachine()`

For component-scoped machines:

```typescript
import { useMachine } from '@xstate/react';
import { useMemo } from 'react';

interface CounterProps {
  initialCount?: number;
  onCountChange?: (count: number) => void;
}

function Counter({ initialCount = 0, onCountChange }: CounterProps) {
  const machine = useMemo(
    () =>
      counterMachine.provide({
        actions: {
          notifyChange: ({ context }) => {
            onCountChange?.(context.count);
          },
        },
      }),
    [onCountChange]
  );

  const [state, send] = useMachine(machine, {
    input: { initialCount },
  });

  return (
    <div>
      <span>Count: {state.context.count}</span>
      <button onClick={() => send({ type: CounterEventType.INCREMENT })}>
        Increment
      </button>
      <button onClick={() => send({ type: CounterEventType.DECREMENT })}>
        Decrement
      </button>
    </div>
  );
}
```

### Using `useActorRef()` for Global Actors

For actors that live outside the component lifecycle:

```typescript
import { useActorRef, useSelector } from '@xstate/react';
import { createActor } from 'xstate';

// Create a global actor
const globalActor = createActor(appMachine).start();

function App() {
  const actorRef = useActorRef(appMachine);
  const currentState = useSelector(actorRef, (state) => state.value);
  const user = useSelector(actorRef, (state) => state.context.user);

  return (
    <div>
      <p>State: {JSON.stringify(currentState)}</p>
      <p>User: {user?.name}</p>
    </div>
  );
}
```

### Using `.provide()` for Action Overrides

Override actions with external methods via `.provide()`:

```typescript
function FormComponent({ onSubmit, onValidationError }) {
  const machine = useMemo(
    () =>
      formMachine.provide({
        actions: {
          submitForm: ({ context }) => onSubmit(context.formData),
          handleValidationError: ({ context }) =>
            onValidationError(context.errors),
        },
      }),
    [onSubmit, onValidationError]
  );

  const [state, send] = useMachine(machine);

  // ...
}
```

### Context Providers for Shared Actors

```typescript
import { createActorContext } from '@xstate/react';

const AuthContext = createActorContext(authMachine);

function App() {
  return (
    <AuthContext.Provider>
      <AuthenticatedApp />
    </AuthContext.Provider>
  );
}

function AuthenticatedApp() {
  const authActor = AuthContext.useActorRef();
  const isAuthenticated = AuthContext.useSelector(
    (state) => state.matches('authenticated')
  );

  return isAuthenticated ? <Dashboard /> : <LoginForm />;
}
```

---

## Testing

### Testing State Transitions

```typescript
import { describe, it, expect } from 'vitest';
import { createActor } from 'xstate';
import { counterMachine, CounterEventType } from './counter-machine';

describe('counterMachine', () => {
  it('should increment count', () => {
    const actor = createActor(counterMachine, {
      input: { initialCount: 0 },
    });
    actor.start();

    actor.send({ type: CounterEventType.INCREMENT });

    expect(actor.getSnapshot().context.count).toBe(1);
  });

  it('should not decrement below zero', () => {
    const actor = createActor(counterMachine, {
      input: { initialCount: 0 },
    });
    actor.start();

    actor.send({ type: CounterEventType.DECREMENT });

    expect(actor.getSnapshot().context.count).toBe(0);
  });

  it('should transition through states correctly', () => {
    const actor = createActor(fetchMachine);
    actor.start();

    expect(actor.getSnapshot().matches('idle')).toBe(true);

    actor.send({ type: 'FETCH' });
    expect(actor.getSnapshot().matches('loading')).toBe(true);
  });
});
```

### Testing with Mocked Actors

```typescript
import { createActor } from 'xstate';

describe('userMachine with mocked fetch', () => {
  it('should handle successful fetch', async () => {
    const mockUser = { id: '1', name: 'Test User', email: 'test@test.com' };

    const testMachine = userMachine.provide({
      actors: {
        fetchUser: fromPromise(async () => mockUser),
      },
    });

    const actor = createActor(testMachine);
    actor.start();

    actor.send({ type: 'FETCH', userId: '1' });

    await waitFor(() => {
      expect(actor.getSnapshot().matches('success')).toBe(true);
      expect(actor.getSnapshot().context.user).toEqual(mockUser);
    });
  });
});
```

### Testing Guards

```typescript
describe('guards', () => {
  it('should prevent increment when at max', () => {
    const actor = createActor(counterMachine, {
      input: { initialCount: 99, maxCount: 100 },
    });
    actor.start();

    actor.send({ type: CounterEventType.INCREMENT });
    expect(actor.getSnapshot().context.count).toBe(100);

    // Should not increment beyond max
    actor.send({ type: CounterEventType.INCREMENT });
    expect(actor.getSnapshot().context.count).toBe(100);
  });
});
```

---

## Migration from v4

### Deprecated APIs to Avoid

| v4 API | v5 Replacement |
|--------|----------------|
| `interpret()` | `createActor()` |
| `cond` | `guard` |
| `Machine()` | `setup().createMachine()` |
| Generic parameters | `setup({ types: {} })` |
| `actions` array in assign | `enqueueActions()` |
| `spawn()` in actions | `spawn()` from action params |

### Key Migration Steps

1. Replace `interpret()` with `createActor()`
2. Replace `cond` with `guard`
3. Replace `Machine()` with `setup().createMachine()`
4. Define actions outside `setup()` using type-bound helpers
5. Use enums for event types instead of string literals
6. Always call `.start()` on actors

---

## Common Pitfalls

### Do NOT

- Use generic parameters; use `setup()` instead
- Define actions inside `setup()`; define them outside using type-bound helpers
- Use string literals for event types; use enums instead
- Mutate context directly; always use `assign()`
- Create impure guards or guards with side effects
- Use deprecated v4 APIs (`interpret()`, `cond`, etc.)
- Forget to `.start()` actors

### DO

- Use `setup()` API for all machines
- Use enums with UPPER_SNAKE_CASE for event types
- Define actions outside `setup()` using type-bound helpers
- Use `enqueueActions()` for sequential actions
- Use `.provide()` for React integration
- Initialize context from `input` using function form
- Use hierarchical states to reduce duplication
- Use parallel states for orthogonal concerns

---

## Validation Checklist

Before completing any task involving XState:

- [ ] Machine uses `setup()` API for type safety
- [ ] Event types are defined using enums with UPPER_SNAKE_CASE
- [ ] Actions are defined outside `setup()` using type-bound helpers
- [ ] Context is initialized from `input` using function form
- [ ] Guards are pure functions without side effects
- [ ] React components use `useMachine()` or `useActorRef()`
- [ ] `.provide()` is used for action overrides in React
- [ ] Actors are properly started with `.start()`
- [ ] No deprecated v4 APIs are used
- [ ] Type checks pass (`pnpm run typecheck`)
- [ ] Tests pass (`pnpm run test`)
