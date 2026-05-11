# Stripe Webhooks Overview

## What Are Stripe Webhooks?

Stripe uses webhooks to notify your application when events occur in your account. Instead of polling the API for changes, Stripe sends HTTP POST requests to your configured endpoint URL whenever something happens—like a successful payment, a subscription renewal, or a dispute being created.

Webhooks are essential for building reliable payment integrations because many events (like asynchronous payment confirmations) can only be received via webhooks.

## Common Event Types

| Event                           | Triggered When                        | Common Use Cases                         |
| ------------------------------- | ------------------------------------- | ---------------------------------------- |
| `payment_intent.succeeded`      | Payment completes successfully        | Fulfill orders, send confirmation emails |
| `payment_intent.payment_failed` | Payment attempt fails                 | Notify customer, retry logic             |
| `customer.subscription.created` | New subscription starts               | Provision access, welcome emails         |
| `customer.subscription.updated` | Subscription changes (plan, quantity) | Update entitlements                      |
| `customer.subscription.deleted` | Subscription canceled or expired      | Revoke access, retention emails          |
| `invoice.paid`                  | Invoice payment succeeds              | Record payment, update billing history   |
| `invoice.payment_failed`        | Invoice payment fails                 | Dunning emails, grace periods            |
| `checkout.session.completed`    | Checkout Session completes            | Fulfill one-time purchases               |
| `charge.dispute.created`        | Customer disputes a charge            | Gather evidence, notify team             |

## Event Payload Structure

All Stripe webhook events share a common structure:

```json
{
  "id": "evt_1234567890",
  "object": "event",
  "api_version": "2023-10-16",
  "created": 1234567890,
  "type": "payment_intent.succeeded",
  "data": {
    "object": {
      // The full API object (PaymentIntent, Subscription, etc.)
    },
    "previous_attributes": {
      // For update events: fields that changed
    }
  },
  "livemode": false,
  "pending_webhooks": 1,
  "request": {
    "id": "req_abc123",
    "idempotency_key": "key_xyz"
  }
}
```

Key fields:

- `type` - The event type (e.g., `payment_intent.succeeded`)
- `data.object` - The full Stripe API object that triggered the event
- `livemode` - `true` for production, `false` for test mode
- `id` - Unique event ID (use for idempotency)

## Full Event Reference

For the complete list of events, see [Stripe's webhook events documentation](https://docs.stripe.com/api/events/types).

For detailed payload schemas per event type, see [Stripe API Reference](https://docs.stripe.com/api).
