#!/usr/bin/env python3
"""
Test script to verify POC invitation endpoints are working correctly.
Run this after restarting the backend to confirm the new routes are available.
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_endpoints():
    print("Testing POC Invitation Endpoints...")
    print("=" * 60)
    
    # Test 1: Check if the new public endpoint exists (will 404 with invalid token, but not 404 for route)
    print("\n1. Testing new endpoint: /poc-invitations/validate/{token}")
    try:
        response = requests.get(f"{BASE_URL}/poc-invitations/validate/test-token-123")
        if response.status_code == 404 and "Invitation not found" in response.text:
            print("   ✅ NEW ENDPOINT EXISTS (returns 'Invitation not found' as expected)")
        elif response.status_code == 404 and "Not Found" in response.text:
            print("   ❌ NEW ENDPOINT DOES NOT EXIST (route not found)")
            print(f"   Response: {response.text[:200]}")
        else:
            print(f"   ✅ NEW ENDPOINT EXISTS (status: {response.status_code})")
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to backend at", BASE_URL)
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Check docs to see if endpoint is listed
    print("\n2. Checking API documentation for new endpoints...")
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if "poc-invitations" in response.text.lower():
            print("   ✅ New 'poc-invitations' endpoint found in API docs")
        else:
            print("   ❌ New endpoint NOT found in API docs")
            print("   ⚠️  Backend may not have been restarted with new code")
    except Exception as e:
        print(f"   ❌ Error checking docs: {e}")
    
    # Test 3: Check OpenAPI schema
    print("\n3. Checking OpenAPI schema...")
    try:
        response = requests.get(f"{BASE_URL}/openapi.json")
        if response.status_code == 200:
            openapi_data = response.json()
            paths = openapi_data.get("paths", {})
            
            new_validate = "/poc-invitations/validate/{token}" in paths
            new_accept = "/poc-invitations/accept" in paths
            
            if new_validate and new_accept:
                print("   ✅ Both new endpoints found in OpenAPI schema:")
                print("      - /poc-invitations/validate/{token}")
                print("      - /poc-invitations/accept")
            else:
                print("   ❌ New endpoints NOT in OpenAPI schema")
                print(f"      validate endpoint: {'Found' if new_validate else 'NOT FOUND'}")
                print(f"      accept endpoint: {'Found' if new_accept else 'NOT FOUND'}")
                print("\n   ⚠️  BACKEND MUST BE RESTARTED!")
    except Exception as e:
        print(f"   ❌ Error checking OpenAPI: {e}")
    
    print("\n" + "=" * 60)
    print("\nIf endpoints are NOT found, restart the backend:")
    print("  Docker: docker compose restart backend")
    print("  Local:  Kill uvicorn process and restart")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    test_endpoints()
