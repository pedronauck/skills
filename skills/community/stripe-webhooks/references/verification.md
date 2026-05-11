# Stripe Signature Verification

## How It Works

Stripe signs every webhook request using HMAC SHA-256. The signature is included in the `Stripe-Signature` header and contains:

1. A timestamp (`t`) - When Stripe sent the request
2. A signature (`v1`) - HMAC SHA-256 of `timestamp.payload` using your webhook secret

Example header:

```
Stripe-Signature: t=1614556800,v1=abc123...,v0=def456...
```

The `v1` signature is the current version. Ignore `v0` (legacy).

## Implementation

### Using the Stripe SDK (Recommended)

The official Stripe SDK handles signature verification automatically:

**Node.js:**

```javascript
const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);

// IMPORTANT: Use raw body, not parsed JSON
const event = stripe.webhooks.constructEvent(
  rawBody, // Raw request body as Buffer or string
  request.headers["stripe-signature"], // Stripe-Signature header
  process.env.STRIPE_WEBHOOK_SECRET // Your webhook signing secret
);
```

**Python:**

```python
import stripe

event = stripe.Webhook.construct_event(
    payload=raw_body,                    # Raw request body as bytes
    sig_header=request.headers['Stripe-Signature'],
    secret=os.environ['STRIPE_WEBHOOK_SECRET']
)
```

### Manual Verification

If you need to verify manually (not recommended):

```javascript
const crypto = require("crypto");

function verifyStripeSignature(payload, header, secret) {
  const parts = header.split(",");
  const timestamp = parts.find(p => p.startsWith("t=")).slice(2);
  const signature = parts.find(p => p.startsWith("v1=")).slice(3);

  const signedPayload = `${timestamp}.${payload}`;
  const expectedSignature = crypto.createHmac("sha256", secret).update(signedPayload).digest("hex");

  // Use timing-safe comparison
  return crypto.timingSafeEqual(Buffer.from(signature), Buffer.from(expectedSignature));
}
```

## Common Gotchas

### 1. Raw Body Requirement

The most common cause of verification failures is using a parsed JSON body instead of the raw request body.

**Express:**

```javascript
// WRONG - body is already parsed
app.use(express.json());
app.post('/webhooks/stripe', (req, res) => {
  stripe.webhooks.constructEvent(req.body, ...); // Fails!
});

// CORRECT - use raw body for this route
app.post('/webhooks/stripe',
  express.raw({ type: 'application/json' }),
  (req, res) => {
    stripe.webhooks.constructEvent(req.body, ...); // Works!
  }
);
```

### 2. Middleware Ordering

If you use a global JSON parser, configure the webhook route BEFORE the parser:

```javascript
// Webhook route with raw body (FIRST)
app.post("/webhooks/stripe", express.raw({ type: "application/json" }), handleWebhook);

// Global JSON parser (AFTER)
app.use(express.json());
```

### 3. Timestamp Tolerance

Stripe rejects requests older than 300 seconds (5 minutes) by default. This prevents replay attacks but can cause issues if:

- Your server clock is significantly off
- You're replaying old events for testing

The SDK accepts a `tolerance` parameter to adjust this:

```javascript
stripe.webhooks.constructEvent(body, sig, secret, 600); // 10 minute tolerance
```

### 4. Multiple Signing Secrets

When rotating secrets, Stripe may include signatures from both old and new secrets. The SDK handles this automatically by trying each `v1` signature.

## Debugging Verification Failures

### Error: "No signatures found matching the expected signature"

1. **Check the raw body**: Log `typeof req.body` - it should be `Buffer` or `string`, not `object`
2. **Check the secret**: Ensure you're using the correct `whsec_...` secret for this endpoint
3. **Check test vs live**: Test mode endpoints need test mode secrets

### Error: "Timestamp outside tolerance"

1. **Check server time**: Run `date` and compare to actual time
2. **Increase tolerance**: For testing only, increase the tolerance parameter

### Logging for Debugging

```javascript
app.post('/webhooks/stripe', express.raw({ type: 'application/json' }), (req, res) => {
  console.log('Body type:', typeof req.body);
  console.log('Body length:', req.body.length);
  console.log('Signature header:', req.headers['stripe-signature']);

  try {
    const event = stripe.webhooks.constructEvent(...);
  } catch (err) {
    console.error('Verification failed:', err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }
});
```

## Full Documentation

For complete signature verification details, see [Stripe's signature verification documentation](https://docs.stripe.com/webhooks/signatures).
