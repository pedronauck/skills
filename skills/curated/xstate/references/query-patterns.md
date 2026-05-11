# XState v5 + TanStack Query Integration Patterns

This document provides comprehensive patterns and best practices for integrating XState v5 with TanStack Query in React applications.

## Core Principles

1. **XState for Orchestration**: Use XState machines for state management and workflow orchestration.
2. **TanStack Query for Data**: Use TanStack Query for data fetching, caching, and server state management.
3. **Actors as Bridges**: Wrap Query operations as XState actors using `fromCallback` and `fromPromise`.
4. **QueryClient in Context**: Pass QueryClient through machine input/context for access within actors.
5. **Cache Updates in Mutations**: Keep query cache updates in mutation callbacks, not in machine actions.

## Event Type Enums

Always use enums for event type definitions to ensure type safety and consistency:

```typescript
export enum DataEventType {
  // Remote events
  REMOTE_UPDATE = "REMOTE_UPDATE",
  REMOTE_ERROR = "REMOTE_ERROR",

  // User actions
  SAVE_START = "SAVE_START",
  SAVE_SUCCESS = "SAVE_SUCCESS",
  SAVE_ERROR = "SAVE_ERROR",

  // State transitions
  RESET = "RESET",
  CANCEL = "CANCEL",
}

// Event type definitions
export type DataEvent =
  | { type: DataEventType.REMOTE_UPDATE; data: SomeDataType }
  | { type: DataEventType.REMOTE_ERROR; error: Error }
  | { type: DataEventType.SAVE_START; payload: SavePayload }
  | { type: DataEventType.SAVE_SUCCESS }
  | { type: DataEventType.SAVE_ERROR; error: Error };
```

## Query Subscriptions with QueryObserver

Use `fromCallback` with `QueryObserver` for reactive subscriptions to query state:

```typescript
import { fromCallback } from "xstate";
import { QueryObserver, type QueryClient } from "@tanstack/react-query";

interface SubscriptionInput {
  queryClient: QueryClient;
  entityId: string;
}

const subscribeToEntityQuery = fromCallback<
  { type: string; data?: EntityData; error?: Error },
  SubscriptionInput
>(({ input, sendBack }) => {
  const { queryClient, entityId } = input;

  const observer = new QueryObserver(queryClient, {
    queryKey: ["entity", entityId],
    queryFn: async () => {
      const response = await fetch(`/api/entities/${entityId}`);
      if (!response.ok) throw new Error("Failed to fetch entity");
      return response.json();
    },
    staleTime: 5000,
    refetchOnWindowFocus: true,
  });

  const unsubscribe = observer.subscribe((result) => {
    if (result.error) {
      sendBack({ type: DataEventType.REMOTE_ERROR, error: result.error });
    } else if (result.data) {
      sendBack({ type: DataEventType.REMOTE_UPDATE, data: result.data });
    }
  });

  // Emit current result immediately if available
  const currentResult = observer.getCurrentResult();
  if (currentResult.data) {
    sendBack({ type: DataEventType.REMOTE_UPDATE, data: currentResult.data });
  }

  // Return cleanup function
  return () => {
    unsubscribe();
  };
});
```

## Mutations with fromPromise

Wrap `useMutation` hooks as `fromPromise` actors and provide them via `.provide()`:

```typescript
import { useMutation } from "@tanstack/react-query";
import { fromPromise } from "xstate";
import { useMemo } from "react";

function useEntityMachine(entityId: string) {
  const queryClient = useQueryClient();

  // Define mutation hook
  const saveMutation = useMutation({
    mutationFn: async (data: EntityData) => {
      const response = await fetch(`/api/entities/${entityId}`, {
        method: "PUT",
        body: JSON.stringify(data),
        headers: { "Content-Type": "application/json" },
      });
      if (!response.ok) throw new Error("Failed to save");
      return response.json();
    },
    onSuccess: (data) => {
      // Update cache here, NOT in machine actions
      queryClient.setQueryData(["entity", entityId], data);
    },
  });

  // Create machine with provided actors
  const machine = useMemo(
    () =>
      createEntityMachine().provide({
        actors: {
          saveEntity: fromPromise(async ({ input }) => {
            return await saveMutation.mutateAsync(input.data);
          }),
        },
      }),
    [saveMutation]
  );

  return useActor(machine, {
    input: {
      queryClient,
      entityId,
    },
  });
}
```

