# XState Store Patterns and Best Practices

This document provides comprehensive patterns and code examples for working with @xstate/store.

## Table of Contents

- [Core Concepts](#core-concepts)
- [Store Creation Patterns](#store-creation-patterns)
- [Selector Patterns](#selector-patterns)
- [React Integration Patterns](#react-integration-patterns)
- [Effects and Emissions](#effects-and-emissions)
- [Atom Patterns](#atom-patterns)
- [Undo/Redo Patterns](#undoredo-patterns)
- [Migration Patterns](#migration-patterns)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)

---

## Core Concepts

### Event-Driven State Updates

@xstate/store uses an event-driven architecture where all state changes happen through events:

```typescript
import { createStore } from '@xstate/store';

// Events are the ONLY way to update state
const store = createStore({
  context: { count: 0 },
  on: {
    // Event handler receives current context and event payload
    increment: (context, event: { by: number }) => ({
      ...context, // ALWAYS spread context
      count: context.count + event.by,
    }),
  },
});

// Type-safe event dispatch via trigger API
store.trigger.increment({ by: 1 });
```

### Immutable Context Updates

Context must NEVER be mutated directly. Always return a new object:

```typescript
// CORRECT - Returns new object with spread
on: {
  updateUser: (context, event: { name: string }) => ({
    ...context,
    user: { ...context.user, name: event.name },
  }),
}

// WRONG - Direct mutation
on: {
  updateUser: (context, event: { name: string }) => {
    context.user.name = event.name; // NEVER do this
    return context;
  },
}
```

---

## Store Creation Patterns

### Basic Store

```typescript
import { createStore } from '@xstate/store';

interface User {
  id: string;
  name: string;
  email: string;
}

interface UserStoreContext {
  user: User | null;
  isLoading: boolean;
  error: string | null;
}

const userStore = createStore({
  context: {
    user: null,
    isLoading: false,
    error: null,
  } as UserStoreContext,
  on: {
    setUser: (context, event: { user: User }) => ({
      ...context,
      user: event.user,
      error: null,
    }),
    setLoading: (context, event: { isLoading: boolean }) => ({
      ...context,
      isLoading: event.isLoading,
    }),
    setError: (context, event: { error: string }) => ({
      ...context,
      error: event.error,
      isLoading: false,
    }),
    clearError: (context) => ({
      ...context,
      error: null,
    }),
  },
});

export { userStore };
```

### Store with Complex Types

```typescript
import { createStore } from '@xstate/store';

interface TodoItem {
  id: string;
  text: string;
  completed: boolean;
  createdAt: Date;
}

interface TodoFilter {
  status: 'all' | 'active' | 'completed';
  searchQuery: string;
}

const todoStore = createStore({
  context: {
    todos: [] as TodoItem[],
    filter: { status: 'all', searchQuery: '' } as TodoFilter,
    selectedId: null as string | null,
  },
  on: {
    addTodo: (context, event: { text: string }) => ({
      ...context,
      todos: [
        ...context.todos,
        {
          id: crypto.randomUUID(),
          text: event.text,
          completed: false,
          createdAt: new Date(),
        },
      ],
    }),
    toggleTodo: (context, event: { id: string }) => ({
      ...context,
      todos: context.todos.map((todo) =>
        todo.id === event.id ? { ...todo, completed: !todo.completed } : todo
      ),
    }),
    removeTodo: (context, event: { id: string }) => ({
      ...context,
      todos: context.todos.filter((todo) => todo.id !== event.id),
    }),
    setFilter: (context, event: { filter: Partial<TodoFilter> }) => ({
      ...context,
      filter: { ...context.filter, ...event.filter },
    }),
    selectTodo: (context, event: { id: string | null }) => ({
      ...context,
      selectedId: event.id,
    }),
  },
});
```

### Store Factory Pattern

Create reusable store factories for similar use cases:

```typescript
import { createStore } from '@xstate/store';

interface PaginatedListContext<T> {
  items: T[];
  page: number;
  pageSize: number;
  total: number;
  isLoading: boolean;
}

function createPaginatedListStore<T>(initialPageSize = 10) {
  return createStore({
    context: {
      items: [] as T[],
      page: 1,
      pageSize: initialPageSize,
      total: 0,
      isLoading: false,
    } as PaginatedListContext<T>,
    on: {
      setItems: (context, event: { items: T[]; total: number }) => ({
        ...context,
        items: event.items,
        total: event.total,
        isLoading: false,
      }),
      setPage: (context, event: { page: number }) => ({
        ...context,
        page: event.page,
      }),
      setPageSize: (context, event: { pageSize: number }) => ({
        ...context,
        pageSize: event.pageSize,
        page: 1, // Reset to first page
      }),
      setLoading: (context, event: { isLoading: boolean }) => ({
        ...context,
        isLoading: event.isLoading,
      }),
    },
  });
}

// Usage
const usersListStore = createPaginatedListStore<User>();
const productsListStore = createPaginatedListStore<Product>(20);
```

---

## Selector Patterns

### Basic Selectors

```typescript
import { createStore, shallowEqual } from '@xstate/store';

const appStore = createStore({
  context: {
    user: { id: '1', name: 'John', preferences: { theme: 'dark' } },
    notifications: [] as Notification[],
    settings: { language: 'en', timezone: 'UTC' },
  },
  on: { /* ... */ },
});

// Simple selector
const userSelector = appStore.select((state) => state.context.user);

// Nested property selector
const themeSelector = appStore.select(
  (state) => state.context.user.preferences.theme
);

// Object selector with shallowEqual comparison
const userObjectSelector = appStore.select(
  (state) => state.context.user,
  shallowEqual
);

// Subscribe to selector changes
const unsubscribe = userSelector.subscribe((user) => {
  console.log('User changed:', user);
});
```

### Derived Selectors

```typescript
const todoStore = createStore({
  context: {
    todos: [] as TodoItem[],
    filter: 'all' as 'all' | 'active' | 'completed',
  },
  on: { /* ... */ },
});

// Count selector
const todoCountSelector = todoStore.select(
  (state) => state.context.todos.length
);

// Computed/derived selector
const filteredTodosSelector = todoStore.select((state) => {
  const { todos, filter } = state.context;
  switch (filter) {
    case 'active':
      return todos.filter((t) => !t.completed);
    case 'completed':
      return todos.filter((t) => t.completed);
    default:
      return todos;
  }
}, shallowEqual);

// Stats selector
const todoStatsSelector = todoStore.select((state) => {
  const todos = state.context.todos;
  return {
    total: todos.length,
    completed: todos.filter((t) => t.completed).length,
    active: todos.filter((t) => !t.completed).length,
  };
}, shallowEqual);
```

### Parameterized Selectors

```typescript
// Create selector factory for parameterized queries
function createTodoByIdSelector(id: string) {
  return todoStore.select((state) =>
    state.context.todos.find((t) => t.id === id)
  );
}

// Usage
const todoSelector = createTodoByIdSelector('todo-123');
const todo = todoSelector.get();
```

---

## React Integration Patterns

### useSelector Hook

```typescript
import { useSelector } from '@xstate/store/react';
import { shallowEqual } from '@xstate/store';

// Basic usage
function UserProfile() {
  const user = useSelector(userStore, (state) => state.context.user);

  if (!user) return <div>Loading...</div>;
  return <div>{user.name}</div>;
}

// With shallowEqual for objects
function UserPreferences() {
  const preferences = useSelector(
    userStore,
    (state) => state.context.user?.preferences,
    shallowEqual
  );

  return <div>Theme: {preferences?.theme}</div>;
}

// Multiple selectors in one component
function Dashboard() {
  const user = useSelector(userStore, (state) => state.context.user);
  const todos = useSelector(todoStore, (state) => state.context.todos);
  const settings = useSelector(settingsStore, (state) => state.context);

  return (
    <div>
      <h1>Welcome, {user?.name}</h1>
      <p>You have {todos.length} todos</p>
      <p>Language: {settings.language}</p>
    </div>
  );
}
```

### useStore Hook for Local State

```typescript
import { useStore, useSelector } from '@xstate/store/react';

function Counter() {
  const store = useStore({
    context: { count: 0 },
    on: {
      increment: (context, event: { by: number }) => ({
        ...context,
        count: context.count + event.by,
      }),
      decrement: (context, event: { by: number }) => ({
        ...context,
        count: context.count - event.by,
      }),
      reset: (context) => ({
        ...context,
        count: 0,
      }),
    },
  });

  const count = useSelector(store, (state) => state.context.count);

  return (
    <div>
      <button onClick={() => store.trigger.decrement({ by: 1 })}>-</button>
      <span>{count}</span>
      <button onClick={() => store.trigger.increment({ by: 1 })}>+</button>
      <button onClick={() => store.trigger.reset()}>Reset</button>
    </div>
  );
}
```

### Custom Hooks Pattern

```typescript
import { useSelector } from '@xstate/store/react';
import { shallowEqual } from '@xstate/store';

// Encapsulate store access in custom hooks
export function useUser() {
  return useSelector(userStore, (state) => state.context.user);
}

export function useUserLoading() {
  return useSelector(userStore, (state) => state.context.isLoading);
}

export function useUserError() {
  return useSelector(userStore, (state) => state.context.error);
}

// Actions hook
export function useUserActions() {
  return {
    setUser: (user: User) => userStore.trigger.setUser({ user }),
    setLoading: (isLoading: boolean) => userStore.trigger.setLoading({ isLoading }),
    setError: (error: string) => userStore.trigger.setError({ error }),
    clearError: () => userStore.trigger.clearError(),
  };
}

// Combined hook
export function useUserStore() {
  const user = useUser();
  const isLoading = useUserLoading();
  const error = useUserError();
  const actions = useUserActions();

  return { user, isLoading, error, ...actions };
}
```

---

## Effects and Emissions

### Using emits for Side Effects

```typescript
import { createStore } from '@xstate/store';

const todoStore = createStore({
  context: {
    todos: [] as TodoItem[],
    syncStatus: 'idle' as 'idle' | 'syncing' | 'error',
  },
  emits: {
    todoAdded: (payload: { todo: TodoItem }) => {},
    todoRemoved: (payload: { id: string }) => {},
    syncStarted: () => {},
    syncCompleted: () => {},
    syncFailed: (payload: { error: string }) => {},
  },
  on: {
    addTodo: (context, event: { text: string }, enqueue) => {
      const newTodo: TodoItem = {
        id: crypto.randomUUID(),
        text: event.text,
        completed: false,
        createdAt: new Date(),
      };

      // Emit event for side effects
      enqueue.emit.todoAdded({ todo: newTodo });

      // Queue async effect
      enqueue.effect(async () => {
        await saveTodoToServer(newTodo);
      });

      return {
        ...context,
        todos: [...context.todos, newTodo],
      };
    },
    removeTodo: (context, event: { id: string }, enqueue) => {
      enqueue.emit.todoRemoved({ id: event.id });

      enqueue.effect(async () => {
        await deleteTodoFromServer(event.id);
      });

      return {
        ...context,
        todos: context.todos.filter((t) => t.id !== event.id),
      };
    },
  },
});

// Subscribe to emitted events
todoStore.on('todoAdded', ({ todo }) => {
  console.log('Todo added:', todo.text);
  showNotification(`Added: ${todo.text}`);
});

todoStore.on('todoRemoved', ({ id }) => {
  console.log('Todo removed:', id);
});
```

### Effect Cleanup

```typescript
const searchStore = createStore({
  context: {
    query: '',
    results: [] as SearchResult[],
    isSearching: false,
  },
  on: {
    search: (context, event: { query: string }, enqueue) => {
      // Effect with cleanup
      enqueue.effect(() => {
        const controller = new AbortController();

        searchApi(event.query, { signal: controller.signal })
          .then((results) => {
            searchStore.trigger.setResults({ results });
          })
          .catch((error) => {
            if (error.name !== 'AbortError') {
              searchStore.trigger.setError({ error: error.message });
            }
          });

        // Return cleanup function
        return () => controller.abort();
      });

      return {
        ...context,
        query: event.query,
        isSearching: true,
      };
    },
    setResults: (context, event: { results: SearchResult[] }) => ({
      ...context,
      results: event.results,
      isSearching: false,
    }),
  },
});
```

---

## Atom Patterns

### Basic Atoms

```typescript
import { createAtom } from '@xstate/store';
import { useAtom } from '@xstate/store/react';

// Simple atom
const countAtom = createAtom(0);

// Read atom value
console.log(countAtom.get()); // 0

// Set atom value
countAtom.set(5);

// Update with callback
countAtom.set((current) => current + 1);

// Subscribe to changes
const unsubscribe = countAtom.subscribe((value) => {
  console.log('Count changed:', value);
});
```

### Derived Atoms

```typescript
import { createAtom } from '@xstate/store';

const countAtom = createAtom(0);
const multiplierAtom = createAtom(2);

// Derived atom - computed from other atoms
const multipliedAtom = createAtom(() => countAtom.get() * multiplierAtom.get());

// Derived atom updates automatically when dependencies change
countAtom.set(5);
console.log(multipliedAtom.get()); // 10

multiplierAtom.set(3);
console.log(multipliedAtom.get()); // 15
```

### Atoms in React

```typescript
import { useAtom } from '@xstate/store/react';
import { createAtom } from '@xstate/store';

const themeAtom = createAtom<'light' | 'dark'>('light');
const fontSizeAtom = createAtom(14);

function ThemeToggle() {
  const theme = useAtom(themeAtom);

  return (
    <button onClick={() => themeAtom.set(theme === 'light' ? 'dark' : 'light')}>
      Toggle Theme ({theme})
    </button>
  );
}

function FontSizeControl() {
  const fontSize = useAtom(fontSizeAtom);

  return (
    <div>
      <button onClick={() => fontSizeAtom.set((s) => s - 1)}>-</button>
      <span>{fontSize}px</span>
      <button onClick={() => fontSizeAtom.set((s) => s + 1)}>+</button>
    </div>
  );
}
```

### Atom Families

```typescript
import { createAtom } from '@xstate/store';

// Atom family pattern - create atoms with IDs
const todoAtomFamily = new Map<string, ReturnType<typeof createAtom<boolean>>>();

function getTodoCompletedAtom(id: string) {
  if (!todoAtomFamily.has(id)) {
    todoAtomFamily.set(id, createAtom(false));
  }
  return todoAtomFamily.get(id)!;
}

// Usage
const todo1Atom = getTodoCompletedAtom('todo-1');
const todo2Atom = getTodoCompletedAtom('todo-2');

todo1Atom.set(true);
console.log(todo1Atom.get()); // true
console.log(todo2Atom.get()); // false
```

---

## Undo/Redo Patterns

### Basic Undo/Redo

```typescript
import { createStore } from '@xstate/store';
import { undoRedo } from '@xstate/store/undo';

const editorStore = createStore(
  undoRedo({
    context: {
      content: '',
      cursorPosition: 0,
    },
    on: {
      insertText: (context, event: { text: string }) => ({
        ...context,
        content: context.content + event.text,
        cursorPosition: context.cursorPosition + event.text.length,
      }),
      deleteText: (context, event: { count: number }) => ({
        ...context,
        content: context.content.slice(0, -event.count),
        cursorPosition: Math.max(0, context.cursorPosition - event.count),
      }),
      moveCursor: (context, event: { position: number }) => ({
        ...context,
        cursorPosition: event.position,
      }),
    },
  })
);

// Use undo/redo
editorStore.trigger.insertText({ text: 'Hello' });
editorStore.trigger.insertText({ text: ' World' });
console.log(editorStore.getSnapshot().context.content); // "Hello World"

editorStore.trigger.undo();
console.log(editorStore.getSnapshot().context.content); // "Hello"

editorStore.trigger.redo();
console.log(editorStore.getSnapshot().context.content); // "Hello World"
```

### Undo/Redo with Skip Events

```typescript
import { createStore } from '@xstate/store';
import { undoRedo } from '@xstate/store/undo';

const editorStore = createStore(
  undoRedo(
    {
      context: {
        content: '',
        cursorPosition: 0,
        isModified: false,
      },
      on: {
        insertText: (context, event: { text: string }) => ({
          ...context,
          content: context.content + event.text,
          isModified: true,
        }),
        moveCursor: (context, event: { position: number }) => ({
          ...context,
          cursorPosition: event.position,
        }),
        save: (context) => ({
          ...context,
          isModified: false,
        }),
      },
    },
    {
      // Skip certain events from history
      skipEvent: (event) => {
        // Don't record cursor movements or save actions
        return event.type === 'moveCursor' || event.type === 'save';
      },
    }
  )
);
```

### Undo/Redo in React

```typescript
import { useSelector } from '@xstate/store/react';

function Editor() {
  const content = useSelector(editorStore, (state) => state.context.content);
  const canUndo = useSelector(
    editorStore,
    (state) => state.context._history?.past.length > 0
  );
  const canRedo = useSelector(
    editorStore,
    (state) => state.context._history?.future.length > 0
  );

  return (
    <div>
      <div>
        <button
          onClick={() => editorStore.trigger.undo()}
          disabled={!canUndo}
        >
          Undo
        </button>
        <button
          onClick={() => editorStore.trigger.redo()}
          disabled={!canRedo}
        >
          Redo
        </button>
      </div>
      <textarea
        value={content}
        onChange={(e) =>
          editorStore.trigger.insertText({ text: e.target.value })
        }
      />
    </div>
  );
}
```

---

## Migration Patterns

### When to Migrate to XState Machines

Consider migrating from @xstate/store to XState machines when:

1. **Need finite states**: Multiple distinct states with specific transitions
2. **Need guards**: Conditional logic for transitions
3. **Need invoked actors**: Async operations as part of state machine
4. **Need hierarchical states**: Nested state machines
5. **Need parallel states**: Multiple independent state regions

### Migration Example

```typescript
// Before: @xstate/store
const authStore = createStore({
  context: {
    user: null as User | null,
    isLoading: false,
    error: null as string | null,
  },
  on: {
    login: (context, event: { credentials: Credentials }) => {
      // Complex logic that would benefit from states
      return { ...context, isLoading: true };
    },
    loginSuccess: (context, event: { user: User }) => ({
      ...context,
      user: event.user,
      isLoading: false,
    }),
    loginFailure: (context, event: { error: string }) => ({
      ...context,
      error: event.error,
      isLoading: false,
    }),
  },
});

// After: XState machine
import { createMachine, assign } from 'xstate';

const authMachine = createMachine({
  id: 'auth',
  initial: 'idle',
  context: {
    user: null as User | null,
    error: null as string | null,
  },
  states: {
    idle: {
      on: {
        LOGIN: 'authenticating',
      },
    },
    authenticating: {
      invoke: {
        src: 'loginService',
        onDone: {
          target: 'authenticated',
          actions: assign({ user: (_, event) => event.data }),
        },
        onError: {
          target: 'error',
          actions: assign({ error: (_, event) => event.data.message }),
        },
      },
    },
    authenticated: {
      on: {
        LOGOUT: 'idle',
      },
    },
    error: {
      on: {
        RETRY: 'authenticating',
        CLEAR_ERROR: 'idle',
      },
    },
  },
});
```

---

## Anti-Patterns to Avoid

### 1. Direct Context Mutation

```typescript
// WRONG
on: {
  addItem: (context, event) => {
    context.items.push(event.item); // NEVER mutate
    return context;
  },
}

// CORRECT
on: {
  addItem: (context, event) => ({
    ...context,
    items: [...context.items, event.item],
  }),
}
```

### 2. Forgetting to Spread Context

```typescript
// WRONG - Other properties are lost
on: {
  setUser: (context, event) => ({
    user: event.user, // isLoading and error are lost!
  }),
}

// CORRECT
on: {
  setUser: (context, event) => ({
    ...context, // Preserve other properties
    user: event.user,
  }),
}
```

### 3. Not Cleaning Up Subscriptions

```typescript
// WRONG - Memory leak
useEffect(() => {
  userStore.subscribe((state) => {
    console.log(state);
  });
}, []);

// CORRECT
useEffect(() => {
  const unsubscribe = userStore.subscribe((state) => {
    console.log(state);
  });
  return unsubscribe; // Clean up on unmount
}, []);
```

### 4. Using Store for Complex State Machines

```typescript
// WRONG - Using store for complex state logic
const checkoutStore = createStore({
  context: {
    step: 'cart' as 'cart' | 'shipping' | 'payment' | 'confirmation',
    canGoBack: false,
    canGoForward: true,
    // ... complex state management
  },
  on: {
    nextStep: (context) => {
      // Complex conditional logic
      if (context.step === 'cart' && hasItems()) {
        return { ...context, step: 'shipping' };
      }
      // ... more conditions
    },
  },
});

// CORRECT - Use XState machine for complex flows
import { createMachine } from 'xstate';

const checkoutMachine = createMachine({
  id: 'checkout',
  initial: 'cart',
  states: {
    cart: {
      on: { NEXT: { target: 'shipping', guard: 'hasItems' } },
    },
    shipping: {
      on: {
        NEXT: { target: 'payment', guard: 'hasShippingAddress' },
        BACK: 'cart',
      },
    },
    payment: {
      on: {
        NEXT: { target: 'confirmation', guard: 'hasPaymentMethod' },
        BACK: 'shipping',
      },
    },
    confirmation: {
      type: 'final',
    },
  },
});
```

### 5. Creating New Stores in Components

```typescript
// WRONG - Creates new store on every render
function Counter() {
  const store = createStore({
    context: { count: 0 },
    on: { increment: (ctx) => ({ ...ctx, count: ctx.count + 1 }) },
  });
  // ...
}

// CORRECT - Use useStore hook for local stores
function Counter() {
  const store = useStore({
    context: { count: 0 },
    on: { increment: (ctx) => ({ ...ctx, count: ctx.count + 1 }) },
  });
  // ...
}

// OR define store outside component for global state
const counterStore = createStore({
  context: { count: 0 },
  on: { increment: (ctx) => ({ ...ctx, count: ctx.count + 1 }) },
});

function Counter() {
  const count = useSelector(counterStore, (s) => s.context.count);
  // ...
}
```

---

## Validation Checklist

Before completing any task involving @xstate/store:

- [ ] Always spread `...context` in transition return values
- [ ] Use `trigger` API for type-safe event sending
- [ ] Create selectors for optimized subscriptions
- [ ] Clean up subscriptions in React components
- [ ] Use `emits` for side effect coordination
- [ ] Use `useStore` hook for local component state
- [ ] Consider migrating to XState machines for complex flows
- [ ] Type checks pass (`pnpm run typecheck`)
- [ ] Tests pass (`pnpm run test`)
