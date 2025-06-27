#!/usr/bin/env python3
"""
Comprehensive deployment readiness check for Melbourne Celebrant Portal.
This script verifies all components are properly configured and working.
"""

import os
import sys
import json
import requests
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple

class DeploymentChecker:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3001"
        self.issues = []
        self.successes = []
        
    def log_success(self, check: str, message: str):
        """Log a successful check."""
        self.successes.append(f"✅ {check}: {message}")
        print(f"✅ {check}: {message}")
        
    def log_issue(self, check: str, message: str, severity: str = "ERROR"):
        """Log an issue found during checks."""
        self.issues.append(f"❌ {severity} - {check}: {message}")
        print(f"❌ {severity} - {check}: {message}")
        
    def check_backend_health(self) -> bool:
        """Check if backend is running and healthy."""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "healthy":
                    self.log_success("Backend Health", f"Backend is healthy (v{data.get('version')})")
                    return True
                else:
                    self.log_issue("Backend Health", f"Backend reports unhealthy status: {data}")
                    return False
            else:
                self.log_issue("Backend Health", f"Backend health check failed: {response.status_code}")
                return False
        except Exception as e:
            self.log_issue("Backend Health", f"Cannot connect to backend: {e}")
            return False
            
    def check_authentication(self) -> Tuple[bool, str]:
        """Test authentication flow."""
        try:
            login_data = {
                "email": "admin@melbournecelebrant.com",
                "password": "admin123"
            }
            response = requests.post(f"{self.backend_url}/api/auth/login", json=login_data, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("access_token")
                if token:
                    self.log_success("Authentication", "Login successful, token obtained")
                    return True, token
                else:
                    self.log_issue("Authentication", "Login response missing access token")
                    return False, ""
            else:
                self.log_issue("Authentication", f"Login failed: {response.status_code} - {response.text}")
                return False, ""
        except Exception as e:
            self.log_issue("Authentication", f"Authentication test failed: {e}")
            return False, ""
            
    def check_api_endpoints(self, token: str) -> bool:
        """Test critical API endpoints."""
        headers = {"Authorization": f"Bearer {token}"}
        endpoints = [
            ("/api/auth/me", "User Info"),
            ("/api/dashboard/metrics", "Dashboard Metrics"),
            ("/api/couples/", "Couples List")
        ]
        
        all_good = True
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", headers=headers, timeout=5)
                if response.status_code == 200:
                    self.log_success(f"API - {name}", f"Endpoint {endpoint} working")
                else:
                    self.log_issue(f"API - {name}", f"Endpoint {endpoint} failed: {response.status_code}")
                    all_good = False
            except Exception as e:
                self.log_issue(f"API - {name}", f"Endpoint {endpoint} error: {e}")
                all_good = False
                
        return all_good
        
    def check_frontend_accessibility(self) -> bool:
        """Check if frontend is accessible."""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                if "Celebrant Portal" in response.text:
                    self.log_success("Frontend", "Frontend is accessible and loading")
                    return True
                else:
                    self.log_issue("Frontend", "Frontend accessible but content may be wrong")
                    return False
            else:
                self.log_issue("Frontend", f"Frontend not accessible: {response.status_code}")
                return False
        except Exception as e:
            self.log_issue("Frontend", f"Cannot connect to frontend: {e}")
            return False
            
    def check_file_structure(self) -> bool:
        """Check critical files exist."""
        critical_files = [
            "celebrant-portal-v2/backend/app/main.py",
            "celebrant-portal-v2/backend/requirements.txt",
            "src/app/page.tsx",
            "src/app/login/page.tsx",
            "src/app/dashboard/page.tsx",
            "package.json",
            "next.config.js",
            "Procfile"
        ]
        
        all_good = True
        for file_path in critical_files:
            if Path(file_path).exists():
                self.log_success("File Structure", f"{file_path} exists")
            else:
                self.log_issue("File Structure", f"Missing critical file: {file_path}")
                all_good = False
                
        return all_good
        
    def check_environment_config(self) -> bool:
        """Check environment configuration."""
        config_checks = []
        
        # Check backend config
        try:
            from celebrant_portal_v2.backend.app.config import settings
            if settings.secret_key != "your-secret-key-here":
                config_checks.append(("Backend Secret Key", True, "Secret key is configured"))
            else:
                config_checks.append(("Backend Secret Key", False, "Using default secret key"))
                
            if len(settings.cors_origins) > 0:
                config_checks.append(("CORS Origins", True, f"CORS configured: {settings.cors_origins}"))
            else:
                config_checks.append(("CORS Origins", False, "No CORS origins configured"))
                
        except Exception as e:
            config_checks.append(("Backend Config", False, f"Cannot load backend config: {e}"))
            
        all_good = True
        for check_name, success, message in config_checks:
            if success:
                self.log_success("Environment", f"{check_name}: {message}")
            else:
                self.log_issue("Environment", f"{check_name}: {message}")
                all_good = False
                
        return all_good
        
    def check_deployment_files(self) -> bool:
        """Check deployment-specific files."""
        deployment_files = {
            "Procfile": "Web process definition",
            "runtime.txt": "Python runtime version",
            "requirements.txt": "Python dependencies",
            "package.json": "Node.js dependencies",
            "next.config.js": "Next.js configuration"
        }
        
        all_good = True
        for file_name, description in deployment_files.items():
            if Path(file_name).exists():
                self.log_success("Deployment Files", f"{file_name} ({description}) exists")
            else:
                self.log_issue("Deployment Files", f"Missing {file_name} ({description})")
                all_good = False
                
        return all_good
        
    def run_all_checks(self) -> bool:
        """Run all deployment checks."""
        print("🚀 Starting comprehensive deployment readiness check...\n")
        
        # File structure checks (don't require running services)
        file_structure_ok = self.check_file_structure()
        deployment_files_ok = self.check_deployment_files()
        env_config_ok = self.check_environment_config()
        
        # Service checks (require running services)
        backend_ok = self.check_backend_health()
        auth_ok, token = self.check_authentication() if backend_ok else (False, "")
        api_ok = self.check_api_endpoints(token) if auth_ok else False
        frontend_ok = self.check_frontend_accessibility()
        
        # Summary
        print("\n" + "="*60)
        print("📊 DEPLOYMENT READINESS SUMMARY")
        print("="*60)
        
        all_checks = [
            ("File Structure", file_structure_ok),
            ("Deployment Files", deployment_files_ok),
            ("Environment Config", env_config_ok),
            ("Backend Health", backend_ok),
            ("Authentication", auth_ok),
            ("API Endpoints", api_ok),
            ("Frontend Accessibility", frontend_ok)
        ]
        
        for check_name, passed in all_checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} {check_name}")
            
        overall_ready = all(passed for _, passed in all_checks)
        
        print("\n" + "="*60)
        if overall_ready:
            print("🎉 DEPLOYMENT READY! All checks passed.")
            print("The application is ready for production deployment.")
        else:
            print("⚠️  DEPLOYMENT NOT READY. Please fix the issues above.")
            print(f"Found {len(self.issues)} issues that need attention.")
            
        print("="*60)
        return overall_ready

if __name__ == "__main__":
    checker = DeploymentChecker()
    ready = checker.run_all_checks()
    sys.exit(0 if ready else 1) 