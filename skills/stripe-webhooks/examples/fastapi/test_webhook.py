import os
import json
import hmac
import hashlib
import time
import pytest
from fastapi.testclient import TestClient

# Set test environment variables before importing app
os.environ["STRIPE_SECRET_KEY"] = "sk_test_fake_key"
os.environ["STRIPE_WEBHOOK_SECRET"] = "whsec_test_secret"

from main import app

client = TestClient(app)


def generate_stripe_signature(payload: str, secret: str) -> str:
    """Generate a valid Stripe signature for testing."""
    timestamp = str(int(time.time()))
    signed_payload = f"{timestamp}.{payload}"
    signature = hmac.new(
        secret.encode("utf-8"),
        signed_payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return f"t={timestamp},v1={signature}"


class TestStripeWebhook:
    """Tests for Stripe webhook endpoint."""
    
    webhook_secret = os.environ["STRIPE_WEBHOOK_SECRET"]

    def test_missing_signature_returns_400(self):
        """Should return 400 when signature header is missing."""
        response = client.post(
            "/webhooks/stripe",
            content="{}",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 400
        assert "Missing stripe-signature" in response.json()["detail"]

    def test_invalid_signature_returns_400(self):
        """Should return 400 when signature is invalid."""
        payload = json.dumps({
            "id": "evt_test",
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_test"}}
        })
        
        response = client.post(
            "/webhooks/stripe",
            content=payload,
            headers={
                "Content-Type": "application/json",
                "Stripe-Signature": "t=123,v1=invalid_signature"
            }
        )
        assert response.status_code == 400
        assert "Invalid signature" in response.json()["detail"]

    def test_valid_signature_returns_200(self):
        """Should return 200 when signature is valid."""
        payload = json.dumps({
            "id": "evt_test_valid",
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_test_valid"}}
        })
        signature = generate_stripe_signature(payload, self.webhook_secret)
        
        response = client.post(
            "/webhooks/stripe",
            content=payload,
            headers={
                "Content-Type": "application/json",
                "Stripe-Signature": signature
            }
        )
        assert response.status_code == 200
        assert response.json() == {"received": True}

    def test_handles_different_event_types(self):
        """Should handle various Stripe event types."""
        event_types = [
            "payment_intent.succeeded",
            "payment_intent.payment_failed",
            "customer.subscription.created",
            "customer.subscription.deleted",
            "invoice.paid",
            "unknown.event.type"
        ]
        
        for event_type in event_types:
            payload = json.dumps({
                "id": f"evt_{event_type.replace('.', '_')}",
                "type": event_type,
                "data": {"object": {"id": "obj_123"}}
            })
            signature = generate_stripe_signature(payload, self.webhook_secret)
            
            response = client.post(
                "/webhooks/stripe",
                content=payload,
                headers={
                    "Content-Type": "application/json",
                    "Stripe-Signature": signature
                }
            )
            assert response.status_code == 200, f"Failed for event type: {event_type}"


class TestHealth:
    """Tests for health endpoint."""
    
    def test_health_returns_ok(self):
        """Should return health status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
