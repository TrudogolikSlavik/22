import os
import sys

import requests

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

BASE_URL = "http://localhost:8080"

def test_endpoints():
    """Test all API endpoints"""

    print("=" * 60)
    print("Testing Knowledge Base API")
    print("=" * 60)

    # 1. Test public endpoints
    print("\n1. Testing public endpoints:")

    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/debug-tables", "Debug tables"),
        ("/docs", "Swagger UI"),
    ]

    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            status = "✓" if response.status_code < 400 else "✗"
            print(f"  {status} {description}: {response.status_code}")
        except Exception as e:
            print(f"  ✗ {description}: Error - {e}")

    # 2. Test registration
    print("\n2. Testing user registration:")

    user_data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "is_active": True
    }

    try:
        response = requests.post(
            f"{BASE_URL}/auth/register",
            json=user_data,
            timeout=5
        )

        if response.status_code == 200:
            print("  ✓ Registration successful")
            print(f"    User ID: {response.json().get('id')}")
        elif response.status_code == 400:
            print("  ! User already exists")
        else:
            print(f"  ✗ Registration failed: {response.status_code}")
            print(f"    Response: {response.text}")

    except Exception as e:
        print(f"  ✗ Registration error: {e}")

    # 3. Test login
    print("\n3. Testing login:")

    login_data = {
        "username": "test@example.com",
        "password": "testpassword123"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data=login_data,
            timeout=5
        )

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")
            print("  ✓ Login successful")
            print(f"    Token type: {token_data.get('token_type')}")
            return access_token
        else:
            print(f"  ✗ Login failed: {response.status_code}")
            print(f"    Response: {response.text}")

    except Exception as e:
        print(f"  ✗ Login error: {e}")

    return None

def test_authenticated_endpoints(token):
    """Test endpoints that require authentication"""

    if not token:
        print("\nSkipping authenticated tests (no token)")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("\n" + "=" * 60)
    print("Testing authenticated endpoints")
    print("=" * 60)

    # 1. Test current user info
    print("\n1. Testing user info:")
    try:
        response = requests.get(
            f"{BASE_URL}/users/me",
            headers=headers,
            timeout=5
        )

        if response.status_code == 200:
            user_info = response.json()
            print("  ✓ User info retrieved")
            print(f"    Email: {user_info.get('email')}")
            print(f"    User ID: {user_info.get('id')}")
        else:
            print(f"  ✗ Failed: {response.status_code}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    # 2. Test document creation
    print("\n2. Testing document creation:")

    document_data = {
        "title": "Test Document",
        "content": "This is a test document created via API testing."
    }

    try:
        response = requests.post(
            f"{BASE_URL}/documents/",
            json=document_data,
            headers=headers,
            timeout=5
        )

        if response.status_code == 200:
            document = response.json()
            print("  ✓ Document created")
            print(f"    Document ID: {document.get('id')}")
            print(f"    Title: {document.get('title')}")
            return document.get("id")
        else:
            print(f"  ✗ Failed: {response.status_code}")
            print(f"    Response: {response.text}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    return None

def test_document_operations(token, document_id):
    """Test document operations"""

    if not token or not document_id:
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    print("\n3. Testing document operations:")

    # Get document
    try:
        response = requests.get(
            f"{BASE_URL}/documents/{document_id}",
            headers=headers,
            timeout=5
        )

        if response.status_code == 200:
            print("  ✓ Document retrieved")
        else:
            print(f"  ✗ Get failed: {response.status_code}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    # List documents
    try:
        response = requests.get(
            f"{BASE_URL}/documents/",
            headers=headers,
            timeout=5
        )

        if response.status_code == 200:
            documents = response.json()
            print(f"  ✓ Documents listed: {len(documents)} documents")
        else:
            print(f"  ✗ List failed: {response.status_code}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    # Update document
    update_data = {
        "title": "Updated Test Document",
        "content": "This document has been updated via API testing."
    }

    try:
        response = requests.put(
            f"{BASE_URL}/documents/{document_id}",
            json=update_data,
            headers=headers,
            timeout=5
        )

        if response.status_code == 200:
            print("  ✓ Document updated")
        else:
            print(f"  ✗ Update failed: {response.status_code}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    # Analyze document (if has content)
    try:
        response = requests.post(
            f"{BASE_URL}/documents/{document_id}/analyze",
            headers=headers,
            timeout=10
        )

        if response.status_code == 200:
            analysis = response.json()
            print("  ✓ Document analyzed")
            print(f"    Summary length: {len(analysis.get('summary', ''))} chars")
            print(f"    Keywords: {len(analysis.get('keywords', []))}")
        else:
            print(f"  ✗ Analysis failed: {response.status_code}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

def main():
    print("Knowledge Base API Test Suite")
    print(f"Base URL: {BASE_URL}")

    # Run tests
    token = test_endpoints()

    if token:
        document_id = test_authenticated_endpoints(token)
        if document_id:
            test_document_operations(token, document_id)

    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
