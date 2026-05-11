---
name: centrifugo
description: "Centrifugo real-time messaging server expert for WebSocket PUB/SUB, channel management, JWT authentication, event proxying, and horizontal scaling with Redis/NATS. Use when: centrifugo, centrifugal, real-time messaging, websocket pubsub, channel subscriptions, real-time notifications, live updates, presence, history recovery, server-sent events integration, real-time transport layer. Do not use for: general WebSocket programming without Centrifugo, Socket.IO, Pusher SDK, or other real-time frameworks."
---

# Centrifugo Real-Time Messaging Integration

Centrifugo is a self-hosted, language-agnostic real-time messaging server. It handles persistent connections (WebSocket, SSE, HTTP-streaming, WebTransport, GRPC) and broadcasts messages via a channel-based PUB/SUB model. The application backend publishes to channels via Server API; Centrifugo delivers to online subscribers instantly.

## Core Architecture

```
Backend App ──(HTTP/GRPC Server API)──> Centrifugo Cluster ──(WebSocket/SSE)──> Clients
                                              │
                                        Redis/NATS Broker
                                        (for multi-node)
```

**Key principle**: All user-generated data flows through the application backend first (validate, persist, then publish to Centrifugo). Centrifugo is the transport layer, not the source of truth.

## Procedures

### Step 1: Determine Integration Pattern

Identify the real-time feature being built and select the appropriate pattern:

1. **Unidirectional publish** (most common): Backend publishes to channels after processing user requests. Clients subscribe and receive updates passively.
2. **Bidirectional with proxy**: Clients send data over the real-time connection; Centrifugo proxies events (connect, subscribe, publish, RPC) to the backend for validation.
3. **Server-side subscriptions**: Backend controls which channels a user subscribes to (useful for personalized feeds, notifications).

### Step 2: Configure Centrifugo Server

Generate a minimal configuration:

```bash
centrifugo genconfig  # Creates config.json
```

Or use Docker:

```bash
docker run -p 8000:8000 centrifugo/centrifugo:v6 centrifugo
```

Essential configuration structure (JSON, YAML, or TOML supported):

```json
{
  "client": {
    "token": {
      "hmac_secret_key": "<SECRET>"
    },
    "allowed_origins": ["http://localhost:3000"]
  },
  "http_api": {
    "key": "<API_KEY>"
  },
  "channel": {
    "without_namespace": {
      "allow_subscribe_for_client": true
    }
  }
}
```

Read `references/configuration.md` for the full configuration reference including TLS, admin UI, environment variables, and advanced options.

### Step 3: Set Up Authentication

Centrifugo authenticates clients via JWT or connect proxy.

**JWT approach** (recommended for most cases):

- Backend generates a JWT with `sub` (user ID) and `exp` claims, signed with the configured HMAC/RSA/ECDSA key.
- Client passes the token when connecting.
- Supports token refresh for long-lived connections.

```python
# Backend: generate connection JWT (Python example)
import jwt, time
token = jwt.encode(
    {"sub": "user123", "exp": int(time.time()) + 3600},
    "<HMAC_SECRET>", algorithm="HS256"
)
```

```javascript
// Client: connect with token
const client = new Centrifuge("ws://localhost:8000/connection/websocket", {
  token: "<JWT_TOKEN>",
});
client.connect();
```

**Connect proxy approach** (alternative):

- Centrifugo forwards connection requests to the backend endpoint for authentication.
- No JWT needed; backend responds with user identity.

Read `references/authentication.md` for JWT claims, token refresh, proxy auth, and channel-level authorization tokens.

### Step 4: Design Channel Structure

Channels are ephemeral strings that serve as message pathways. Use namespaces to apply different behaviors.

**Naming conventions**:

- `chat:room-123` — namespace `chat`, channel for room 123
- `notifications:user#42` — user-limited channel (only user 42 can subscribe)
- `$private:secret` — private channel prefix (requires subscription token)

**Namespace configuration**:

