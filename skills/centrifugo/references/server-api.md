# Centrifugo Server API Reference

## HTTP API

All methods use HTTP POST to `http://<host>:8000/api/<method>` with headers:

- `Content-Type: application/json`
- `X-API-Key: <http_api.key>`

Alternative: pass `?api_key=<KEY>` as query param (less secure).

## GRPC API

Same methods available via GRPC. Protobuf definitions at:
`github.com/centrifugal/centrifugo/internal/proxyproto/proxy.proto`

## Methods

### publish

Publish data to a channel.

```bash
curl -X POST -H "X-API-Key: <KEY>" -H "Content-Type: application/json" \
  -d '{"channel": "chat", "data": {"text": "hello"}}' \
  http://localhost:8000/api/publish
```

**PublishRequest**:

| Field             | Type              | Required | Description                              |
| ----------------- | ----------------- | -------- | ---------------------------------------- |
| `channel`         | string            | yes      | Channel name                             |
| `data`            | JSON              | yes      | Data to publish                          |
| `skip_history`    | bool              | no       | Skip adding to history                   |
| `tags`            | map[string]string | no       | Metadata attached to publication         |
| `b64data`         | string            | no       | Binary data base64-encoded               |
| `idempotency_key` | string            | no       | Dedup key (5min cache window)            |
| `delta`           | bool              | no       | Construct delta update for subscribers   |
| `version`         | int               | no       | Document version (channels with history) |
| `version_epoch`   | string            | no       | Reset version epoch                      |

**PublishResult**: `{ offset: int, epoch: string }`

### broadcast

Publish same data to multiple channels efficiently.

```bash
curl -X POST -H "X-API-Key: <KEY>" -H "Content-Type: application/json" \
  -d '{"channels": ["user:1", "user:2"], "data": {"text": "hi"}}' \
  http://localhost:8000/api/broadcast
```

**BroadcastRequest**: Same as publish but `channels: string[]` instead of `channel: string`.

**BroadcastResult**: `{ responses: PublishResponse[] }`

### subscribe

Subscribe user sessions to a channel (server-side subscriptions).

| Field           | Type           | Required | Description                |
| --------------- | -------------- | -------- | -------------------------- |
| `user`          | string         | yes      | User ID                    |
| `channel`       | string         | yes      | Channel name               |
| `info`          | JSON           | no       | Custom subscription data   |
| `client`        | string         | no       | Specific client ID         |
| `session`       | string         | no       | Specific session           |
| `data`          | JSON           | no       | Custom data sent to client |
| `recover_since` | StreamPosition | no       | Recovery position          |
| `override`      | Override       | no       | Override channel options   |

### unsubscribe

Unsubscribe user from a channel.

| Field     | Type   | Required | Description        |
| --------- | ------ | -------- | ------------------ |
| `user`    | string | yes      | User ID            |
| `channel` | string | yes      | Channel name       |
| `client`  | string | no       | Specific client ID |
| `session` | string | no       | Specific session   |

### disconnect

Disconnect user by ID.

| Field        | Type       | Required | Description                               |
| ------------ | ---------- | -------- | ----------------------------------------- |
| `user`       | string     | yes      | User ID                                   |
| `client`     | string     | no       | Specific client ID                        |
| `session`    | string     | no       | Specific session                          |
| `whitelist`  | string[]   | no       | Client IDs to keep                        |
| `disconnect` | Disconnect | no       | Custom disconnect object `{code, reason}` |

### refresh

Refresh user connection (extend expiration).

| Field       | Type   | Required | Description                   |
| ----------- | ------ | -------- | ----------------------------- |
| `user`      | string | yes      | User ID                       |
| `client`    | string | no       | Specific client ID            |
| `expired`   | bool   | no       | Force expire connection       |
| `expire_at` | int    | no       | New expiration Unix timestamp |

### presence

Get all clients subscribed to a channel (must enable `presence: true` in namespace).

```bash
curl -X POST -H "X-API-Key: <KEY>" -H "Content-Type: application/json" \
  -d '{"channel": "chat:room-1"}' \
  http://localhost:8000/api/presence
```

**Result**: `{ presence: map[clientId -> {client, user, conn_info?, chan_info?}] }`

### presence_stats

Lightweight presence: client and user counts only.

**Result**: `{ num_clients: int, num_users: int }`

### history

Get publication history from a channel stream.

| Field     | Type           | Required | Description                             |
| --------- | -------------- | -------- | --------------------------------------- |
| `channel` | string         | yes      | Channel name                            |
| `limit`   | int            | no       | Max publications to return              |
| `since`   | StreamPosition | no       | Return publications after this position |
| `reverse` | bool           | no       | Iterate in reverse order                |

**StreamPosition**: `{ offset: int, epoch: string }`

**Result**: `{ publications: Publication[], offset: int, epoch: string }`

### history_remove

Remove publications from channel history stream.

| Field     | Type   | Required | Description  |
| --------- | ------ | -------- | ------------ |
| `channel` | string | yes      | Channel name |

### channels

Get list of active channels (with at least one subscriber).

| Field     | Type   | Required | Description                     |
| --------- | ------ | -------- | ------------------------------- |
| `pattern` | string | no       | Glob pattern to filter channels |

**Result**: `{ channels: map[channelName -> {num_clients: int}] }`

### info

Get information about running Centrifugo nodes.

**Result**: `{ nodes: [{uid, name, version, num_clients, num_channels, num_subs, num_users, uptime, metrics}] }`

### batch

Execute multiple API commands in a single HTTP request.

```bash
curl -X POST -H "X-API-Key: <KEY>" -H "Content-Type: application/json" \
  -d '{"commands": [
    {"publish": {"channel": "ch1", "data": {"v": 1}}},
    {"publish": {"channel": "ch2", "data": {"v": 2}}}
  ]}' \
  http://localhost:8000/api/batch
```

## Response Format

All responses follow this structure:

```json
// Success
{ "result": { ... } }

// Error
{ "error": { "code": 102, "message": "namespace not found" } }
```

Common error codes:

- `100` — internal server error
- `101` — unauthorized
- `102` — unknown channel (namespace not found)
- `103` — permission denied
- `104` — method not found
- `105` — not available
- `107` — bad request
- `108` — not found

## HTTP API Libraries

Official server-side libraries:

- **Go**: `github.com/centrifugal/gocent`
- **Python**: `pip install pycent`
- **PHP**: `composer require centrifugal/phpcent`
- **Ruby**: `gem install cent`
- **Node.js**: Direct HTTP/fetch calls (no dedicated package needed)
