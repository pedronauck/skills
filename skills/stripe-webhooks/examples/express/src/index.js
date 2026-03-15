require("dotenv").config();
const express = require("express");
const stripe = require("stripe")(process.env.STRIPE_SECRET_KEY);

const app = express();

// Stripe webhook endpoint - must use raw body for signature verification
app.post("/webhooks/stripe", express.raw({ type: "application/json" }), async (req, res) => {
  const sig = req.headers["stripe-signature"];

  let event;
  try {
    // Verify the webhook signature using Stripe SDK
    event = stripe.webhooks.constructEvent(req.body, sig, process.env.STRIPE_WEBHOOK_SECRET);
  } catch (err) {
    console.error("Webhook signature verification failed:", err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  // Handle the event based on type
  switch (event.type) {
    case "payment_intent.succeeded":
      const paymentIntent = event.data.object;
      console.log("Payment succeeded:", paymentIntent.id);
      // TODO: Fulfill the order, send confirmation email, etc.
      break;

    case "payment_intent.payment_failed":
      const failedPayment = event.data.object;
      console.log("Payment failed:", failedPayment.id);
      // TODO: Notify customer, update order status, etc.
      break;

    case "customer.subscription.created":
      const subscription = event.data.object;
      console.log("Subscription created:", subscription.id);
      // TODO: Provision access, send welcome email, etc.
      break;

    case "customer.subscription.deleted":
      const canceledSub = event.data.object;
      console.log("Subscription canceled:", canceledSub.id);
      // TODO: Revoke access, send retention email, etc.
      break;

    case "invoice.paid":
      const invoice = event.data.object;
      console.log("Invoice paid:", invoice.id);
      // TODO: Record payment, update billing history, etc.
      break;

    default:
      console.log(`Unhandled event type: ${event.type}`);
  }

  // Return 200 to acknowledge receipt
  res.json({ received: true });
});

// Health check endpoint
app.get("/health", (req, res) => {
  res.json({ status: "ok" });
});

// Export app for testing
module.exports = app;

// Start server only when run directly (not when imported for testing)
if (require.main === module) {
  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`Webhook endpoint: POST http://localhost:${PORT}/webhooks/stripe`);
  });
}
