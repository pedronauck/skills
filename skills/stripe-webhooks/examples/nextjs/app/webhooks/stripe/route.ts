import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";

const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);

export async function POST(request: NextRequest) {
  // Get the raw body for signature verification
  const body = await request.text();
  const sig = request.headers.get("stripe-signature");

  if (!sig) {
    return NextResponse.json({ error: "Missing stripe-signature header" }, { status: 400 });
  }

  let event: Stripe.Event;
  try {
    // Verify the webhook signature using Stripe SDK
    event = stripe.webhooks.constructEvent(body, sig, process.env.STRIPE_WEBHOOK_SECRET!);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    console.error("Webhook signature verification failed:", message);
    return NextResponse.json({ error: `Webhook Error: ${message}` }, { status: 400 });
  }

  // Handle the event based on type
  const eventObject = event.data?.object;
  switch (event.type) {
    case "payment_intent.succeeded":
      console.log("Payment succeeded:", eventObject?.id);
      // TODO: Fulfill the order, send confirmation email, etc.
      break;

    case "payment_intent.payment_failed":
      console.log("Payment failed:", eventObject?.id);
      // TODO: Notify customer, update order status, etc.
      break;

    case "customer.subscription.created":
      console.log("Subscription created:", eventObject?.id);
      // TODO: Provision access, send welcome email, etc.
      break;

    case "customer.subscription.deleted":
      console.log("Subscription canceled:", eventObject?.id);
      // TODO: Revoke access, send retention email, etc.
      break;

    case "invoice.paid":
      console.log("Invoice paid:", eventObject?.id);
      // TODO: Record payment, update billing history, etc.
      break;

    default:
      console.log(`Unhandled event type: ${event.type}`);
  }

  // Return 200 to acknowledge receipt
  return NextResponse.json({ received: true });
}
