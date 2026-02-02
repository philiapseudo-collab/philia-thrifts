"""Verify environment configuration is properly loaded."""
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("🔍 Configuration Verification")
print("=" * 60)

# Check OpenAI
openai_key = os.getenv("OPENAI_API_KEY", "")
if openai_key and not openai_key.endswith("_here"):
    print(f"✅ OPENAI_API_KEY: {openai_key[:20]}...")
else:
    print("❌ OPENAI_API_KEY: Not set or still placeholder")

# Check TikTok Business ID
biz_id = os.getenv("TIKTOK_BUSINESS_ID", "")
if biz_id and not biz_id.endswith("_here"):
    print(f"✅ TIKTOK_BUSINESS_ID: {biz_id}")
else:
    print("❌ TIKTOK_BUSINESS_ID: Not set or still placeholder")

# Check Webhook Secret
webhook_secret = os.getenv("TIKTOK_WEBHOOK_SECRET", "")
if webhook_secret and not webhook_secret.endswith("_here"):
    print(f"✅ TIKTOK_WEBHOOK_SECRET: {webhook_secret[:10]}...")
else:
    print("❌ TIKTOK_WEBHOOK_SECRET: Not set or still placeholder")

# Check existing TikTok credentials (should already be set)
access_token = os.getenv("TIKTOK_ACCESS_TOKEN", "")
if access_token and not access_token.endswith("_here"):
    print(f"✅ TIKTOK_ACCESS_TOKEN: {access_token[:20]}... (already set)")
else:
    print("⚠️  TIKTOK_ACCESS_TOKEN: Not found")

print("=" * 60)
print("💡 To complete setup:")
print("   1. Edit .env file with your real credentials")
print("   2. Run: python verify_config.py")
print("=" * 60)
