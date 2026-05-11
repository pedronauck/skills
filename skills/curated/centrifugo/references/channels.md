# Centrifugo Channels Reference

## Channel Naming Rules

- **ASCII only** in channel names
- Max length: 255 characters (configurable via `channel_max_length`)
- Reserved symbols: `:` (namespace), `#` (user boundary), `$` (private prefix), `/`, `*`, `&`

## Special Channel Prefixes

### Namespace boundary (`:`)

- `chat:room-1` belongs to namespace `chat`
- Options from `chat` namespace are applied
- The namespace is part of the channel name — publish to `chat:room-1`, not `room-1`

### User-limited channels (`#`)

- `feed#42` — only user ID `42` can subscribe
- `dialog#42,43` — only users 42 and 43 can subscribe
- Requires `allow_user_limited_channels: true` in namespace

### Private channel prefix (`$`)

- `$secret` — requires subscription token even with `allow_subscribe_for_client`
- Configurable via `channel_private_prefix`

## Namespace Configuration

```json
{
  "channel": {
    "without_namespace": {
      // Options for channels without namespace prefix
    },
    "namespaces": [
      {
        "name": "chat"
        // Options for channels starting with "chat:"
      }
    ]
  }
}
```

**No inheritance** between namespaces. Each must be configured independently.

## Channel Options

### Subscription Permissions

| Option                          | Type | Default | Description                               |
| ------------------------------- | ---- | ------- | ----------------------------------------- |
| `allow_subscribe_for_client`    | bool | false   | Allow authenticated clients to subscribe  |
| `allow_subscribe_for_anonymous` | bool | false   | Allow anonymous clients to subscribe      |
| `allow_user_limited_channels`   | bool | false   | Enable `#` user boundary channels         |
| `allow_publish_for_client`      | bool | false   | Allow clients to publish to channel       |
| `allow_publish_for_anonymous`   | bool | false   | Allow anonymous clients to publish        |
| `allow_publish_for_subscriber`  | bool | false   | Allow only subscribers to publish         |
| `allow_presence_for_client`     | bool | false   | Allow clients to query presence           |
| `allow_presence_for_subscriber` | bool | false   | Allow only subscribers to query presence  |
| `allow_presence_for_anonymous`  | bool | false   | Allow anonymous clients to query presence |
| `allow_history_for_client`      | bool | false   | Allow clients to query history            |
| `allow_history_for_subscriber`  | bool | false   | Allow only subscribers to query history   |
| `allow_history_for_anonymous`   | bool | false   | Allow anonymous clients to query history  |

### Presence

| Option                  | Type | Default | Description                                    |
| ----------------------- | ---- | ------- | ---------------------------------------------- |
| `presence`              | bool | false   | Enable online presence tracking                |
| `join_leave`            | bool | false   | Send join/leave events to subscribers          |
| `force_push_join_leave` | bool | false   | Push join/leave even without subscription flag |

### History & Recovery

| Option              | Type     | Default | Description                      |
| ------------------- | -------- | ------- | -------------------------------- |
| `history_size`      | int      | 0       | Max publications in history      |
| `history_ttl`       | duration | "0s"    | Time-to-live for history entries |
| `history_meta_ttl`  | duration | auto    | TTL for history metadata         |
| `force_positioning` | bool     | false   | Detect publication gaps          |
| `force_recovery`    | bool     | false   | Auto-recover missed messages     |

**Cache recovery mode** — keep only latest publication:

```json
{
  "name": "state",
  "history_size": 1,
  "history_ttl": "0s",
  "force_recovery": true,
  "allow_subscribe_for_client": true
}
```

Use `"history_ttl": "0s"` with `"history_size": 1` for infinite cache retention.

### Delta Compression

| Option          | Type | Default | Description                               |
| --------------- | ---- | ------- | ----------------------------------------- |
| `delta_publish` | bool | false   | Enable delta compression for publications |

Reduces bandwidth by sending only differences between consecutive messages.

### Publication Filtering

| Option                        | Type | Default | Description                             |
| ----------------------------- | ---- | ------- | --------------------------------------- |
| `allow_subscribe_tags_filter` | bool | false   | Let clients filter publications by tags |

Clients can subscribe with tags filter to receive only relevant publications.

### Proxy

Per-namespace proxy configuration:

```json
{
  "name": "chat",
  "proxy": {
    "subscribe": {
      "enabled": true,
      "endpoint": "http://backend/centrifugo/subscribe"
    },
    "publish": {
      "enabled": true,
      "endpoint": "http://backend/centrifugo/publish"
    }
  }
}
```

## Example: Full Namespace Setup

```json
{
  "channel": {
    "without_namespace": {
      "allow_subscribe_for_client": true
    },
    "namespaces": [
      {
        "name": "chat",
        "presence": true,
        "join_leave": true,
        "history_size": 100,
        "history_ttl": "600s",
        "force_recovery": true,
        "force_positioning": true,
        "allow_subscribe_for_client": true,
        "allow_presence_for_subscriber": true,
        "allow_history_for_subscriber": true
      },
      {
        "name": "notifications",
        "allow_user_limited_channels": true,
        "allow_subscribe_for_client": true,
        "history_size": 50,
        "history_ttl": "86400s",
        "force_recovery": true
      },
      {
        "name": "live",
        "allow_subscribe_for_client": true,
        "allow_subscribe_for_anonymous": true
      }
    ]
  }
}
```
