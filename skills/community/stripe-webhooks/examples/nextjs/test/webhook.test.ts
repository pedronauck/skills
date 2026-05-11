import { describe, it, expect, beforeAll } from "vitest";
import crypto from "crypto";

// Set test environment variables
beforeAll(() => {
  process.env.STRIPE_SECRET_KEY = "sk_test_fake_key";
  process.env.STRIPE_WEBHOOK_SECRET = "whsec_test_secret";
});

/**
 * Generate a valid Stripe signature for testing
 */
function generateStripeSignature(payload: string, secret: string): string {
  const timestamp = Math.floor(Date.now() / 1000);
  const signedPayload = `${timestamp}.${payload}`;
  const signature = crypto.createHmac("sha256", secret).update(signedPayload).digest("hex");
  return `t=${timestamp},v1=${signature}`;
}

/**
 * Parse Stripe signature header
 */
function parseStripeSignature(header: string): { timestamp: string; signature: string } | null {
  const parts: Record<string, string> = {};
  for (const part of header.split(",")) {
    const [key, value] = part.split("=");
    if (key && value) {
      parts[key] = value;
    }
  }
  if (!parts.t || !parts.v1) return null;
  return { timestamp: parts.t, signature: parts.v1 };
}

/**
 * Verify Stripe signature (same logic as in route.ts)
 */
function verifyStripeSignature(
  payload: string,
  signatureHeader: string,
  secret: string,
  tolerance: number = 300
): boolean {
  const parsed = parseStripeSignature(signatureHeader);
  if (!parsed) return false;

  const { timestamp, signature } = parsed;

  // Check timestamp tolerance
  const now = Math.floor(Date.now() / 1000);
  if (Math.abs(now - parseInt(timestamp)) > tolerance) {
    return false;
  }

  // Compute expected signature
  const signedPayload = `${timestamp}.${payload}`;
  const expectedSignature = crypto.createHmac("sha256", secret).update(signedPayload).digest("hex");

  // Timing-safe comparison
  try {
    return crypto.timingSafeEqual(
      Buffer.from(signature, "hex"),
      Buffer.from(expectedSignature, "hex")
    );
  } catch {
    return false;
  }
}

describe("Stripe Signature Verification", () => {
  const webhookSecret = "whsec_test_secret";

  it("should validate correct signature", () => {
    const payload = JSON.stringify({
      id: "evt_test",
      type: "payment_intent.succeeded",
      data: { object: { id: "pi_test" } },
    });
    const signature = generateStripeSignature(payload, webhookSecret);

    expect(verifyStripeSignature(payload, signature, webhookSecret)).toBe(true);
  });

  it("should reject invalid signature", () => {
    const payload = JSON.stringify({ id: "evt_test", type: "payment_intent.succeeded" });

    expect(verifyStripeSignature(payload, "t=123,v1=invalid", webhookSecret)).toBe(false);
  });

  it("should reject missing signature parts", () => {
    const payload = JSON.stringify({ id: "evt_test" });

    expect(verifyStripeSignature(payload, "invalid_format", webhookSecret)).toBe(false);
  });

  it("should reject tampered payload", () => {
    const originalPayload = JSON.stringify({ id: "evt_test", amount: 100 });
    const signature = generateStripeSignature(originalPayload, webhookSecret);
    const tamperedPayload = JSON.stringify({ id: "evt_test", amount: 999 });

    expect(verifyStripeSignature(tamperedPayload, signature, webhookSecret)).toBe(false);
  });

  it("should reject old timestamps", () => {
    const payload = JSON.stringify({ id: "evt_test" });
    const oldTimestamp = Math.floor(Date.now() / 1000) - 400; // 400 seconds ago
    const signedPayload = `${oldTimestamp}.${payload}`;
    const signature = crypto
      .createHmac("sha256", webhookSecret)
      .update(signedPayload)
      .digest("hex");
    const header = `t=${oldTimestamp},v1=${signature}`;

    expect(verifyStripeSignature(payload, header, webhookSecret)).toBe(false);
  });
});

describe("Stripe Signature Generation", () => {
  it("should generate valid format", () => {
    const payload = '{"test":true}';
    const signature = generateStripeSignature(payload, "whsec_test");

    expect(signature).toMatch(/^t=\d+,v1=[a-f0-9]{64}$/);
  });

  it("should include current timestamp", () => {
    const payload = '{"test":true}';
    const before = Math.floor(Date.now() / 1000);
    const signature = generateStripeSignature(payload, "whsec_test");
    const after = Math.floor(Date.now() / 1000);

    const parsed = parseStripeSignature(signature);
    expect(parsed).not.toBeNull();

    const timestamp = parseInt(parsed!.timestamp);
    expect(timestamp).toBeGreaterThanOrEqual(before);
    expect(timestamp).toBeLessThanOrEqual(after);
  });
});
