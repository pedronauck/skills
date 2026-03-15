# Centrifugo Client SDK Reference

## Official SDKs

| SDK               | Platform                       | Package                                        |
| ----------------- | ------------------------------ | ---------------------------------------------- |
| centrifuge-js     | Browser, Node.js, React Native | `npm install centrifuge`                       |
| centrifuge-go     | Go                             | `go get github.com/centrifugal/centrifuge-go`  |
| centrifuge-dart   | Dart, Flutter                  | `dart pub add centrifuge`                      |
| centrifuge-swift  | iOS (Swift)                    | SPM: `github.com/centrifugal/centrifuge-swift` |
| centrifuge-java   | Android (Java/Kotlin)          | Maven Central                                  |
| centrifuge-python | Python (asyncio)               | `pip install centrifuge-python`                |

## Client Connection

### JavaScript

```javascript
import { Centrifuge } from "centrifuge";

const client = new Centrifuge("ws://localhost:8000/connection/websocket", {
  token: "<JWT>",
  // OR dynamic token:
  // getToken: async () => { const r = await fetch("/token"); return (await r.json()).token; }
});

client.on("connecting", ctx => {
  console.log(`connecting: ${ctx.code}, ${ctx.reason}`);
});
client.on("connected", ctx => {
  console.log(`connected over ${ctx.transport}`);
});
client.on("disconnected", ctx => {
  console.log(`disconnected: ${ctx.code}, ${ctx.reason}`);
});
client.on("error", ctx => {
  console.log("client error", ctx);
});

client.connect();
```

### Connection States

```
disconnected ──> connecting ──> connected
     ^               │              │
     │               │              │
     └───────────────┴──────────────┘
```

- `disconnected` → `connecting`: After `connect()` call
- `connecting` → `connected`: Successful connection
- `connected` → `connecting`: Temporary connection loss (auto-reconnect)
- `connected` → `disconnected`: Terminal error or `disconnect()` call
- `connecting` → `disconnected`: Terminal error

Auto-reconnect uses exponential backoff with full jitter.

## Channel Subscriptions

### Subscribe to a Channel

```javascript
const sub = client.newSubscription("chat:room-1");

sub.on("publication", ctx => {
  console.log("data:", ctx.data);
  console.log("offset:", ctx.offset);
  console.log("tags:", ctx.tags);
});

sub.on("subscribing", ctx => {
  console.log(`subscribing: ${ctx.code}, ${ctx.reason}`);
});
sub.on("subscribed", ctx => {
  console.log("subscribed:", ctx);
  // ctx.wasRecovering, ctx.recovered, ctx.publications
});
sub.on("unsubscribed", ctx => {
  console.log(`unsubscribed: ${ctx.code}, ${ctx.reason}`);
});

// Join/leave events (if enabled in namespace)
sub.on("join", ctx => console.log("join:", ctx.info));
sub.on("leave", ctx => console.log("leave:", ctx.info));

sub.subscribe();
```

### Subscription States

```
unsubscribed ──> subscribing ──> subscribed
     ^                │              │
     │                │              │
     └────────────────┴──────────────┘
```

### Subscription with Token

```javascript
const sub = client.newSubscription("$private:channel", {
  getToken: async () => {
    const resp = await fetch(`/api/sub-token?channel=$private:channel`);
    const data = await resp.json();
    return data.token;
  },
});
sub.subscribe();
```

### Subscription with Recovery

Recovery is automatic when `force_recovery` is enabled in the namespace. After reconnection:

```javascript
sub.on("subscribed", ctx => {
  if (ctx.wasRecovering) {
    if (ctx.recovered) {
      // All missed messages were recovered from history
      // They arrive as "publication" events before "subscribed"
    } else {
      // Recovery failed — load state from main database
      loadStateFromDatabase();
    }
  }
});
```

### Tags Filter (Publication Filtering)

```javascript
const sub = client.newSubscription("live:feed", {
  tagsFilter: { sport: "football" },
});
// Only receives publications with matching tags
sub.subscribe();
```

## Presence

Query online users in a channel (must be enabled in namespace):

```javascript
const sub = client.newSubscription("chat:room-1");
sub.subscribe();

// After subscribed:
const presenceResult = await sub.presence();
// presenceResult.clients: map of clientId -> {client, user, connInfo, chanInfo}

const statsResult = await sub.presenceStats();
// statsResult.numClients, statsResult.numUsers
```

## History

Query channel history (must be enabled in namespace):

```javascript
const historyResult = await sub.history({ limit: 10 });
// historyResult.publications: Publication[]
// historyResult.offset, historyResult.epoch
```

## RPC (Remote Procedure Calls)

Send custom requests through the real-time connection:

```javascript
const result = await client.rpc("method_name", { key: "value" });
console.log("RPC result:", result.data);
```

Requires RPC proxy configured on the server:

```json
{
  "client": {
    "proxy": {
      "rpc": {
        "enabled": true,
        "endpoint": "http://backend/centrifugo/rpc"
      }
    }
  }
}
```

## Client-Side Publish

Publish from client (requires `allow_publish_for_client` or publish proxy):

```javascript
await sub.publish({ text: "hello from client" });
```

## Server-Side Subscriptions

Handled automatically by the client. Listen on the client:

```javascript
client.on("subscribed", ctx => {
  // Server-side subscription established
  console.log("server sub:", ctx.channel);
});

client.on("publication", ctx => {
  // Publication from server-side subscription
  console.log("server pub:", ctx.channel, ctx.data);
});
```

## Protobuf Mode (centrifuge-js)

For binary protocol (faster, more compact):

```javascript
import { Centrifuge } from "centrifuge";
import { encode, decode } from "@bufbuild/protobuf";

const client = new Centrifuge("ws://localhost:8000/connection/websocket", {
  protocol: "protobuf",
  token: "<JWT>",
});
```

Dart, Swift, Java, and Python SDKs use Protobuf by default.

## Disconnect and Cleanup

```javascript
// Unsubscribe from a channel
sub.unsubscribe();

// Remove subscription entirely
client.removeSubscription(sub);

// Disconnect from server
client.disconnect();
```
