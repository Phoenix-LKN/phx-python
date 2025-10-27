"""
Test script to verify backend authentication
"""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Test 1: Check if backend is running
print("=" * 50)
print("Testing Backend Connection")
print("=" * 50)

try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=5)
    print(f"✓ Backend is running: {response.status_code}")
    print(f"  Response: {response.json()}")
except Exception as e:
    print(f"✗ Backend connection failed: {e}")
    print("  Make sure to run: python3 backend/main.py")
    exit(1)

# Test 2: Try login with test credentials
print("\n" + "=" * 50)
print("Testing Authentication Endpoint")
print("=" * 50)

# Replace these with your actual Supabase user credentials
test_email = input("Enter your email: ").strip()
test_password = input("Enter your password: ").strip()

try:
    response = requests.post(
        f"{BACKEND_URL}/api/auth/login",
        json={"email": test_email, "password": test_password},
        timeout=10
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get("access_token"):
            print("\n✓ Authentication successful!")
            print(f"  Token: {data['access_token'][:50]}...")
            print(f"  User: {data.get('user', {})}")
        else:
            print("\n✗ No access token in response")
    else:
        print("\n✗ Authentication failed")
        print(f"  Error: {response.json()}")
        
except Exception as e:
    print(f"\n✗ Request failed: {e}")

print("\n" + "=" * 50)
