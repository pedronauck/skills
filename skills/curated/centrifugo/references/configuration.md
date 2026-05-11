# Centrifugo Configuration Reference

## Configuration Sources (Priority Order)

1. **Command-line flags** (highest)
2. **Environment variables** (medium — override config file)
3. **Configuration file** (lowest — JSON, YAML, or TOML)

## Starting Centrifugo

```bash
# Generate config
centrifugo genconfig              # Creates config.json

# Start with config
centrifugo -c config.json
centrifugo --config=config.yaml
centrifugo --config=config.toml

# Docker
docker run -p 8000:8000 centrifugo/centrifugo:v6 centrifugo
docker run -p 8000:8000 -v $(pwd)/config.json:/centrifugo/config.json centrifugo/centrifugo:v6 centrifugo -c config.json
```

## Minimal Configuration

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
  }
}
```

## Environment Variables

All config options map to env vars. Use `CENTRIFUGO_` prefix with `_` separator for nesting:

| Config Path                    | Environment Variable                                  |
| ------------------------------ | ----------------------------------------------------- |
| `client.token.hmac_secret_key` | `CENTRIFUGO_CLIENT_TOKEN_HMAC_SECRET_KEY`             |
| `http_api.key`                 | `CENTRIFUGO_HTTP_API_KEY`                             |
| `client.allowed_origins`       | `CENTRIFUGO_CLIENT_ALLOWED_ORIGINS` (comma-separated) |
| `engine.type`                  | `CENTRIFUGO_ENGINE_TYPE`                              |
| `engine.redis.address`         | `CENTRIFUGO_ENGINE_REDIS_ADDRESS`                     |

Use `centrifugo defaultenv` to see all available env vars.

## Core Configuration Sections

### `client` — Client Connection Settings

```json
{
  "client": {
    "allowed_origins": ["http://localhost:3000"],
    "token": {
      "hmac_secret_key": "<SECRET>",
      "rsa_public_key": "",
      "ecdsa_public_key": "",
      "audience": "",
      "issuer": ""
    },
    "insecure": false,
    "proxy": { ... }
  }
}
```

**`allowed_origins`**: Required for browser connections. Validates the Origin header. Use `["*"]` only in development.

**`insecure`**: Skip client authentication (development only).

### `http_api` — Server API Settings

```json
{
  "http_api": {
    "key": "<API_KEY>",
    "insecure": false
  }
}
```

### `channel` — Channel & Namespace Settings

See `references/channels.md` for full details.

### `engine` — Engine Configuration

See `references/engines.md` for Memory, Redis, and NATS setup.

### `admin` — Admin Web UI

```json
{
  "admin": {
    "enabled": true,
    "password": "<ADMIN_PASSWORD>",
    "secret": "<ADMIN_SECRET>",
    "insecure": false
  }
}
```

Access at `http://localhost:8000/` when enabled.

### `tls` — TLS/HTTPS

```json
{
  "tls": {
    "enabled": true,
    "cert_file": "/path/to/cert.pem",
    "key_file": "/path/to/key.pem"
  }
}
```

With TLS, use `wss://` for WebSocket and `https://` for API.

### `prometheus` — Metrics

```json
{
  "prometheus": {
    "enabled": true
  }
}
```

Metrics exposed at `/metrics` endpoint.

### `health` — Health Check

```json
{
  "health": {
    "enabled": true
  }
}
```

Health endpoint at `/health`.

### `log_level` — Logging

```json
{
  "log_level": "info"
}
```

Values: `trace`, `debug`, `info`, `warn`, `error`, `fatal`, `panic`.

## Transport Endpoints

Default endpoints (all on port 8000):

| Endpoint                      | Transport      | Description                  |
| ----------------------------- | -------------- | ---------------------------- |
| `/connection/websocket`       | WebSocket      | Bidirectional real-time      |
| `/connection/http_stream`     | HTTP Streaming | Bidirectional emulation      |
| `/connection/sse`             | SSE            | Bidirectional emulation      |
| `/connection/webtransport`    | WebTransport   | Bidirectional (experimental) |
| `/connection/uni_websocket`   | WebSocket      | Unidirectional               |
| `/connection/uni_http_stream` | HTTP Streaming | Unidirectional               |
| `/connection/uni_sse`         | SSE            | Unidirectional               |
| `/api`                        | HTTP           | Server API                   |
| `/api/grpc`                   | GRPC           | Server GRPC API              |
| `/metrics`                    | HTTP           | Prometheus metrics           |
| `/health`                     | HTTP           | Health check                 |
| `/`                           | HTTP           | Admin web UI                 |

## Server Port

```json
{
  "port": 8000
}
```

Or via env: `CENTRIFUGO_PORT=8000`.

## Helper CLI Commands

```bash
centrifugo genconfig            # Generate config file
centrifugo gentoken -u <user>   # Generate test JWT
centrifugo defaultconfig        # Show all config options with defaults
centrifugo defaultenv           # Show all env var mappings
centrifugo configdoc            # Show config documentation
centrifugo checkconfig          # Validate config file
centrifugo serve --port 3000    # Serve static files (development)
```
