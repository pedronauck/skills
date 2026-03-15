import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
import stripe

load_dotenv()

app = FastAPI()

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")


@app.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    # Get the raw body for signature verification
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")

    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing stripe-signature header")

    try:
        # Verify the webhook signature using Stripe SDK
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=webhook_secret
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail=f"Invalid payload: {str(e)}")
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise HTTPException(status_code=400, detail=f"Invalid signature: {str(e)}")

    # Handle the event based on type
    event_type = event["type"]
    data_object = event["data"]["object"]

    if event_type == "payment_intent.succeeded":
        print(f"Payment succeeded: {data_object['id']}")
        # TODO: Fulfill the order, send confirmation email, etc.

    elif event_type == "payment_intent.payment_failed":
        print(f"Payment failed: {data_object['id']}")
        # TODO: Notify customer, update order status, etc.

    elif event_type == "customer.subscription.created":
        print(f"Subscription created: {data_object['id']}")
        # TODO: Provision access, send welcome email, etc.

    elif event_type == "customer.subscription.deleted":
        print(f"Subscription canceled: {data_object['id']}")
        # TODO: Revoke access, send retention email, etc.

    elif event_type == "invoice.paid":
        print(f"Invoice paid: {data_object['id']}")
        # TODO: Record payment, update billing history, etc.

    else:
        print(f"Unhandled event type: {event_type}")

    # Return 200 to acknowledge receipt
    return {"received": True}


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
