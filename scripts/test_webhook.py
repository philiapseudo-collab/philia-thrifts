#!/usr/bin/env python
"""
Phase 3 test script: Send test webhooks to local endpoint.

Usage:
    python scripts/test_webhook.py
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_webhook():
    """Send test webhook to /webhook/tiktok endpoint."""
    
    print("\n" + "="*60)
    print("🧪 Phase 3 Webhook Testing")
    print("="*60)
    
    # Test 1: Valid webhook
    print("\n1️⃣ Testing valid webhook...")
    payload = {
        "event": "message.received",
        "event_id": f"test_phase3_{int(time.time())}",
        "timestamp": int(time.time()),
        "data": {
            "message": {
                "from_user_id": "test_user_webhook",
                "content": "Hello from Phase 3 test script!"
            }
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/webhook/tiktok",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    if response.status_code == 200:
        print("   ✅ Webhook accepted")
    else:
        print("   ❌ Webhook rejected")
    
    # Test 2: Duplicate webhook (idempotency)
    print("\n2️⃣ Testing idempotency (send same event again)...")
    time.sleep(1)  # Small delay
    
    response2 = requests.post(
        f"{BASE_URL}/webhook/tiktok",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response2.status_code}")
    print(f"   Response: {response2.json()}")
    
    if "duplicate" in response2.json():
        print("   ✅ Idempotency working (duplicate detected)")
    else:
        print("   ⚠️  Duplicate not detected (check Redis)")
    
    # Test 3: Different payload structure
    print("\n3️⃣ Testing flexible payload parsing...")
    payload3 = {
        "event": "message.received",
        "event_id": f"test_flex_{int(time.time())}",
        "timestamp": int(time.time()),
        "data": {
            "sender_id": "test_user_flat",  # Flat structure
            "text": "Testing flat structure"
        }
    }
    
    response3 = requests.post(
        f"{BASE_URL}/webhook/tiktok",
        json=payload3,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"   Status: {response3.status_code}")
    print(f"   Response: {response3.json()}")
    
    if response3.status_code == 200:
        print("   ✅ Flexible parsing working")
    else:
        print("   ❌ Parsing failed")
    
    print("\n" + "="*60)
    print("✅ Testing complete!")
    print("\nNext steps:")
    print("1. Check worker logs: docker-compose logs worker")
    print("2. Check Redis: docker-compose exec redis redis-cli KEYS 'idempotency:*'")
    print("3. Check DB: SELECT * FROM idempotency_logs;")
    print("="*60 + "\n")


if __name__ == "__main__":
    try:
        test_webhook()
    except requests.exceptions.ConnectionError:
        print("\n❌ Connection failed!")
        print("Make sure the server is running: docker-compose up\n")
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}\n")
