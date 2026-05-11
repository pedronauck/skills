# Centrifugo Engines & Scalability Reference

## Engine Overview

The Engine handles:

- PUB/SUB between Centrifugo nodes
- Publication history storage
- Online presence management

Engine = Broker (PUB/SUB + history) + Presence Manager.

## Memory Engine (Default)

Single node only. All data in process memory. Lost on restart.

```json
{
  "engine": {
    "type": "memory"
  }
}
```

**Use for**: Development, small deployments, isolated connection scenarios.

## Redis Engine

Multi-node scaling. Data persists across Centrifugo restarts.

### Standalone Redis

```json
{
  "engine": {
    "type": "redis",
    "redis": {
      "address": "redis://user:password@127.0.0.1:6379/0"
    }
  }
}
```

TLS: Use `rediss://` scheme.

### Redis Sentinel

```json
{
  "engine": {
    "type": "redis",
    "redis": {
      "address": "redis+sentinel://user:password@host1:26379,host2:26379,host3:26379/mymaster/0"
    }
  }
}
```

Format: `redis+sentinel://[user:pass@]host1:port,host2:port/master-name/db`

### Redis Cluster

```json
{
  "engine": {
    "type": "redis",
    "redis": {
      "address": "redis+cluster://user:password@host1:7000,host2:7001,host3:7002"
    }
  }
}
```

### Redis Sharding (Client-Side)

Distribute load across multiple Redis instances:

```json
{
  "engine": {
    "type": "redis",
    "redis": {
      "address": ["redis://redis1:6379", "redis://redis2:6379", "redis://redis3:6379"]
    }
  }
}
```

Uses consistent hashing. Can shard across Redis Clusters too.

### Redis Options

| Option            | Type            | Default          | Description          |
| ----------------- | --------------- | ---------------- | -------------------- |
| `address`         | string/string[] | "127.0.0.1:6379" | Redis address(es)    |
| `prefix`          | string          | "centrifugo"     | Key prefix in Redis  |
| `force_resp2`     | bool            | false            | Force RESP2 protocol |
| `connect_timeout` | duration        | "1s"             | Connection timeout   |
| `io_timeout`      | duration        | "4s"             | Read/write timeout   |
| `tls`             | object          | null             | TLS configuration    |

### Redis TLS

```json
{
  "engine": {
    "type": "redis",
    "redis": {
      "address": "rediss://localhost:6380",
      "tls": {
        "enabled": true,
        "cert_file": "/path/to/cert.pem",
        "key_file": "/path/to/key.pem",
        "root_ca_file": "/path/to/ca.pem",
        "insecure_skip_verify": false,
        "server_name": "redis.example.com"
      }
    }
  }
}
```

### Redis-Compatible Storages

Tested and supported:

- **AWS ElastiCache** (Redis mode)
- **Google Memorystore**
- **Valkey**
- **DragonflyDB** (set `force_resp2: true`)
- **KeyDB**

## NATS Broker

NATS for PUB/SUB only (no history or presence). Combine with Redis for full features.

```json
{
  "broker": {
    "type": "nats",
    "nats": {
      "url": "nats://localhost:4222"
    }
  },
  "presence_manager": {
    "type": "redis",
    "redis": {
      "address": "redis://localhost:6379"
    }
  }
}
```

### NATS Options

| Option          | Type     | Default                 | Description        |
| --------------- | -------- | ----------------------- | ------------------ |
| `url`           | string   | "nats://localhost:4222" | NATS server URL    |
| `prefix`        | string   | "centrifugo"            | Subject prefix     |
| `dial_timeout`  | duration | "1s"                    | Connection timeout |
| `write_timeout` | duration | "1s"                    | Write timeout      |

## Separate Broker and Presence Manager

For fine-grained control, configure broker and presence manager independently:

```json
{
  "broker": {
    "type": "redis",
    "redis": {
      "address": "redis://broker-redis:6379"
    }
  },
  "presence_manager": {
    "type": "redis",
    "redis": {
      "address": "redis://presence-redis:6379"
    }
  }
}
```

## Scaling Architecture

```
                    Load Balancer
                   /     |      \
            Node 1    Node 2    Node 3
                   \     |      /
                    Redis Cluster
                   /            \
              Shard 1        Shard 2
```

- Each Centrifugo node handles a subset of client connections.
- Any node can accept publish API calls — Redis broadcasts to all nodes.
- Add nodes to scale connections; add Redis shards to scale throughput.
- All data is ephemeral with TTLs — resharding is mostly automatic.

## Minimum Redis Version

**Redis 6.2.0 or later** is required.
