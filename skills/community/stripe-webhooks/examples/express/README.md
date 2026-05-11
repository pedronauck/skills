# Stripe Webhooks - Express Example

Minimal example of receiving Stripe webhooks with signature verification.

## Prerequisites

- Node.js 18+
- Stripe account with webhook signing secret

## Setup

1. Install dependencies:

   ```bash
   npm install
   ```

2. Copy environment variables:

   ```bash
   cp .env.example .env
   ```

3. Add your Stripe webhook signing secret to `.env`

## Run

```bash
npm start
```

Server runs on http://localhost:3000

## Test

### Using Stripe CLI

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login and forward events
stripe login
stripe listen --forward-to localhost:3000/webhooks/stripe

# In another terminal, trigger a test event
stripe trigger payment_intent.succeeded
```

### Using Hookdeck CLI

```bash
# Install Hookdeck CLI
brew install hookdeck/hookdeck/hookdeck

# Forward webhooks to localhost
hookdeck listen 3000 --path /webhooks/stripe
```

Then trigger events from the Stripe Dashboard or CLI.

## Endpoint

- `POST /webhooks/stripe` - Receives and verifies Stripe webhook events
