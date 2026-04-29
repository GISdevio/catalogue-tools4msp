#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "requests>=2.31.0",
# ]
# ///
"""
Resource loading test for CKAN static files and assets.

Tests all CSS, JS, images, and other static resources load correctly.
"""

import requests
import sys

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def test_resource(url, resource_name):
    """Test if a resource loads correctly"""
    try:
        response = requests.get(url, timeout=10)
        success = response.status_code == 200
        status = f"{Colors.GREEN}✅" if success else f"{Colors.RED}❌"
        print(f"{status} {resource_name}: {response.status_code}")
        return success
    except Exception as e:
        print(f"{Colors.RED}❌ {resource_name}: ERROR - {e}")
        return False

def main():
    base_url = "http://localhost:5000"
    
    print(f"{Colors.BOLD}🔍 Testing Static Resource Loading{Colors.ENDC}")
    print(f"Base URL: {base_url}\n")
    
    # Test static files from branding extension
    resources = [
        ("/main.css", "Main CSS"),
        ("/logo.png", "Logo"),
        ("/favicon.png", "Favicon"),
        ("/img1.jpg", "Carousel Image 1"),
        ("/img2.jpg", "Carousel Image 2"), 
        ("/img3.jpg", "Carousel Image 3"),
        ("/img4.jpg", "Carousel Image 4"),
        ("/bg.svg", "Background SVG"),
    ]
    
    passed = 0
    total = len(resources)
    
    for path, name in resources:
        if test_resource(f"{base_url}{path}", name):
            passed += 1
    
    print(f"\n{Colors.BOLD}📊 Resource Test Summary{Colors.ENDC}")
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 All resources loading correctly!{Colors.ENDC}")
        return True
    else:
        print(f"{Colors.RED}⚠️ {total - passed} resource(s) failed to load.{Colors.ENDC}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)