## Actions Outside Setup

Define actions outside `setup()` using type-bound helpers for better maintainability:

```typescript
import { setup, assign, type MachineContext } from "xstate";

// First, create the setup
const entityMachineSetup = setup({
  types: {
    context: {} as EntityContext,
    events: {} as EntityEvent,
    input: {} as EntityInput,
  },
  actors: {
    subscribeToQuery: subscribeToEntityQuery,
    saveEntity: fromPromise(async () => {
      /* placeholder */
    }),
  },
});

// Then define actions outside setup using the type-bound helpers
const updateEntityData = entityMachineSetup.assign({
  data: ({ event }) => {
    if (event.type !== DataEventType.REMOTE_UPDATE) return null;
    return event.data;
  },
  lastUpdated: () => Date.now(),
});

const setError = entityMachineSetup.assign({
  error: ({ event }) => {
    if (event.type !== DataEventType.REMOTE_ERROR) return null;
    return event.error;
  },
});

const clearError = entityMachineSetup.assign({
  error: () => null,
});

// Use actions in machine definition
const entityMachine = entityMachineSetup.createMachine({
  id: "entity",
  context: ({ input }) => ({
    entityId: input.entityId,
    data: null,
    error: null,
    lastUpdated: null,
  }),
  initial: "loading",
  states: {
    loading: {
      invoke: {
        src: "subscribeToQuery",
        input: ({ context }) => ({
          queryClient: context.queryClient,
          entityId: context.entityId,
        }),
      },
      on: {
        [DataEventType.REMOTE_UPDATE]: {
          target: "idle",
          actions: updateEntityData,
        },
        [DataEventType.REMOTE_ERROR]: {
          target: "error",
          actions: setError,
        },
      },
    },
    idle: {
      on: {
        [DataEventType.SAVE_START]: "saving",
        [DataEventType.REMOTE_UPDATE]: {
          actions: updateEntityData,
        },
      },
    },
    saving: {
      invoke: {
        src: "saveEntity",
        input: ({ event }) => ({ data: event.payload }),
        onDone: {
          target: "idle",
          actions: clearError,
        },
        onError: {
          target: "error",
          actions: setError,
        },
      },
    },
    error: {
      on: {
        RETRY: {
          target: "loading",
          actions: clearError,
        },
      },
    },
  },
});
```

## Using enqueueActions for Sequential Actions

When you need to execute multiple actions in sequence:

```typescript
import { enqueueActions } from "xstate";

const handleComplexUpdate = enqueueActions(({ enqueue, event }) => {
  // First clear any existing error
  enqueue.assign({ error: null });

  // Then update the data
  if (event.type === DataEventType.REMOTE_UPDATE) {
    enqueue.assign({ data: event.data });
    enqueue.assign({ lastUpdated: Date.now() });
  }

  // Optionally raise another event
  enqueue.raise({ type: "DATA_PROCESSED" });
});
```

## Complete Machine Example

Here's a complete example combining all patterns:

