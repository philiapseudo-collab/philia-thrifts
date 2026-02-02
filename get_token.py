import requests
import urllib.parse
import json

# --- CONFIGURATION ---
CLIENT_KEY = "sbawyt08o3l3o9d4ti".strip()
CLIENT_SECRET = "4wRBEuwM3Bn4lNBzB2VheFcAh82qIoNZ".strip()
REDIRECT_URI = "https://example.com/callback" 

# --- STEP 1: AUTHORIZE ---
base_url = "https://www.tiktok.com/v2/auth/authorize/"
csrf_state = "final_attempt_123" 
params = {
    "client_key": CLIENT_KEY,
    "response_type": "code",
    "scope": "user.info.basic,user.info.profile", 
    "redirect_uri": REDIRECT_URI,
    "state": csrf_state
}
auth_url = f"{base_url}?{urllib.parse.urlencode(params)}"

print("\n=== STEP 1: AUTHORIZE ===")
print("Click this link:\n")
print(auth_url)
print("\n" + "="*30)

# --- STEP 2: CAPTURE & CLEAN CODE ---
print("1. Authorize -> Redirect to example.com")
print("2. Copy the code from the URL.")
raw_input = input("\nPaste the code (or the whole URL) here: ").strip()

# --- THE FIX: SMART CLEANING ---
# 1. If user pasted whole URL, find the 'code=' part
if "code=" in raw_input:
    auth_code = raw_input.split("code=")[1]
else:
    auth_code = raw_input

# 2. Cut off anything after '&' (like &scopes=...)
if "&" in auth_code:
    auth_code = auth_code.split("&")[0]

# 3. Handle URL encoding (e.g. changing %21 to !)
auth_code = urllib.parse.unquote(auth_code)

print(f"\n[DEBUG] Cleaned Code to send: {auth_code[:10]}...{auth_code[-5:]}")

# --- STEP 3: EXCHANGE ---
token_url = "https://open.tiktokapis.com/v2/oauth/token/"
payload = {
    "client_key": CLIENT_KEY,
    "client_secret": CLIENT_SECRET,
    "code": auth_code,
    "grant_type": "authorization_code",
    "redirect_uri": REDIRECT_URI
}

print("\n=== STEP 3: EXCHANGING... ===")
response = requests.post(token_url, data=payload)

try:
    json_data = response.json()
    # Check inside 'data' if it exists, otherwise use top level
    data_obj = json_data.get('data', json_data)

    if 'access_token' in data_obj:
        print("\n✅ VICTORY! HERE ARE YOUR KEYS:\n")
        print(f"TIKTOK_ACCESS_TOKEN={data_obj['access_token']}")
        print(f"TIKTOK_REFRESH_TOKEN={data_obj.get('refresh_token')}")
        print(f"TIKTOK_OPEN_ID={data_obj.get('open_id')}")
        print("\n[Action]: Copy these into your .env file.")
    else:
        print("\n❌ FAILED. RAW RESPONSE:")
        print(json.dumps(json_data, indent=2))
except Exception as e:
    print(f"Error: {e}")
    print(response.text)