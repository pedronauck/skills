# Stripe Webhooks - FastAPI Example

Minimal example of receiving Stripe webhooks with signature verification using FastAPI.

## Prerequisites

- Python 3.9+
- Stripe account with webhook signing secret

## Setup

1. Create virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy environment variables:

   ```bash
   cp .env.example .env
   ```

4. Add your Stripe webhook signing secret to `.env`

## Run

```bash
uvicorn main:app --reload --port 3000
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

## Endpoint

- `POST /webhooks/stripe` - Receives and verifies Stripe webhook events