```json
{
  "channel": {
    "namespaces": [
      {
        "name": "chat",
        "presence": true,
        "history_size": 50,
        "history_ttl": "300s",
        "force_recovery": true,
        "join_leave": true
      },
      {
        "name": "notifications",
        "allow_user_limited_channels": true
      }
    ]
  }
}
```

Read `references/channels.md` for all channel options, namespace rules, and special channel prefixes.

### Step 5: Publish from Backend (Server API)

Use HTTP or GRPC to publish messages from the application backend.

**HTTP API** — POST to `/api/<method>` with `X-API-Key` header:

```bash
# Publish to a channel
curl -X POST -H "X-API-Key: <KEY>" -H "Content-Type: application/json" \
  -d '{"channel": "chat:room-1", "data": {"text": "hello"}}' \
  http://localhost:8000/api/publish

# Broadcast to multiple channels
curl -X POST -H "X-API-Key: <KEY>" -H "Content-Type: application/json" \
  -d '{"channels": ["user:1", "user:2"], "data": {"text": "hello"}}' \
  http://localhost:8000/api/broadcast
```

**Available API methods**: `publish`, `broadcast`, `subscribe`, `unsubscribe`, `disconnect`, `refresh`, `presence`, `presence_stats`, `history`, `history_remove`, `channels`, `info`, `batch`.

Read `references/server-api.md` for all method signatures, request/response schemas, and HTTP API library links.

### Step 6: Connect Clients with SDK

Official SDKs: `centrifuge-js` (browser/Node/React Native), `centrifuge-go`, `centrifuge-dart` (Flutter), `centrifuge-swift` (iOS), `centrifuge-java` (Android), `centrifuge-python`.

**JavaScript client pattern**:

```javascript
import { Centrifuge } from "centrifuge";

const client = new Centrifuge("ws://localhost:8000/connection/websocket", {
  token: "<JWT>",
});

// Connection state handlers
client.on("connecting", ctx => console.log("connecting", ctx));
client.on("connected", ctx => console.log("connected", ctx));
client.on("disconnected", ctx => console.log("disconnected", ctx));

// Subscribe to channel
const sub = client.newSubscription("chat:room-1");
sub.on("publication", ctx => {
  console.log("received:", ctx.data);
});
sub.on("subscribing", ctx => console.log("subscribing", ctx));
sub.on("subscribed", ctx => console.log("subscribed", ctx));
sub.subscribe();

client.connect();
```

**Client states**: `disconnected` -> `connecting` -> `connected` (auto-reconnect with exponential backoff).

**Subscription states**: `unsubscribed` -> `subscribing` -> `subscribed` (auto-resubscribe on reconnect).

Read `references/client-sdk.md` for all SDK patterns, token refresh, presence/history from client, RPC calls, and Protobuf mode.

### Step 7: Configure Event Proxy (Optional)

Proxy client events to the backend for validation and custom logic.

**Supported proxy events**:

- `connect` — authenticate connections without JWT
- `refresh` — extend client sessions
- `subscribe` — validate channel access
- `publish` — validate publications from clients
- `rpc` — handle custom client-to-server calls
- `sub_refresh` — extend subscription sessions

```json
{
  "client": {
    "proxy": {
      "connect": {
        "enabled": true,
        "endpoint": "http://backend:3000/centrifugo/connect"
      },
      "rpc": {
        "enabled": true,
        "endpoint": "http://backend:3000/centrifugo/rpc"
      }
    }
  },
  "channel": {
    "namespaces": [
      {
        "name": "chat",
        "proxy": {
          "subscribe": {
            "enabled": true,
            "endpoint": "http://backend:3000/centrifugo/subscribe"
          },
          "publish": {
            "enabled": true,
            "endpoint": "http://backend:3000/centrifugo/publish"
          }
        }
      }
    ]
  }
}
```

Read `references/proxy.md` for proxy request/response schemas, GRPC proxy, header forwarding, and timeout configuration.