```typescript
import { setup, assign, fromCallback, fromPromise, enqueueActions } from "xstate";
import { useActor } from "@xstate/react";
import { QueryObserver, useQueryClient, useMutation } from "@tanstack/react-query";
import { useMemo } from "react";

// Event type enum
export enum ChatEventType {
  REMOTE_UPDATE = "REMOTE_UPDATE",
  REMOTE_ERROR = "REMOTE_ERROR",
  SEND_MESSAGE = "SEND_MESSAGE",
  MESSAGE_SENT = "MESSAGE_SENT",
  MESSAGE_ERROR = "MESSAGE_ERROR",
  RETRY = "RETRY",
}

// Types
interface ChatMessage {
  id: string;
  content: string;
  timestamp: number;
}

interface ChatContext {
  chatId: string;
  messages: ChatMessage[];
  error: Error | null;
  pendingMessage: string | null;
}

interface ChatInput {
  chatId: string;
  queryClient: QueryClient;
}

type ChatEvent =
  | { type: ChatEventType.REMOTE_UPDATE; messages: ChatMessage[] }
  | { type: ChatEventType.REMOTE_ERROR; error: Error }
  | { type: ChatEventType.SEND_MESSAGE; content: string }
  | { type: ChatEventType.MESSAGE_SENT }
  | { type: ChatEventType.MESSAGE_ERROR; error: Error }
  | { type: ChatEventType.RETRY };

// Query subscription actor
const subscribeToChatMessages = fromCallback<ChatEvent, ChatInput>(({ input, sendBack }) => {
  const { queryClient, chatId } = input;

  const observer = new QueryObserver(queryClient, {
    queryKey: ["chat", chatId, "messages"],
    queryFn: async () => {
      const response = await fetch(`/api/chats/${chatId}/messages`);
      if (!response.ok) throw new Error("Failed to fetch messages");
      return response.json();
    },
    refetchInterval: 5000,
  });

  const unsubscribe = observer.subscribe((result) => {
    if (result.error) {
      sendBack({ type: ChatEventType.REMOTE_ERROR, error: result.error });
    } else if (result.data) {
      sendBack({ type: ChatEventType.REMOTE_UPDATE, messages: result.data });
    }
  });

  const current = observer.getCurrentResult();
  if (current.data) {
    sendBack({ type: ChatEventType.REMOTE_UPDATE, messages: current.data });
  }

  return () => unsubscribe();
});

// Machine setup
const chatMachineSetup = setup({
  types: {
    context: {} as ChatContext,
    events: {} as ChatEvent,
    input: {} as ChatInput,
  },
  actors: {
    subscribeToChatMessages,
    sendMessage: fromPromise(async () => {
      /* placeholder - provided at runtime */
    }),
  },
});

// Actions defined outside setup
const updateMessages = chatMachineSetup.assign({
  messages: ({ event }) => {
    if (event.type !== ChatEventType.REMOTE_UPDATE) return [];
    return event.messages;
  },
});

const setPendingMessage = chatMachineSetup.assign({
  pendingMessage: ({ event }) => {
    if (event.type !== ChatEventType.SEND_MESSAGE) return null;
    return event.content;
  },
});

const clearPendingMessage = chatMachineSetup.assign({
  pendingMessage: () => null,
});

const setError = chatMachineSetup.assign({
  error: ({ event }) => {
    if (event.type === ChatEventType.REMOTE_ERROR || event.type === ChatEventType.MESSAGE_ERROR) {
      return event.error;
    }
    return null;
  },
});

const clearError = chatMachineSetup.assign({
  error: () => null,
});

// Machine definition
export const createChatMachine = () =>
  chatMachineSetup.createMachine({
    id: "chat",
    context: ({ input }) => ({
      chatId: input.chatId,
      messages: [],
      error: null,
      pendingMessage: null,
    }),
    initial: "connecting",
    states: {
      connecting: {
        invoke: {
          src: "subscribeToChatMessages",
          input: ({ context }) => ({
            queryClient: context.queryClient,
            chatId: context.chatId,
          }),
        },
        on: {
          [ChatEventType.REMOTE_UPDATE]: {
            target: "connected",
            actions: updateMessages,
          },
          [ChatEventType.REMOTE_ERROR]: {
            target: "error",
            actions: setError,
          },
        },
      },
      connected: {
        on: {
          [ChatEventType.REMOTE_UPDATE]: {
            actions: updateMessages,
          },
          [ChatEventType.SEND_MESSAGE]: {
            target: "sending",
            actions: setPendingMessage,
          },
        },
      },
      sending: {
        invoke: {
          src: "sendMessage",
          input: ({ context }) => ({
            chatId: context.chatId,
            content: context.pendingMessage,
          }),
          onDone: {
            target: "connected",
            actions: clearPendingMessage,
          },
          onError: {
            target: "error",
            actions: [setError, clearPendingMessage],
          },
        },
      },
      error: {
        on: {
          [ChatEventType.RETRY]: {
            target: "connecting",
            actions: clearError,
          },
        },
      },
    },
  });

// React hook
export function useChatMachine(chatId: string) {
  const queryClient = useQueryClient();

  const sendMutation = useMutation({
    mutationFn: async ({ chatId, content }: { chatId: string; content: string }) => {
      const response = await fetch(`/api/chats/${chatId}/messages`, {
        method: "POST",
        body: JSON.stringify({ content }),
        headers: { "Content-Type": "application/json" },
      });
      if (!response.ok) throw new Error("Failed to send message");
      return response.json();
    },
    onSuccess: (newMessage, { chatId }) => {
      // Update cache here, NOT in machine actions
      queryClient.setQueryData(["chat", chatId, "messages"], (old: ChatMessage[] = []) => [
        ...old,
        newMessage,
      ]);
    },
  });

  const machine = useMemo(
    () =>
      createChatMachine().provide({
        actors: {
          sendMessage: fromPromise(async ({ input }) => {
            return await sendMutation.mutateAsync(input);
          }),
        },
      }),
    [sendMutation]
  );

  return useActor(machine, {
    input: {
      chatId,
      queryClient,
    },
  });
}
```

