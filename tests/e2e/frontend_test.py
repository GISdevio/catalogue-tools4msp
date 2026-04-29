#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = [
#     "playwright>=1.40.0",
#     "requests>=2.31.0",
# ]
# ///
"""
End-to-end test for CKAN 2.11 frontend using Playwright.

This test validates:
1. Homepage loads without template errors
2. MSP schema pages render correctly 
3. Custom templates and styling work
4. JavaScript functionality works
5. Search and navigation work properly

Usage:
    uv run tests/e2e/frontend_test.py
"""

import asyncio
import sys
import time
import requests
from playwright.async_api import async_playwright

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log(message, color=None):
    if color:
        print(f"{color}{message}{Colors.ENDC}")
    else:
        print(message)

def test_result(test_name, success, details=None):
    status = f"{Colors.GREEN}✅ PASS" if success else f"{Colors.RED}❌ FAIL"
    log(f"{status}: {test_name}")
    if details and not success:
        log(f"   Details: {details}", Colors.YELLOW)
    return success

class FrontendE2ETester:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.browser = None
        self.page = None
        
    async def setup(self):
        """Setup Playwright browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=True,
            executable_path="/usr/bin/google-chrome"
        )
        self.page = await self.browser.new_page()
        
        # Set longer timeout for CKAN responses
        self.page.set_default_timeout(30000)
        
    async def teardown(self):
        """Cleanup Playwright resources"""
        if self.browser:
            await self.browser.close()
    
    def wait_for_ckan(self, max_wait=60):
        """Wait for CKAN to be ready"""
        log("🕐 Waiting for CKAN to be ready...", Colors.BLUE)
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(self.base_url, timeout=10)
                if response.status_code == 200:
                    return test_result("CKAN availability", True)
            except requests.exceptions.RequestException:
                pass
            time.sleep(2)
            
        return test_result("CKAN availability", False, f"CKAN not ready after {max_wait}s")
    
    async def test_homepage_loads(self):
        """Test homepage loads without errors"""
        try:
            response = await self.page.goto(self.base_url)
            
            if response.status != 200:
                return test_result("Homepage load", False, f"Status: {response.status}")
            
            # Wait for page to be fully loaded
            await self.page.wait_for_load_state('networkidle')
            
            # Check for basic HTML structure
            title = await self.page.title()
            success = "Tools4MSP" in title or "CKAN" in title
            
            return test_result("Homepage load", success, f"Title: {title}" if not success else None)
            
        except Exception as e:
            return test_result("Homepage load", False, str(e))
    
    async def test_template_rendering(self):
        """Test custom template rendering"""
        try:
            await self.page.goto(self.base_url)
            await self.page.wait_for_load_state('networkidle')
            
            # Check for template elements that should be present
            checks = [
                ("Main content", 'role="main"'),
                ("Featured Categories", "Featured Categories"),
                ("Featured Datasets", "Featured Datasets"), 
                ("Featured Groups", "Featured Groups"),
                ("Search form", 'name="q"'),
            ]
            
            all_passed = True
            for check_name, selector in checks:
                try:
                    if "Featured" in selector:
                        await self.page.locator(f'text="{selector}"').first.wait_for(timeout=5000)
                    else:
                        await self.page.locator(f'[{selector}]').first.wait_for(timeout=5000)
                    test_result(f"Template: {check_name}", True)
                except Exception:
                    test_result(f"Template: {check_name}", False)
                    all_passed = False
                    
            return all_passed
            
        except Exception as e:
            return test_result("Template rendering", False, str(e))
    
    async def test_css_loading(self):
        """Test CSS and styling loads correctly"""
        try:
            await self.page.goto(self.base_url)
            await self.page.wait_for_load_state('networkidle')
            
            # Check for CSS files
            stylesheets = await self.page.locator('link[rel="stylesheet"]').all()
            css_urls = []
            for sheet in stylesheets:
                href = await sheet.get_attribute('href')
                if href:
                    css_urls.append(href)
            
            # Check for main.css (custom styling)
            has_main_css = any('/main.css' in url for url in css_urls)
            
            # Check for FontAwesome
            has_fontawesome = any('font-awesome' in url or 'fontawesome' in url for url in css_urls)
            
            # Check for Splide
            has_splide = any('splide' in url for url in css_urls)
            
            test_result("CSS: main.css", has_main_css)
            test_result("CSS: FontAwesome", has_fontawesome)
            test_result("CSS: Splide carousel", has_splide)
            
            return has_main_css and has_fontawesome and has_splide
            
        except Exception as e:
            return test_result("CSS loading", False, str(e))
    
    async def test_javascript_functionality(self):
        """Test JavaScript functionality"""
        try:
            await self.page.goto(self.base_url)
            await self.page.wait_for_load_state('networkidle')
            
            # Check for JavaScript errors in console
            js_errors = []
            self.page.on('console', lambda msg: js_errors.append(msg.text) if msg.type == 'error' else None)
            
            # Wait a bit for any JS to execute
            await self.page.wait_for_timeout(3000)
            
            # Check if Splide carousel is initialized
            try:
                carousel = await self.page.locator('.splide').first.wait_for(timeout=5000)
                carousel_visible = await carousel.is_visible()
                test_result("JS: Splide carousel", carousel_visible)
            except Exception:
                test_result("JS: Splide carousel", False)
                
            # Check for critical JS errors
            critical_errors = [err for err in js_errors if any(word in err.lower() for word in ['error', 'failed', 'undefined'])]
            has_critical_errors = len(critical_errors) > 0
            
            if has_critical_errors:
                test_result("JS: No critical errors", False, f"Errors: {critical_errors[:3]}")
            else:
                test_result("JS: No critical errors", True)
                
            return not has_critical_errors
            
        except Exception as e:
            return test_result("JavaScript functionality", False, str(e))
    
    async def test_schema_pages(self):
        """Test MSP schema pages load correctly"""
        schema_types = ['msp-data', 'msp-tool', 'msp-portal']
        all_passed = True
        
        for schema_type in schema_types:
            try:
                url = f"{self.base_url}/{schema_type}/"
                response = await self.page.goto(url)
                
                if response.status != 200:
                    test_result(f"Schema page: {schema_type}", False, f"Status: {response.status}")
                    all_passed = False
                    continue
                    
                await self.page.wait_for_load_state('networkidle')
                
                # Check for dataset listing page elements
                has_search = await self.page.locator('[name="q"]').count() > 0
                has_facets = await self.page.locator('.facet').count() > 0 or await self.page.locator('[data-module="autocomplete"]').count() > 0
                
                page_success = has_search  # At minimum should have search
                test_result(f"Schema page: {schema_type}", page_success, 
                           f"Search: {has_search}, Facets: {has_facets}" if not page_success else None)
                           
                if not page_success:
                    all_passed = False
                    
            except Exception as e:
                test_result(f"Schema page: {schema_type}", False, str(e))
                all_passed = False
                
        return all_passed
    
    async def test_navigation(self):
        """Test navigation and routing"""
        try:
            await self.page.goto(self.base_url)
            await self.page.wait_for_load_state('networkidle')
            
            # Test navigation links
            nav_tests = [
                ("Datasets link", "//a[contains(@href, '/dataset') or contains(text(), 'Datasets')]"),
                ("Organizations link", "//a[contains(@href, '/organization') or contains(text(), 'Organizations')]"),
                ("Groups link", "//a[contains(@href, '/group') or contains(text(), 'Groups')]"),
            ]
            
            all_passed = True
            for test_name, xpath in nav_tests:
                try:
                    element = self.page.locator(f"xpath={xpath}").first
                    is_visible = await element.is_visible()
                    test_result(f"Navigation: {test_name}", is_visible)
                    if not is_visible:
                        all_passed = False
                except Exception:
                    test_result(f"Navigation: {test_name}", False)
                    all_passed = False
                    
            return all_passed
            
        except Exception as e:
            return test_result("Navigation test", False, str(e))
    
    async def test_responsive_design(self):
        """Test responsive design works"""
        try:
            await self.page.goto(self.base_url)
            await self.page.wait_for_load_state('networkidle')
            
            # Test different viewport sizes
            viewports = [
                ("Desktop", 1920, 1080),
                ("Tablet", 768, 1024),
                ("Mobile", 375, 667),
            ]
            
            all_passed = True
            for name, width, height in viewports:
                await self.page.set_viewport_size({"width": width, "height": height})
                await self.page.wait_for_timeout(1000)
                
                # Check if main content is visible
                main_visible = await self.page.locator('[role="main"]').is_visible()
                test_result(f"Responsive: {name} ({width}x{height})", main_visible)
                
                if not main_visible:
                    all_passed = False
                    
            return all_passed
            
        except Exception as e:
            return test_result("Responsive design", False, str(e))
    
    async def run_all_tests(self):
        """Run all frontend tests"""
        log(f"\n{Colors.BOLD}🧪 Running Frontend E2E Tests with Playwright{Colors.ENDC}", Colors.BLUE)
        log(f"Target URL: {self.base_url}\n")
        
        # First check if CKAN is available
        if not self.wait_for_ckan():
            log(f"{Colors.RED}CKAN is not available. Please start the services first.{Colors.ENDC}")
            return False
            
        await self.setup()
        
        tests = [
            ("Homepage Load", self.test_homepage_loads),
            ("Template Rendering", self.test_template_rendering),
            ("CSS Loading", self.test_css_loading),
            ("JavaScript Functionality", self.test_javascript_functionality),
            ("Schema Pages", self.test_schema_pages),
            ("Navigation", self.test_navigation),
            ("Responsive Design", self.test_responsive_design),
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            log(f"\n📋 Running: {test_name}", Colors.BLUE)
            try:
                if await test_func():
                    passed += 1
            except Exception as e:
                test_result(test_name, False, str(e))
                
        await self.teardown()
        
        # Summary
        log(f"\n{Colors.BOLD}📊 Test Summary{Colors.ENDC}")
        log(f"Passed: {passed}/{total}")
        
        if passed == total:
            log(f"{Colors.GREEN}🎉 All tests passed! Frontend is working correctly.{Colors.ENDC}")
            return True
        else:
            log(f"{Colors.RED}⚠️ {total - passed} test(s) failed. Check the issues above.{Colors.ENDC}")
            return False

async def main():
    """Main entry point"""
    tester = FrontendE2ETester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())