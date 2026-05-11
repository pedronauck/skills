const request = require("supertest");
const crypto = require("crypto");

// Set test environment variables before importing app
process.env.STRIPE_SECRET_KEY = "sk_test_fake_key";
process.env.STRIPE_WEBHOOK_SECRET = "whsec_test_secret";

const app = require("../src/index");

/**
 * Generate a valid Stripe signature for testing
 */
function generateStripeSignature(payload, secret) {
  const timestamp = Math.floor(Date.now() / 1000);
  const signedPayload = `${timestamp}.${payload}`;
  const signature = crypto.createHmac("sha256", secret).update(signedPayload).digest("hex");
  return `t=${timestamp},v1=${signature}`;
}

describe("Stripe Webhook Endpoint", () => {
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  describe("POST /webhooks/stripe", () => {
    it("should return 400 for missing signature", async () => {
      const response = await request(app)
        .post("/webhooks/stripe")
        .set("Content-Type", "application/json")
        .send("{}");

      expect(response.status).toBe(400);
    });

    it("should return 400 for invalid signature", async () => {
      const payload = JSON.stringify({
        id: "evt_test_123",
        type: "payment_intent.succeeded",
        data: { object: { id: "pi_test_123" } },
      });

      const response = await request(app)
        .post("/webhooks/stripe")
        .set("Content-Type", "application/json")
        .set("Stripe-Signature", "t=123,v1=invalid_signature")
        .send(payload);

      expect(response.status).toBe(400);
      expect(response.text).toContain("Webhook Error");
    });

    it("should return 400 for tampered payload", async () => {
      const originalPayload = JSON.stringify({
        id: "evt_test_123",
        type: "payment_intent.succeeded",
        data: { object: { id: "pi_test_123" } },
      });

      // Sign with original payload but send different payload
      const signature = generateStripeSignature(originalPayload, webhookSecret);
      const tamperedPayload = JSON.stringify({
        id: "evt_test_123",
        type: "payment_intent.succeeded",
        data: { object: { id: "pi_tampered" } },
      });

      const response = await request(app)
        .post("/webhooks/stripe")
        .set("Content-Type", "application/json")
        .set("Stripe-Signature", signature)
        .send(tamperedPayload);

      expect(response.status).toBe(400);
    });

    it("should return 200 for valid signature", async () => {
      const payload = JSON.stringify({
        id: "evt_test_valid",
        type: "payment_intent.succeeded",
        data: { object: { id: "pi_test_valid" } },
      });
      const signature = generateStripeSignature(payload, webhookSecret);

      const response = await request(app)
        .post("/webhooks/stripe")
        .set("Content-Type", "application/json")
        .set("Stripe-Signature", signature)
        .send(payload);

      expect(response.status).toBe(200);
      expect(response.body).toEqual({ received: true });
    });

    it("should handle different event types", async () => {
      const eventTypes = [
        "payment_intent.succeeded",
        "payment_intent.payment_failed",
        "customer.subscription.created",
        "customer.subscription.deleted",
        "invoice.paid",
        "unknown.event.type",
      ];

      for (const eventType of eventTypes) {
        const payload = JSON.stringify({
          id: `evt_${eventType.replace(/\./g, "_")}`,
          type: eventType,
          data: { object: { id: "obj_123" } },
        });
        const signature = generateStripeSignature(payload, webhookSecret);

        const response = await request(app)
          .post("/webhooks/stripe")
          .set("Content-Type", "application/json")
          .set("Stripe-Signature", signature)
          .send(payload);

        expect(response.status).toBe(200);
      }
    });
  });

  describe("GET /health", () => {
    it("should return health status", async () => {
      const response = await request(app).get("/health");

      expect(response.status).toBe(200);
      expect(response.body).toEqual({ status: "ok" });
    });
  });
});
