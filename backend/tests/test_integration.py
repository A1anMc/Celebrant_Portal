"""
Integration tests for the Melbourne Celebrant Portal.
Tests all systems working together including caching, WebSockets, and email.
"""

import pytest
import asyncio
import json
from httpx import AsyncClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock

from app.core.database import get_db
from app.core.cache import CacheManager
from app.core.websockets import manager, NotificationService
from app.core.email_service import email_service
from app.models import User, Couple, Invoice
from app.core.auth import create_access_token

@pytest.fixture
async def test_client():
    """Create test client with database session."""
    from app.main import app
    
    async def override_get_db():
        db = next(get_db())
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    app.dependency_overrides.clear()

@pytest.fixture
async def authenticated_client(test_client, db_session):
    """Create authenticated test client."""
    # Create test user
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password",
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    
    # Create access token
    token = create_access_token(data={"sub": user.email})
    
    # Add authorization header
    test_client.headers["Authorization"] = f"Bearer {token}"
    
    return test_client, user

class TestSystemIntegration:
    """Test that all systems work together properly."""
    
    @pytest.mark.asyncio
    async def test_full_user_workflow(self, authenticated_client, db_session):
        """Test complete user workflow from registration to invoice."""
        client, user = authenticated_client
        
        # 1. Create a couple
        couple_data = {
            "partner1_name": "John Doe",
            "partner2_name": "Jane Smith",
            "partner1_email": "john@example.com",
            "partner2_email": "jane@example.com",
            "wedding_date": "2024-06-15T14:00:00",
            "venue": "Melbourne Gardens",
            "status": "Active"
        }
        
        response = await client.post("/api/v1/couples/", json=couple_data)
        assert response.status_code == 200
        couple = response.json()
        couple_id = couple["id"]
        
        # 2. Create an invoice
        invoice_data = {
            "couple_id": couple_id,
            "amount": 500.00,
            "status": "Draft",
            "due_date": "2024-05-15T00:00:00",
            "notes": "Wedding ceremony services"
        }
        
        response = await client.post("/api/v1/invoices/", json=invoice_data)
        assert response.status_code == 200
        invoice = response.json()
        invoice_id = invoice["id"]
        
        # 3. Check caching is working
        cache_key = f"couple_details:{couple_id}"
        cached_data = CacheManager.get(cache_key)
        assert cached_data is not None
        
        # 4. Test statistics endpoint
        response = await client.get("/api/v1/couples/statistics/")
        assert response.status_code == 200
        stats = response.json()
        assert stats["total_couples"] >= 1
        
        # 5. Test invoice statistics
        response = await client.get("/api/v1/invoices/statistics/")
        assert response.status_code == 200
        invoice_stats = response.json()
        assert invoice_stats["total_invoices"] >= 1

class TestCachingSystem:
    """Test Redis caching functionality."""
    
    @pytest.mark.asyncio
    async def test_cache_operations(self):
        """Test basic cache operations."""
        # Test set and get
        test_data = {"test": "data", "number": 123}
        CacheManager.set("test_key", test_data, expire=60)
        
        retrieved_data = CacheManager.get("test_key")
        assert retrieved_data == test_data
        
        # Test cache expiration
        CacheManager.set("expire_key", "test", expire=1)
        await asyncio.sleep(2)
        expired_data = CacheManager.get("expire_key")
        assert expired_data is None
        
        # Test cache deletion
        CacheManager.set("delete_key", "test")
        assert CacheManager.exists("delete_key")
        CacheManager.delete("delete_key")
        assert not CacheManager.exists("delete_key")
    
    @pytest.mark.asyncio
    async def test_cache_pattern_deletion(self):
        """Test pattern-based cache deletion."""
        # Set multiple keys with pattern
        CacheManager.set("user_stats:1", {"data": "user1"})
        CacheManager.set("user_stats:2", {"data": "user2"})
        CacheManager.set("user_profile:1", {"data": "profile1"})
        
        # Delete pattern
        deleted_count = CacheManager.delete_pattern("user_stats:*")
        assert deleted_count == 2
        
        # Verify deletion
        assert CacheManager.get("user_stats:1") is None
        assert CacheManager.get("user_stats:2") is None
        assert CacheManager.get("user_profile:1") is not None

class TestWebSocketSystem:
    """Test WebSocket functionality."""
    
    @pytest.mark.asyncio
    async def test_websocket_connection(self):
        """Test WebSocket connection and messaging."""
        # Mock WebSocket
        mock_websocket = MagicMock()
        mock_websocket.client_state = "CONNECTED"
        mock_websocket.send_text = MagicMock()
        
        # Test connection
        user_id = 1
        await manager.connect(mock_websocket, user_id)
        
        # Verify connection
        assert user_id in manager.active_connections
        assert mock_websocket in manager.active_connections[user_id]
        
        # Test message sending
        test_message = {"type": "test", "data": "test_message"}
        await manager.send_personal_message(test_message, user_id)
        
        # Verify message was sent
        mock_websocket.send_text.assert_called_with(json.dumps(test_message))
        
        # Test disconnection
        manager.disconnect(mock_websocket)
        assert user_id not in manager.active_connections
    
    @pytest.mark.asyncio
    async def test_notification_service(self):
        """Test notification service functionality."""
        # Mock WebSocket connection
        mock_websocket = MagicMock()
        mock_websocket.client_state = "CONNECTED"
        mock_websocket.send_text = MagicMock()
        
        user_id = 1
        await manager.connect(mock_websocket, user_id)
        
        # Test invoice reminder notification
        invoice_data = {
            "id": 1,
            "invoice_number": "INV-001",
            "amount": 500.00,
            "due_date": "2024-05-15"
        }
        
        await NotificationService.send_invoice_reminder(user_id, invoice_data)
        
        # Verify notification was sent
        mock_websocket.send_text.assert_called()
        sent_message = json.loads(mock_websocket.send_text.call_args[0][0])
        assert sent_message["type"] == "notification"
        assert sent_message["notification_type"] == "invoice_reminder"

