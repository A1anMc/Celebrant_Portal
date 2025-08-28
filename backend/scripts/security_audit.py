#!/usr/bin/env python3
"""
Security Audit Script for Melbourne Celebrant Portal
Performs security checks and validation for staging/production environments.
"""

import requests
import json
import argparse
import logging
from typing import Dict, List, Any
from dataclasses import dataclass
from urllib.parse import urljoin
import ssl
import socket
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SecurityCheck:
    """Security check result."""
    name: str
    status: str  # PASS, FAIL, WARNING
    description: str
    details: Dict[str, Any] = None
    recommendation: str = ""

class SecurityAuditor:
    """Security auditing utility for the Celebrant Portal."""
    
    def __init__(self, base_url: str, auth_token: str = None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.session = requests.Session()
        if auth_token:
            self.session.headers.update({'Authorization': f'Bearer {auth_token}'})
        self.session.headers.update({'User-Agent': 'SecurityAuditor/1.0'})
    
    def check_ssl_certificate(self) -> SecurityCheck:
        """Check SSL certificate validity."""
        try:
            # Extract hostname from URL
            from urllib.parse import urlparse
            parsed = urlparse(self.base_url)
            hostname = parsed.hostname
            port = parsed.port or (443 if parsed.scheme == 'https' else 80)
            
            if parsed.scheme != 'https':
                return SecurityCheck(
                    name="SSL Certificate",
                    status="FAIL",
                    description="HTTPS not enabled",
                    recommendation="Enable HTTPS for production environments"
                )
            
            # Check SSL certificate
            context = ssl.create_default_context()
            with socket.create_connection((hostname, port)) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check certificate expiration
                    from datetime import datetime
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.now()).days
                    
                    if days_until_expiry < 30:
                        return SecurityCheck(
                            name="SSL Certificate",
                            status="WARNING",
                            description=f"Certificate expires in {days_until_expiry} days",
                            details={"expiry_date": cert['notAfter']},
                            recommendation="Renew SSL certificate before expiration"
                        )
                    
                    return SecurityCheck(
                        name="SSL Certificate",
                        status="PASS",
                        description="Valid SSL certificate",
                        details={"expiry_date": cert['notAfter'], "days_until_expiry": days_until_expiry}
                    )
                    
        except Exception as e:
            return SecurityCheck(
                name="SSL Certificate",
                status="FAIL",
                description=f"SSL check failed: {str(e)}",
                recommendation="Verify SSL configuration"
            )
    
    def check_security_headers(self) -> SecurityCheck:
        """Check for security headers in responses."""
        try:
            response = self.session.get(self.base_url)
            headers = response.headers
            
            required_headers = {
                'X-Content-Type-Options': 'nosniff',
                'X-Frame-Options': ['DENY', 'SAMEORIGIN'],
                'X-XSS-Protection': '1; mode=block',
                'Strict-Transport-Security': None,  # Any value is good
                'Content-Security-Policy': None     # Any value is good
            }
            
            missing_headers = []
            weak_headers = []
            
            for header, expected_value in required_headers.items():
                if header not in headers:
                    missing_headers.append(header)
                elif expected_value and headers[header] not in expected_value:
                    weak_headers.append(f"{header}: {headers[header]}")
            
            if missing_headers:
                return SecurityCheck(
                    name="Security Headers",
                    status="FAIL",
                    description=f"Missing security headers: {', '.join(missing_headers)}",
                    details={"missing": missing_headers, "weak": weak_headers},
                    recommendation="Configure missing security headers"
                )
            elif weak_headers:
                return SecurityCheck(
                    name="Security Headers",
                    status="WARNING",
                    description=f"Weak security header values: {', '.join(weak_headers)}",
                    details={"weak": weak_headers},
                    recommendation="Review and strengthen security header values"
                )
            else:
                return SecurityCheck(
                    name="Security Headers",
                    status="PASS",
                    description="All security headers properly configured",
                    details={"headers_found": list(required_headers.keys())}
                )
                
        except Exception as e:
            return SecurityCheck(
                name="Security Headers",
                status="FAIL",
                description=f"Failed to check security headers: {str(e)}",
                recommendation="Verify application is accessible"
            )
    
    def check_authentication_endpoints(self) -> SecurityCheck:
        """Check authentication endpoints for common vulnerabilities."""
        auth_endpoints = [
            '/api/v1/auth/login',
            '/api/v1/auth/register',
            '/api/v1/auth/me'
        ]
        
        vulnerabilities = []
        
        for endpoint in auth_endpoints:
            url = urljoin(self.base_url, endpoint)
            
            # Check for rate limiting
            try:
                responses = []
                for _ in range(10):  # Try to trigger rate limiting
                    response = self.session.post(url, json={
                        'email': 'test@example.com',
                        'password': 'wrongpassword'
                    })
                    responses.append(response.status_code)
                
                # Check if rate limiting is working
                if responses.count(429) == 0:
                    vulnerabilities.append(f"No rate limiting on {endpoint}")
                    
            except Exception as e:
                vulnerabilities.append(f"Error testing {endpoint}: {str(e)}")
        
        if vulnerabilities:
            return SecurityCheck(
                name="Authentication Security",
                status="WARNING",
                description=f"Found {len(vulnerabilities)} potential issues",
                details={"vulnerabilities": vulnerabilities},
                recommendation="Review and fix authentication security issues"
            )
        else:
            return SecurityCheck(
                name="Authentication Security",
                status="PASS",
                description="Authentication endpoints appear secure",
                details={"endpoints_tested": auth_endpoints}
            )
    
    def check_cors_configuration(self) -> SecurityCheck:
        """Check CORS configuration for security issues."""
        try:
            # Test with different origins
            test_origins = [
                'https://malicious-site.com',
                'http://localhost:3000',
                'https://your-frontend-domain.com'
            ]
            
            cors_issues = []
            
            for origin in test_origins:
                headers = {'Origin': origin}
                response = self.session.options(self.base_url, headers=headers)
                
                acao = response.headers.get('Access-Control-Allow-Origin')
                if acao == '*' or acao == origin:
                    cors_issues.append(f"Overly permissive CORS for origin: {origin}")
            
            if cors_issues:
                return SecurityCheck(
                    name="CORS Configuration",
                    status="WARNING",
                    description=f"Found {len(cors_issues)} CORS issues",
                    details={"issues": cors_issues},
                    recommendation="Review CORS configuration and restrict allowed origins"
                )
            else:
                return SecurityCheck(
                    name="CORS Configuration",
                    status="PASS",
                    description="CORS configuration appears secure",
                    details={"origins_tested": test_origins}
                )
                
        except Exception as e:
            return SecurityCheck(
                name="CORS Configuration",
                status="FAIL",
                description=f"Failed to check CORS: {str(e)}",
                recommendation="Verify CORS configuration"
            )
    
    def check_sensitive_endpoints(self) -> SecurityCheck:
        """Check if sensitive endpoints are properly protected."""
        sensitive_endpoints = [
            '/api/v1/couples/',
            '/api/v1/invoices/',
            '/api/v1/ceremonies/',
            '/metrics',
            '/docs'
        ]
        
        unprotected_endpoints = []
        
        for endpoint in sensitive_endpoints:
            url = urljoin(self.base_url, endpoint)
            try:
                response = self.session.get(url)
                if response.status_code == 200:
                    unprotected_endpoints.append(endpoint)
            except Exception:
                pass
        
        if unprotected_endpoints:
            return SecurityCheck(
                name="Endpoint Protection",
                status="FAIL",
                description=f"Found {len(unprotected_endpoints)} unprotected endpoints",
                details={"unprotected": unprotected_endpoints},
                recommendation="Implement authentication for sensitive endpoints"
            )
        else:
            return SecurityCheck(
                name="Endpoint Protection",
                status="PASS",
                description="All sensitive endpoints are properly protected",
                details={"endpoints_tested": sensitive_endpoints}
            )
    
    def check_dependencies(self) -> SecurityCheck:
        """Check for known security vulnerabilities in dependencies."""
        try:
            # This would typically use a tool like safety or pip-audit
            # For now, we'll check if we can access the requirements
            import subprocess
            result = subprocess.run(['pip', 'list', '--format=json'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                return SecurityCheck(
                    name="Dependencies",
                    status="INFO",
                    description="Dependency check completed (manual review recommended)",
                    recommendation="Run 'pip-audit' or 'safety check' for detailed analysis"
                )
            else:
                return SecurityCheck(
                    name="Dependencies",
                    status="WARNING",
                    description="Could not check dependencies automatically",
                    recommendation="Manually review dependencies for security issues"
                )
                
        except Exception as e:
            return SecurityCheck(
                name="Dependencies",
                status="WARNING",
                description=f"Failed to check dependencies: {str(e)}",
                recommendation="Manually review dependencies for security issues"
            )
    
    def run_full_audit(self) -> List[SecurityCheck]:
        """Run all security checks."""
        logger.info("Starting security audit...")
        
        checks = [
            self.check_ssl_certificate(),
            self.check_security_headers(),
            self.check_authentication_endpoints(),
            self.check_cors_configuration(),
            self.check_sensitive_endpoints(),
            self.check_dependencies()
        ]
        
        return checks
    
    def generate_report(self, checks: List[SecurityCheck]) -> Dict[str, Any]:
        """Generate a comprehensive security report."""
        total_checks = len(checks)
        passed = sum(1 for c in checks if c.status == "PASS")
        failed = sum(1 for c in checks if c.status == "FAIL")
        warnings = sum(1 for c in checks if c.status == "WARNING")
        
        return {
            "timestamp": datetime.now().isoformat(),
            "target_url": self.base_url,
            "summary": {
                "total_checks": total_checks,
                "passed": passed,
                "failed": failed,
                "warnings": warnings,
                "success_rate": (passed / total_checks) * 100 if total_checks > 0 else 0
            },
            "checks": [
                {
                    "name": check.name,
                    "status": check.status,
                    "description": check.description,
                    "details": check.details,
                    "recommendation": check.recommendation
                }
                for check in checks
            ],
            "risk_level": "HIGH" if failed > 0 else "MEDIUM" if warnings > 0 else "LOW"
        }

def main():
    """Main function to run security audit."""
    parser = argparse.ArgumentParser(description='Security audit for Celebrant Portal')
    parser.add_argument('--target', required=True,
                       help='Target URL for security audit')
    parser.add_argument('--auth-token', help='Authentication token')
    parser.add_argument('--output', help='Output file for report')
    parser.add_argument('--environment', choices=['staging', 'production'],
                       default='staging', help='Environment being audited')
    
    args = parser.parse_args()
    
    logger.info(f"Starting security audit for {args.target}")
    
    auditor = SecurityAuditor(args.target, args.auth_token)
    checks = auditor.run_full_audit()
    report = auditor.generate_report(checks)
    
    # Print summary
    print("\n" + "="*60)
    print("SECURITY AUDIT REPORT")
    print("="*60)
    print(f"Target: {args.target}")
    print(f"Environment: {args.environment}")
    print(f"Timestamp: {report['timestamp']}")
    print(f"Risk Level: {report['summary']['risk_level']}")
    print(f"Success Rate: {report['summary']['success_rate']:.1f}%")
    print(f"Passed: {report['summary']['passed']}, Failed: {report['summary']['failed']}, Warnings: {report['summary']['warnings']}")
    
    print("\n" + "-"*60)
    print("DETAILED RESULTS")
    print("-"*60)
    
    for check in checks:
        status_icon = "✅" if check.status == "PASS" else "❌" if check.status == "FAIL" else "⚠️"
        print(f"{status_icon} {check.name}: {check.status}")
        print(f"   {check.description}")
        if check.recommendation:
            print(f"   Recommendation: {check.recommendation}")
        print()
    
    # Save report if output file specified
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"Report saved to {args.output}")
    
    # Exit with appropriate code
    if report['summary']['failed'] > 0:
        logger.error("Security audit failed - critical issues found")
        exit(1)
    elif report['summary']['warnings'] > 0:
        logger.warning("Security audit completed with warnings")
        exit(0)
    else:
        logger.info("Security audit passed")
        exit(0)

if __name__ == "__main__":
    main()
