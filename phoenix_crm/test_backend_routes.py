"""
Test which routes are available on the backend
"""
import requests

backend_url = "http://localhost:8000"

print("=" * 50)
print("Testing Available Backend Routes")
print("=" * 50)

# Test root
try:
    resp = requests.get(f"{backend_url}/")
    print(f"\n✓ GET / : {resp.status_code}")
    print(f"  {resp.json()}")
except Exception as e:
    print(f"✗ GET / failed: {e}")

# Test health
try:
    resp = requests.get(f"{backend_url}/health")
    print(f"\n✓ GET /health : {resp.status_code}")
    print(f"  {resp.json()}")
except Exception as e:
    print(f"✗ GET /health failed: {e}")

# Test docs (FastAPI auto-generated)
try:
    resp = requests.get(f"{backend_url}/docs")
    print(f"\n✓ GET /docs : {resp.status_code}")
    print("  Open http://localhost:8000/docs in your browser to see all available routes")
except Exception as e:
    print(f"✗ GET /docs failed: {e}")

# Test openapi.json to see all routes
try:
    resp = requests.get(f"{backend_url}/openapi.json")
    if resp.status_code == 200:
        openapi = resp.json()
        print(f"\n✓ Available routes:")
        for path, methods in openapi.get('paths', {}).items():
            for method in methods.keys():
                print(f"  {method.upper():6} {path}")
except Exception as e:
    print(f"✗ Failed to get routes: {e}")

print("\n" + "=" * 50)
