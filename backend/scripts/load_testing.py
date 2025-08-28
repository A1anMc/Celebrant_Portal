#!/usr/bin/env python3
"""
Load Testing Script for Melbourne Celebrant Portal
Tests application performance under various load conditions.
"""

import asyncio
import aiohttp
import time
import json
import argparse
from typing import List, Dict, Any
from dataclasses import dataclass
from statistics import mean, median, stdev
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure."""
    endpoint: str
    method: str
    status_code: int
    response_time: float
    timestamp: float
    success: bool
    error_message: str = ""

class LoadTester:
    """Load testing utility for the Celebrant Portal."""
    
    def __init__(self, base_url: str, auth_token: str = None):
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.results: List[TestResult] = []
        self.session = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'Authorization': f'Bearer {self.auth_token}' if self.auth_token else '',
                'Content-Type': 'application/json'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def make_request(self, endpoint: str, method: str = 'GET', 
                          data: Dict = None) -> TestResult:
        """Make a single HTTP request and record results."""
        url = f"{self.base_url}{endpoint}"
        start_time = time.time()
        
        try:
            if method.upper() == 'GET':
                async with self.session.get(url) as response:
                    response_time = time.time() - start_time
                    return TestResult(
                        endpoint=endpoint,
                        method=method,
                        status_code=response.status,
                        response_time=response_time,
                        timestamp=start_time,
                        success=response.status < 400
                    )
            elif method.upper() == 'POST':
                async with self.session.post(url, json=data) as response:
                    response_time = time.time() - start_time
                    return TestResult(
                        endpoint=endpoint,
                        method=method,
                        status_code=response.status,
                        response_time=response_time,
                        timestamp=start_time,
                        success=response.status < 400
                    )
        except Exception as e:
            response_time = time.time() - start_time
            return TestResult(
                endpoint=endpoint,
                method=method,
                status_code=0,
                response_time=response_time,
                timestamp=start_time,
                success=False,
                error_message=str(e)
            )
    
    async def run_concurrent_requests(self, endpoint: str, method: str = 'GET',
                                    data: Dict = None, concurrency: int = 10,
                                    total_requests: int = 100) -> List[TestResult]:
        """Run concurrent requests to test load handling."""
        logger.info(f"Running {total_requests} requests with {concurrency} concurrency")
        
        semaphore = asyncio.Semaphore(concurrency)
        
        async def make_request_with_semaphore():
            async with semaphore:
                return await self.make_request(endpoint, method, data)
        
        tasks = [make_request_with_semaphore() for _ in range(total_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and collect valid results
        valid_results = []
        for result in results:
            if isinstance(result, TestResult):
                valid_results.append(result)
            else:
                logger.error(f"Request failed with exception: {result}")
        
        return valid_results
    
    def analyze_results(self, results: List[TestResult]) -> Dict[str, Any]:
        """Analyze test results and generate statistics."""
        if not results:
            return {"error": "No results to analyze"}
        
        response_times = [r.response_time for r in results]
        success_count = sum(1 for r in results if r.success)
        error_count = len(results) - success_count
        
        status_codes = {}
        for result in results:
            status_codes[result.status_code] = status_codes.get(result.status_code, 0) + 1
        
        return {
            "total_requests": len(results),
            "successful_requests": success_count,
            "failed_requests": error_count,
            "success_rate": (success_count / len(results)) * 100,
            "response_time_stats": {
                "mean": mean(response_times),
                "median": median(response_times),
                "min": min(response_times),
                "max": max(response_times),
                "std_dev": stdev(response_times) if len(response_times) > 1 else 0
            },
            "status_codes": status_codes,
            "endpoints_tested": list(set(r.endpoint for r in results))
        }
    
    async def run_health_check(self) -> bool:
        """Run a basic health check."""
        logger.info("Running health check...")
        result = await self.make_request('/health')
        
        if result.success and result.status_code == 200:
            logger.info("✅ Health check passed")
            return True
        else:
            logger.error(f"❌ Health check failed: {result.status_code}")
            return False
    
    async def run_basic_load_test(self) -> Dict[str, Any]:
        """Run a basic load test on common endpoints."""
        endpoints = [
            ('/health', 'GET'),
            ('/api/v1/auth/login', 'POST', {'email': 'test@example.com', 'password': 'testpass'}),
            ('/api/v1/couples/', 'GET'),
            ('/metrics', 'GET')
        ]
        
        all_results = []
        
        for endpoint_info in endpoints:
            endpoint = endpoint_info[0]
            method = endpoint_info[1]
            data = endpoint_info[2] if len(endpoint_info) > 2 else None
            
            logger.info(f"Testing endpoint: {method} {endpoint}")
            results = await self.run_concurrent_requests(
                endpoint, method, data, concurrency=5, total_requests=20
            )
            all_results.extend(results)
        
        return self.analyze_results(all_results)

async def main():
    """Main function to run load tests."""
    parser = argparse.ArgumentParser(description='Load testing for Celebrant Portal')
    parser.add_argument('--target', default='http://localhost:8000',
                       help='Target URL for testing')
    parser.add_argument('--auth-token', help='Authentication token')
    parser.add_argument('--concurrency', type=int, default=10,
                       help='Number of concurrent requests')
    parser.add_argument('--total-requests', type=int, default=100,
                       help='Total number of requests')
    parser.add_argument('--endpoint', default='/health',
                       help='Endpoint to test')
    parser.add_argument('--method', default='GET',
                       help='HTTP method to use')
    parser.add_argument('--output', help='Output file for results')
    
    args = parser.parse_args()
    
    logger.info(f"Starting load test against: {args.target}")
    
    async with LoadTester(args.target, args.auth_token) as tester:
        # Run health check first
        if not await tester.run_health_check():
            logger.error("Health check failed, aborting load test")
            return
        
        # Run load test
        results = await tester.run_concurrent_requests(
            args.endpoint, args.method, 
            concurrency=args.concurrency,
            total_requests=args.total_requests
        )
        
        # Analyze results
        analysis = tester.analyze_results(results)
        
        # Print results
        print("\n" + "="*50)
        print("LOAD TEST RESULTS")
        print("="*50)
        print(f"Target: {args.target}")
        print(f"Endpoint: {args.method} {args.endpoint}")
        print(f"Concurrency: {args.concurrency}")
        print(f"Total Requests: {args.total_requests}")
        print(f"Success Rate: {analysis['success_rate']:.2f}%")
        print(f"Mean Response Time: {analysis['response_time_stats']['mean']:.3f}s")
        print(f"Median Response Time: {analysis['response_time_stats']['median']:.3f}s")
        print(f"Max Response Time: {analysis['response_time_stats']['max']:.3f}s")
        print(f"Status Codes: {analysis['status_codes']}")
        
        # Save results if output file specified
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(analysis, f, indent=2)
            logger.info(f"Results saved to {args.output}")

if __name__ == "__main__":
    asyncio.run(main())
