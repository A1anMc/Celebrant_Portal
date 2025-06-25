#!/usr/bin/env python3
"""
Deployment verification script for Melbourne Celebrant Portal.
"""

import requests
import time
import sys

def test_health_endpoint(url, max_retries=10, delay=30):
    """Test the health endpoint with retries."""
    print(f"🔍 Testing health endpoint: {url}")
    
    for attempt in range(1, max_retries + 1):
        try:
            print(f"  Attempt {attempt}/{max_retries}...")
            response = requests.get(f"{url}/health", timeout=10)
            
            if response.status_code == 200:
                print(f"✅ Health check passed! Status: {response.status_code}")
                try:
                    data = response.json()
                    print(f"   Response: {data}")
                except:
                    print(f"   Response: {response.text[:100]}")
                return True
            else:
                print(f"❌ Health check failed. Status: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection error: {e}")
        
        if attempt < max_retries:
            print(f"   Waiting {delay} seconds before retry...")
            time.sleep(delay)
    
    return False

def test_api_endpoints(url):
    """Test basic API endpoints."""
    endpoints = [
        "/",
        "/docs",
        "/health"
    ]
    
    print(f"\n🔍 Testing API endpoints...")
    results = []
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{url}{endpoint}", timeout=10)
            status = "✅ PASS" if response.status_code in [200, 307, 404] else "❌ FAIL"
            print(f"  {endpoint}: {status} ({response.status_code})")
            results.append((endpoint, response.status_code in [200, 307, 404]))
        except requests.exceptions.RequestException as e:
            print(f"  {endpoint}: ❌ FAIL (Connection error)")
            results.append((endpoint, False))
    
    return results

def main():
    """Main verification function."""
    url = "https://amelbournecelebrant-6ykh.onrender.com"
    
    print("🚀 Melbourne Celebrant Portal - Deployment Verification")
    print("=" * 60)
    print(f"Target URL: {url}")
    print("=" * 60)
    
    # Test health endpoint with retries
    health_ok = test_health_endpoint(url)
    
    if health_ok:
        # Test other endpoints
        endpoint_results = test_api_endpoints(url)
        
        print("\n" + "=" * 60)
        print("📊 SUMMARY:")
        print(f"  Health Check: {'✅ PASS' if health_ok else '❌ FAIL'}")
        
        for endpoint, result in endpoint_results:
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"  {endpoint}: {status}")
        
        all_passed = health_ok and all(result for _, result in endpoint_results)
        
        if all_passed:
            print("\n🎉 Deployment verification successful!")
            print("Your Melbourne Celebrant Portal is now live!")
            print(f"Visit: {url}")
            return 0
        else:
            print("\n⚠️  Some tests failed, but the service might still be functional.")
            return 1
    else:
        print("\n❌ Health check failed. Please check:")
        print("   1. Environment variables are set correctly in Render")
        print("   2. Database connection is working")
        print("   3. Application logs in Render dashboard")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 