## Common Pitfalls to Avoid

### Do NOT:

1. **Use string literals for event types** - Always use enums:

   ```typescript
   // BAD
   on: { "REMOTE_UPDATE": { ... } }

   // GOOD
   on: { [DataEventType.REMOTE_UPDATE]: { ... } }
   ```

2. **Define actions inside `setup()`** - Define them outside using type-bound helpers:

   ```typescript
   // BAD
   setup({
     actions: {
       updateData: assign({ ... })
     }
   })

   // GOOD
   const machineSetup = setup({ ... });
   const updateData = machineSetup.assign({ ... });
   ```

3. **Create QueryObserver instances outside callback actors** - They must be inside `fromCallback`:

   ```typescript
   // BAD
   const observer = new QueryObserver(queryClient, options);
   const actor = fromCallback(() => observer.subscribe(...));

   // GOOD
   const actor = fromCallback(({ input }) => {
     const observer = new QueryObserver(input.queryClient, options);
     // ...
   });
   ```

4. **Forget to unsubscribe in callback cleanup**:

   ```typescript
   // BAD
   fromCallback(({ sendBack }) => {
     observer.subscribe(callback);
     // No cleanup!
   });

   // GOOD
   fromCallback(({ sendBack }) => {
     const unsubscribe = observer.subscribe(callback);
     return () => unsubscribe();
   });
   ```

5. **Update query cache inside machine actions** - Keep cache updates in mutation callbacks:

   ```typescript
   // BAD
   const updateCache = machineSetup.assign({
     data: ({ context, event }) => {
       queryClient.setQueryData(...); // DON'T DO THIS
       return event.data;
     }
   });

   // GOOD
   const mutation = useMutation({
     mutationFn: ...,
     onSuccess: (data) => {
       queryClient.setQueryData(...); // Cache updates here
     }
   });
   ```

6. **Pass mutation hooks directly to actors** - Wrap in `fromPromise`:

   ```typescript
   // BAD
   provide({
     actors: {
       save: saveMutation, // Wrong!
     },
   });

   // GOOD
   provide({
     actors: {
       save: fromPromise(async ({ input }) => {
         return await saveMutation.mutateAsync(input);
       }),
     },
   });
   ```

7. **Access QueryClient from closure** - Pass through context:

   ```typescript
   // BAD
   const queryClient = useQueryClient();
   fromCallback(() => {
     new QueryObserver(queryClient, ...); // Stale closure!
   });

   // GOOD
   fromCallback(({ input }) => {
     new QueryObserver(input.queryClient, ...);
   });
   ```

8. **Forget to use `enqueueActions()` for grouping sequential actions**:

   ```typescript
   // When you need multiple sequential actions, use enqueueActions
   const complexAction = enqueueActions(({ enqueue }) => {
     enqueue.assign({ step1: true });
     enqueue.assign({ step2: true });
     enqueue.raise({ type: "STEP_COMPLETE" });
   });
   ```

9. **Forget to use `.provide()` for React integration** - Always provide actors that use hooks:
   ```typescript
   // Actors that wrap hooks must be provided at runtime
   const machine = useMemo(
     () =>
       baseMachine.provide({
         actors: {
           /* ... */
         },
       }),
     [dependencies]
   );
   ```

## Validation Checklist

Before completing any task involving XState + TanStack Query integration:

- [ ] Event types use enums with UPPER_SNAKE_CASE naming
- [ ] Actions are defined outside `setup()` using type-bound helpers
- [ ] QueryObserver subscriptions are wrapped in `fromCallback`
- [ ] Mutations are wrapped in `fromPromise` and provided via `.provide()`
- [ ] Query cache updates happen in mutation callbacks, not machine actions
- [ ] Cleanup functions are returned from callback actors
- [ ] QueryClient is passed through machine input/context
- [ ] Run type checks: `pnpm run typecheck`
- [ ] Run tests: `pnpm run test`
