# Centrifugo Authentication Reference

## Connection JWT Authentication

Centrifugo authenticates clients via JWT (JSON Web Token) signed by the application backend. Supported algorithms: HS256, HS384, HS512, RSA256, RSA384, RSA512, EC256, EC384, EC512.

### Configuration

```json
{
  "client": {
    "token": {
      "hmac_secret_key": "<SECRET>", // For HMAC algorithms
      "rsa_public_key": "-----BEGIN...", // For RSA algorithms
      "ecdsa_public_key": "-----BEGIN...", // For ECDSA algorithms
      "audience": "centrifugo", // Optional: validate aud claim
      "issuer": "my_app" // Optional: validate iss claim
    }
  }
}
```

### JWT Claims

**Standard claims**:

| Claim | Type   | Required | Description                                         |
| ----- | ------ | -------- | --------------------------------------------------- |
| `sub` | string | yes      | User ID (empty string for anonymous)                |
| `exp` | int    | no       | Expiration Unix timestamp (seconds)                 |
| `iat` | int    | no       | Issued-at timestamp                                 |
| `jti` | string | no       | Unique token identifier                             |
| `aud` | string | no       | Audience (validated if `client.token.audience` set) |
| `iss` | string | no       | Issuer (validated if `client.token.issuer` set)     |

**Centrifugo-specific claims**:

| Claim       | Type     | Description                                               |
| ----------- | -------- | --------------------------------------------------------- |
| `info`      | JSON     | Connection info (included in presence, join/leave events) |
| `b64info`   | string   | Binary connection info (base64)                           |
| `channels`  | string[] | Server-side subscriptions list                            |
| `subs`      | map      | Server-side subscriptions with options                    |
| `meta`      | JSON     | Connection metadata (not shared with other clients)       |
| `expire_at` | int      | Override `exp` for connection expiration                  |

### Token Generation Examples

**Python**:

```python
import jwt, time
token = jwt.encode(
    {"sub": "42", "exp": int(time.time()) + 3600, "info": {"name": "Alice"}},
    "secret", algorithm="HS256"
)
```

**Node.js**:

```javascript
const jwt = require("jsonwebtoken");
const token = jwt.sign({ sub: "42", info: { name: "Alice" } }, "secret", { expiresIn: "1h" });
```

**Go**:

```go
token := jwt.NewWithClaims(jwt.SigningMethodHS256, jwt.MapClaims{
    "sub": "42",
    "exp": time.Now().Add(time.Hour).Unix(),
})
tokenString, _ := token.SignedString([]byte("secret"))
```

### Token Refresh

When `exp` is set, SDKs support automatic token refresh:

```javascript
const client = new Centrifuge("ws://localhost:8000/connection/websocket", {
  getToken: async () => {
    const resp = await fetch("/api/centrifugo/token");
    const data = await resp.json();
    return data.token;
  },
});
```

The `getToken` callback is called when the token is about to expire or when initial connection needs a token.

## Channel Subscription Tokens

For per-channel authorization, issue a separate subscription JWT:

```json
{
  "client": {
    "channel_token": {
      "hmac_secret_key": "<CHANNEL_SECRET>"
    }
  }
}
```

**Subscription JWT claims**:

| Claim      | Type   | Required | Description              |
| ---------- | ------ | -------- | ------------------------ |
| `sub`      | string | yes      | User ID                  |
| `channel`  | string | yes      | Channel name             |
| `exp`      | int    | no       | Expiration timestamp     |
| `info`     | JSON   | no       | Channel-specific info    |
| `b64info`  | string | no       | Binary channel info      |
| `override` | object | no       | Override channel options |

Client-side usage:

```javascript
const sub = client.newSubscription("private:channel", {
  getToken: async () => {
    const resp = await fetch(`/api/centrifugo/sub-token?channel=private:channel`);
    const data = await resp.json();
    return data.token;
  },
});
```

## Connect Proxy Authentication

Alternative to JWT — proxy the connect event to the backend:

```json
{
  "client": {
    "proxy": {
      "connect": {
        "enabled": true,
        "endpoint": "http://backend:3000/centrifugo/connect"
      }
    }
  }
}
```

The backend receives the connection request with original HTTP headers (cookies, authorization) and responds:

```json
{
  "result": {
    "user": "42",
    "expire_at": 1700000000,
    "info": { "name": "Alice" },
    "channels": ["notifications:user#42"]
  }
}
```

**Advantages of connect proxy**: No JWT management, leverages existing session/cookie auth, can subscribe to channels during connection.

## Anonymous Access

Allow connections without authentication:

```json
{
  "client": {
    "insecure": true
  }
}
```

Or use JWT with empty `sub` claim: `{"sub": ""}`. Then enable anonymous-friendly channel options:

```json
{
  "channel": {
    "namespaces": [
      {
        "name": "public",
        "allow_subscribe_for_anonymous": true,
        "allow_subscribe_for_client": true
      }
    ]
  }
}
```
