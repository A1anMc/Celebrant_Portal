// test_full_integration.js - Comprehensive Frontend-Backend Integration Test
const axios = require('axios');

const API_BASE = 'http://localhost:8000';
const FRONTEND_BASE = 'http://localhost:3001';

async function testBackendHealth() {
    console.log('🔍 Testing Backend Health...');
    try {
        const response = await axios.get(`${API_BASE}/health`);
        console.log('✅ Backend Health:', response.data);
        return true;
    } catch (error) {
        console.error('❌ Backend Health Failed:', error.message);
        return false;
    }
}

async function testAuthentication() {
    console.log('🔍 Testing Authentication...');
    try {
        // Test login
        const loginResponse = await axios.post(`${API_BASE}/api/auth/login`, {
            email: 'admin@melbournecelebrant.com',
            password: 'admin123'
        });
        
        console.log('✅ Login successful');
        const token = loginResponse.data.access_token;
        
        // Test user info
        const userResponse = await axios.get(`${API_BASE}/api/auth/me`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        console.log('✅ User info retrieved:', userResponse.data.email);
        return token;
    } catch (error) {
        console.error('❌ Authentication Failed:', error.response?.data || error.message);
        return null;
    }
}

async function testDashboardAPI(token) {
    console.log('🔍 Testing Dashboard API...');
    try {
        const response = await axios.get(`${API_BASE}/api/dashboard/metrics`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        console.log('✅ Dashboard metrics:', response.data);
        return true;
    } catch (error) {
        console.error('❌ Dashboard API Failed:', error.response?.data || error.message);
        return false;
    }
}

async function testCouplesAPI(token) {
    console.log('🔍 Testing Couples API...');
    try {
        const response = await axios.get(`${API_BASE}/api/couples`, {
            headers: { Authorization: `Bearer ${token}` }
        });
        
        console.log('✅ Couples API:', response.data);
        return true;
    } catch (error) {
        console.error('❌ Couples API Failed:', error.response?.data || error.message);
        return false;
    }
}

async function testFrontendAccessibility() {
    console.log('🔍 Testing Frontend Accessibility...');
    try {
        // Test main page
        const mainResponse = await axios.get(FRONTEND_BASE);
        console.log('✅ Frontend main page accessible');
        
        // Test login page
        const loginResponse = await axios.get(`${FRONTEND_BASE}/login`);
        console.log('✅ Frontend login page accessible');
        
        return true;
    } catch (error) {
        console.error('❌ Frontend Accessibility Failed:', error.message);
        return false;
    }
}

async function testCORSHeaders() {
    console.log('🔍 Testing CORS Configuration...');
    try {
        const response = await axios.options(`${API_BASE}/api/auth/login`, {
            headers: {
                'Origin': FRONTEND_BASE,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'Content-Type'
            }
        });
        
        console.log('✅ CORS headers configured correctly');
        return true;
    } catch (error) {
        console.error('❌ CORS Test Failed:', error.message);
        return false;
    }
}

async function runAllTests() {
    console.log('🚀 Starting Comprehensive Integration Tests...\n');
    
    const results = {
        backendHealth: await testBackendHealth(),
        frontendAccessibility: await testFrontendAccessibility(),
        corsConfiguration: await testCORSHeaders(),
    };
    
    const token = await testAuthentication();
    if (token) {
        results.authentication = true;
        results.dashboardAPI = await testDashboardAPI(token);
        results.couplesAPI = await testCouplesAPI(token);
    } else {
        results.authentication = false;
        results.dashboardAPI = false;
        results.couplesAPI = false;
    }
    
    console.log('\n📊 Test Results Summary:');
    console.log('========================');
    Object.entries(results).forEach(([test, passed]) => {
        console.log(`${passed ? '✅' : '❌'} ${test}: ${passed ? 'PASSED' : 'FAILED'}`);
    });
    
    const allPassed = Object.values(results).every(result => result === true);
    console.log(`\n🎯 Overall Status: ${allPassed ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);
    
    if (allPassed) {
        console.log('\n🚀 Application is ready for deployment!');
    } else {
        console.log('\n⚠️  Fix failing tests before deployment.');
    }
    
    return allPassed;
}

// Run if called directly
if (require.main === module) {
    runAllTests().then(success => {
        process.exit(success ? 0 : 1);
    });
}

module.exports = { runAllTests }; 