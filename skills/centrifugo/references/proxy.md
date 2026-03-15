# Centrifugo Event Proxy Reference

## Overview

Centrifugo proxies client events to the application backend via HTTP or GRPC. This allows the backend to authenticate connections, authorize subscriptions, validate publications, and handle RPC calls.

## Proxy Protocols

- **HTTP**: Use `http://` or `https://` endpoint. Sends JSON POST requests.
- **GRPC**: Use `grpc://` endpoint. Uses Protobuf-defined service.

Both share the same schema: `github.com/centrifugal/centrifugo/internal/proxyproto/proxy.proto`

## Client-Wide Proxy Events

### Connect Proxy

Authenticate connections without JWT.

```json
{
  "client": {
    "proxy": {
      "connect": {
        "enabled": true,
        "endpoint": "http://backend:3000/centrifugo/connect",
        "timeout": "3s",
        "http_headers": ["Cookie", "Authorization"]
      }
    }
  }
}
```

**Backend receives**:

```json
{
  "client": "client-id",
  "transport": "websocket",
  "protocol": "json",
  "encoding": "json",
  "data": {}, // Custom data from client
  "b64data": "", // Binary data (base64)
  "name": "js", // SDK name
  "version": "5.x.x", // SDK version
  "channels": [] // Channels client wants to subscribe to
}
```

**Backend responds**:

```json
{
  "result": {
    "user": "42",
    "expire_at": 1700000000,
    "info": { "name": "Alice" },
    "b64info": "",
    "data": {},
    "channels": ["notifications:user#42"],
    "subs": {
      "chat:room-1": {
        "data": {},
        "info": {}
      }
    },
    "meta": {}
  }
}
```

To reject: return `{"error": {"code": 1000, "message": "unauthorized"}}` or use `{"disconnect": {"code": 4501, "reason": "unauthorized"}}`.

### Refresh Proxy

Extend sessions or perform periodic liveness checks.

```json
{
  "client": {
    "proxy": {
      "refresh": {
        "enabled": true,
        "endpoint": "http://backend:3000/centrifugo/refresh"
      }
    }
  }
}
```

**Backend receives**: `{ client, transport, protocol, encoding, user, meta }`

**Backend responds**:

```json
{
  "result": {
    "expire_at": 1700003600,
    "info": {},
    "expired": false
  }
}
```

## Channel Proxy Events

Configured per-namespace:

```json
{
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
          },
          "sub_refresh": {
            "enabled": true,
            "endpoint": "http://backend:3000/centrifugo/sub_refresh"
          }
        }
      }
    ]
  }
}
```

### Subscribe Proxy

Validate channel access.

**Backend receives**:

```json
{
  "client": "client-id",
  "transport": "websocket",
  "protocol": "json",
  "encoding": "json",
  "user": "42",
  "channel": "chat:room-1",
  "token": "",
  "meta": {},
  "data": {}
}
```

**Backend responds** (allow):

```json
{
  "result": {
    "info": { "role": "admin" },
    "data": { "last_read": 100 },
    "override": {
      "presence": { "value": true },
      "join_leave": { "value": true }
    }
  }
}
```

**Backend responds** (deny):

```json
{
  "error": {
    "code": 403,
    "message": "not allowed"
  }
}
```

### Publish Proxy

Validate and optionally transform client publications.

**Backend receives**:

```json
{
  "client": "client-id",
  "transport": "websocket",
  "user": "42",
  "channel": "chat:room-1",
  "data": { "text": "hello" },
  "meta": {}
}
```

**Backend responds** (allow, optionally modify):

```json
{
  "result": {
    "data": { "text": "hello", "author": "Alice", "timestamp": 1700000000 },
    "skip_history": false
  }
}
```

**Backend responds** (reject):

```json
{
  "error": {
    "code": 400,
    "message": "message too long"
  }
}
```

### Sub Refresh Proxy

Extend subscription expiration.

**Backend receives**: `{ client, transport, user, channel, meta }`

**Backend responds**: `{ result: { expire_at, expired, info } }`

## RPC Proxy

Handle custom client-to-server calls.

```json
{
  "client": {
    "proxy": {
      "rpc": {
        "enabled": true,
        "endpoint": "http://backend:3000/centrifugo/rpc"
      }
    }
  }
}
```

**Backend receives**:

```json
{
  "client": "client-id",
  "transport": "websocket",
  "user": "42",
  "method": "get_user_profile",
  "data": { "user_id": "123" },
  "meta": {}
}
```

**Backend responds**:

```json
{
  "result": {
    "data": { "name": "Bob", "avatar": "url" }
  }
}
```

## Proxy Configuration Options

Each proxy event supports:

| Option                    | Type     | Description                              |
| ------------------------- | -------- | ---------------------------------------- |
| `enabled`                 | bool     | Enable this proxy                        |
| `endpoint`                | string   | Backend URL (http://, https://, grpc://) |
| `timeout`                 | duration | Request timeout (default: "1s")          |
| `http_headers`            | string[] | HTTP headers to forward from client      |
| `grpc_metadata`           | string[] | GRPC metadata keys to forward            |
| `binary_encoding`         | bool     | Use base64 for data fields               |
| `include_connection_meta` | bool     | Include connection meta in request       |
| `grpc_cert_file`          | string   | TLS cert for GRPC                        |
| `grpc_credentials_key`    | string   | GRPC auth key                            |

## HTTP Headers Forwarding

By default, Centrifugo forwards no headers. Configure which client headers to proxy:

```json
{
  "client": {
    "proxy": {
      "connect": {
        "enabled": true,
        "endpoint": "http://backend/connect",
        "http_headers": ["Cookie", "Authorization", "X-Forwarded-For"]
      }
    }
  }
}
```