### Step 8: Scale Horizontally (Production)

**Memory engine** (default): Single node only. Fast, no dependencies. Suitable for development and small deployments.

**Redis engine**: Multi-node clusters. Messages published on any node reach all subscribers.

```json
{
  "engine": {
    "type": "redis",
    "redis": {
      "address": "redis://localhost:6379"
    }
  }
}
```

Supports Redis Sentinel, Redis Cluster, consistent sharding across multiple Redis instances, and Redis-compatible storages (Valkey, DragonflyDB, KeyDB, AWS ElastiCache).

**NATS broker**: Alternative for PUB/SUB only (no history/presence persistence).

Read `references/engines.md` for Redis Sentinel/Cluster setup, sharding, NATS configuration, and separate broker/presence manager configuration.

### Step 9: Enable History and Recovery

History allows caching recent publications per channel. Recovery automatically restores missed messages after reconnection.

```json
{
  "channel": {
    "namespaces": [
      {
        "name": "chat",
        "history_size": 100,
        "history_ttl": "600s",
        "force_recovery": true,
        "force_positioning": true
      }
    ]
  }
}
```

- `history_size` + `history_ttl`: Define retention window.
- `force_recovery`: Clients automatically recover missed messages on reconnect.
- `force_positioning`: Detect publication gaps.
- **Cache recovery mode**: Optimized for channels where only the latest state matters. Read `references/channels.md` for details.

### Step 10: Add Observability

Centrifugo exposes Prometheus metrics at `/metrics` and supports structured logging.

```json
{
  "log_level": "info",
  "prometheus": {
    "enabled": true
  },
  "health": {
    "enabled": true
  }
}
```

Metrics include: connections, subscriptions, publications, API calls, transport stats, and engine stats.

## Anti-Patterns

### Do NOT use Centrifugo history as a primary database

History is an ephemeral hot cache designed to reduce database load during reconnect storms. Always maintain a primary application database.

### Do NOT rely solely on Centrifugo for data delivery

Design with graceful degradation. If Centrifugo goes down, the application should still function (just without real-time updates). Return data in API responses, not only via channels.

### Do NOT skip `allowed_origins` in production

Empty `allowed_origins` blocks all browser connections. Configure it with the exact origins of the frontend application.

### Do NOT publish directly from clients without proxy validation

Always validate client publications through either:

- The application backend (clients call backend API, backend publishes to Centrifugo), or
- Publish proxy (Centrifugo forwards client publish to backend for validation)

### Do NOT use channels without namespaces in production

Namespaces provide granular control over channel behavior and permissions. Define a namespace for each real-time feature.

### Do NOT ignore token expiration

Set reasonable `exp` claims in JWTs. Too short = excessive refresh requests. Too long = delayed user deactivation. Implement the token refresh callback in client SDKs.

## Error Handling

- If the client receives `102: unknown channel` — verify the namespace is defined in configuration.
- If the client receives `103: permission denied` — check channel permissions (`allow_subscribe_for_client`, subscription JWT, or subscribe proxy).
- If publications are not delivered — verify the channel name matches exactly (namespace prefix included). Ensure at least one subscriber exists.
- If reconnection loops occur — check `allowed_origins`, JWT validity/expiration, and network connectivity.
- If Redis engine fails to connect — verify address format (`redis://`, `rediss://` for TLS, `redis+sentinel://` for Sentinel, `redis+cluster://` for Cluster).

## Related Integrations

Centrifugo integrates well with any backend language/framework. Common setups include:

- **Node.js/Hono/Express**: Use HTTP API or `centrifuge` npm package for server-side operations.
- **Go**: Use the `centrifuge` Go library directly or the Centrifugo HTTP/GRPC API.
- **Python/Django/Flask**: Use `pycent` library or direct HTTP API calls.
- **PHP/Laravel**: Use `phpcent` library.

For the JavaScript client SDK (`centrifuge-js`), install via npm:

```bash
npm install centrifuge
# or
bun add centrifuge
```