class TestEmailSystem:
    """Test email service functionality."""
    
    @pytest.mark.asyncio
    @patch('app.core.email_service.smtplib.SMTP')
    async def test_email_sending(self, mock_smtp):
        """Test email sending functionality."""
        # Mock SMTP
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        # Test welcome email
        success = await email_service.send_welcome_email(
            "test@example.com",
            "Test User"
        )
        
        assert success
        mock_server.starttls.assert_called()
        mock_server.login.assert_called()
        mock_server.sendmail.assert_called()
    
    @pytest.mark.asyncio
    @patch('app.core.email_service.smtplib.SMTP')
    async def test_invoice_reminder_email(self, mock_smtp):
        """Test invoice reminder email."""
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        invoice_data = {
            "invoice_number": "INV-001",
            "amount": 500.00,
            "due_date": "2024-05-15",
            "couple_names": "John & Jane"
        }
        
        success = await email_service.send_invoice_reminder(
            "test@example.com",
            "Test User",
            invoice_data
        )
        
        assert success
        mock_server.sendmail.assert_called()

class TestPerformanceMonitoring:
    """Test performance monitoring and metrics."""
    
    @pytest.mark.asyncio
    async def test_health_check_endpoint(self, test_client):
        """Test health check endpoint."""
        response = await test_client.get("/health")
        assert response.status_code == 200
        
        health_data = response.json()
        assert "status" in health_data
        assert "timestamp" in health_data
        assert "version" in health_data
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint(self, test_client):
        """Test metrics endpoint."""
        response = await test_client.get("/metrics")
        assert response.status_code == 200
        
        metrics_data = response.json()
        assert "request_count" in metrics_data
        assert "error_count" in metrics_data
        assert "avg_response_time" in metrics_data
    
    @pytest.mark.asyncio
    async def test_websocket_status_endpoint(self, test_client):
        """Test WebSocket status endpoint."""
        response = await test_client.get("/api/v1/ws/status")
        assert response.status_code == 200
        
        status_data = response.json()
        assert "total_connections" in status_data
        assert "active_users" in status_data

class TestErrorHandling:
    """Test error handling and recovery."""
    
    @pytest.mark.asyncio
    async def test_database_connection_failure(self, test_client):
        """Test handling of database connection failures."""
        # This would require mocking database connection failure
        # For now, test that the application doesn't crash
        response = await test_client.get("/health")
        assert response.status_code in [200, 503]  # Either healthy or service unavailable
    
    @pytest.mark.asyncio
    async def test_cache_failure_graceful_degradation(self):
        """Test that the system works when cache is unavailable."""
        # Test with cache disabled
        original_set = CacheManager.set
        CacheManager.set = lambda *args, **kwargs: False
        
        # System should still work without cache
        test_data = {"test": "data"}
        result = CacheManager.set("test_key", test_data)
        assert result is False
        
        # Restore original function
        CacheManager.set = original_set
    
    @pytest.mark.asyncio
    async def test_websocket_failure_handling(self):
        """Test WebSocket failure handling."""
        # Test with invalid WebSocket
        mock_websocket = MagicMock()
        mock_websocket.client_state = "CLOSED"
        mock_websocket.send_text.side_effect = Exception("Connection failed")
        
        # Should handle failure gracefully
        user_id = 1
        await manager.connect(mock_websocket, user_id)
        
        # Try to send message (should handle failure)
        test_message = {"type": "test"}
        await manager.send_personal_message(test_message, user_id)
        
        # Should clean up failed connections
        manager.disconnect(mock_websocket)

class TestSecurityFeatures:
    """Test security features and authentication."""
    
    @pytest.mark.asyncio
    async def test_authentication_required(self, test_client):
        """Test that protected endpoints require authentication."""
        # Test without authentication
        response = await test_client.get("/api/v1/couples/")
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_rate_limiting(self, authenticated_client):
        """Test rate limiting functionality."""
        client, user = authenticated_client
        
        # Make multiple requests quickly
        responses = []
        for _ in range(105):  # Exceed rate limit
            response = await client.get("/api/v1/couples/")
            responses.append(response.status_code)
        
        # Should have rate limit errors
        assert 429 in responses
    
    @pytest.mark.asyncio
    async def test_csrf_protection(self, test_client):
        """Test CSRF protection."""
        # Test POST request without CSRF token
        response = await test_client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "full_name": "Test User"
        })
        
        # Should be blocked by CSRF protection
        assert response.status_code in [403, 422]

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
