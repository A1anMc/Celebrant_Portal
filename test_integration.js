// test_integration.js - Comprehensive Frontend-Backend Integration Test
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

async function runAllTests() {
    console.log('🚀 Starting Comprehensive Integration Tests...\n');
    
    const results = {
        backendHealth: await testBackendHealth(),
    };
    
    const token = await testAuthentication();
    if (token) {
        results.authentication = true;
        results.dashboardAPI = await testDashboardAPI(token);
    } else {
        results.authentication = false;
        results.dashboardAPI = false;
    }
    
    console.log('\n📊 Test Results Summary:');
    console.log('========================');
    Object.entries(results).forEach(([test, passed]) => {
        console.log(`${passed ? '✅' : '❌'} ${test}: ${passed ? 'PASSED' : 'FAILED'}`);
    });
    
    const allPassed = Object.values(results).every(result => result === true);
    console.log(`\n🎯 Overall Status: ${allPassed ? '✅ ALL TESTS PASSED' : '❌ SOME TESTS FAILED'}`);
    
    return allPassed;
}

runAllTests().then(success => {
    process.exit(success ? 0 : 1);
}); 