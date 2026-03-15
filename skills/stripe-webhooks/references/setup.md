# Setting Up Stripe Webhooks

## Prerequisites

- Stripe account (test mode works for development)
- Your application's webhook endpoint URL (must be HTTPS in production)

## Get Your Signing Secret

The webhook signing secret is used to verify that webhook requests actually come from Stripe.

### Via Stripe Dashboard

1. Go to [Stripe Dashboard → Developers → Webhooks](https://dashboard.stripe.com/webhooks)
2. Click **+ Add endpoint**
3. Enter your endpoint URL (e.g., `https://your-app.com/webhooks/stripe`)
4. Select the events you want to receive
5. Click **Add endpoint**
6. Click on your new endpoint to view details
7. Under **Signing secret**, click **Reveal** to see your `whsec_...` secret

### Via Stripe CLI (Local Development)

For local development, use the Stripe CLI:

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login to your Stripe account
stripe login

# Forward webhooks to your local server
stripe listen --forward-to localhost:3000/webhooks/stripe
```

The CLI will display a webhook signing secret (`whsec_...`) to use for local testing.

## Register Your Endpoint

### Recommended Events for Common Use Cases

**Payments:**

- `payment_intent.succeeded`
- `payment_intent.payment_failed`

**Subscriptions:**

- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.paid`
- `invoice.payment_failed`

**Checkout:**

- `checkout.session.completed`
- `checkout.session.expired`

**Disputes:**

- `charge.dispute.created`
- `charge.dispute.closed`

## Test Mode vs Live Mode

Stripe maintains separate webhook endpoints and signing secrets for test and live modes:

- **Test mode**: Use test API keys, test webhook secret, simulated events
- **Live mode**: Use live API keys, live webhook secret, real transactions

You can trigger test events from the Dashboard:

1. Go to your webhook endpoint in the Dashboard
2. Click **Send test webhook**
3. Select an event type and click **Send test webhook**

Or use the Stripe CLI:

```bash
stripe trigger payment_intent.succeeded
```

## Environment Variables

Store your signing secret securely:

```bash
# .env
STRIPE_WEBHOOK_SECRET=whsec_your_signing_secret_here
STRIPE_SECRET_KEY=sk_test_your_api_key_here
```

Never commit secrets to version control. Use environment variables or a secrets manager.

## Full Documentation

For complete setup instructions, see [Stripe Webhooks Documentation](https://docs.stripe.com/webhooks).
