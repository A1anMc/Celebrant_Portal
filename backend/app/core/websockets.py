"""
WebSocket support for real-time features.
Provides real-time notifications, live updates, and chat functionality.
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect, Depends
from fastapi.websockets import WebSocketState
from sqlalchemy.orm import Session
import structlog

from .database import get_db
from .auth import get_current_user_ws
from .monitoring import logger

class ConnectionManager:
    """Manages WebSocket connections and broadcasts."""
    
    def __init__(self):
        self.active_connections: Dict[int, List[WebSocket]] = {}
        self.connection_data: Dict[WebSocket, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int):
        """Connect a new WebSocket client."""
        await websocket.accept()
        
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        
        self.active_connections[user_id].append(websocket)
        self.connection_data[websocket] = {"user_id": user_id, "connected_at": asyncio.get_event_loop().time()}
        
        logger.info("WebSocket connected", user_id=user_id, total_connections=len(self.active_connections[user_id]))
    
    def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket client."""
        user_id = self.connection_data.get(websocket, {}).get("user_id")
        
        if user_id and user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            
            # Remove user if no more connections
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        
        if websocket in self.connection_data:
            del self.connection_data[websocket]
        
        logger.info("WebSocket disconnected", user_id=user_id)
    
    async def send_personal_message(self, message: dict, user_id: int):
        """Send a message to a specific user."""
        if user_id in self.active_connections:
            disconnected = []
            
            for connection in self.active_connections[user_id]:
                try:
                    if connection.client_state == WebSocketState.CONNECTED:
                        await connection.send_text(json.dumps(message))
                    else:
                        disconnected.append(connection)
                except Exception as e:
                    logger.error("Failed to send personal message", user_id=user_id, error=str(e))
                    disconnected.append(connection)
            
            # Clean up disconnected connections
            for connection in disconnected:
                self.disconnect(connection)
    
    async def broadcast_to_user(self, message: dict, user_id: int):
        """Broadcast a message to all connections of a specific user."""
        await self.send_personal_message(message, user_id)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast a message to all connected users."""
        all_users = list(self.active_connections.keys())
        for user_id in all_users:
            await self.send_personal_message(message, user_id)
    
    async def broadcast_to_multiple_users(self, message: dict, user_ids: List[int]):
        """Broadcast a message to multiple specific users."""
        for user_id in user_ids:
            await self.send_personal_message(message, user_id)
    
    def get_connection_count(self) -> int:
        """Get total number of active connections."""
        return sum(len(connections) for connections in self.active_connections.values())
    
    def get_user_connection_count(self, user_id: int) -> int:
        """Get number of connections for a specific user."""
        return len(self.active_connections.get(user_id, []))

# Global connection manager
manager = ConnectionManager()

class NotificationService:
    """Service for sending real-time notifications."""
    
    @staticmethod
    async def send_notification(user_id: int, notification_type: str, data: dict):
        """Send a notification to a specific user."""
        message = {
            "type": "notification",
            "notification_type": notification_type,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await manager.send_personal_message(message, user_id)
    
    @staticmethod
    async def send_invoice_reminder(user_id: int, invoice_data: dict):
        """Send invoice reminder notification."""
        await NotificationService.send_notification(
            user_id,
            "invoice_reminder",
            {
                "invoice_id": invoice_data.get("id"),
                "invoice_number": invoice_data.get("invoice_number"),
                "amount": str(invoice_data.get("amount")),
                "due_date": invoice_data.get("due_date"),
                "message": f"Invoice {invoice_data.get('invoice_number')} is due soon"
            }
        )
    
    @staticmethod
    async def send_ceremony_reminder(user_id: int, ceremony_data: dict):
        """Send ceremony reminder notification."""
        await NotificationService.send_notification(
            user_id,
            "ceremony_reminder",
            {
                "ceremony_id": ceremony_data.get("id"),
                "title": ceremony_data.get("title"),
                "ceremony_date": ceremony_data.get("ceremony_date"),
                "couple_names": ceremony_data.get("couple_names"),
                "message": f"Ceremony '{ceremony_data.get('title')}' is tomorrow"
            }
        )
    
    @staticmethod
    async def send_new_couple_notification(user_id: int, couple_data: dict):
        """Send new couple notification."""
        await NotificationService.send_notification(
            user_id,
            "new_couple",
            {
                "couple_id": couple_data.get("id"),
                "partner1_name": couple_data.get("partner1_name"),
                "partner2_name": couple_data.get("partner2_name"),
                "wedding_date": couple_data.get("wedding_date"),
                "message": f"New couple: {couple_data.get('partner1_name')} & {couple_data.get('partner2_name')}"
            }
        )
    
    @staticmethod
    async def send_payment_received(user_id: int, payment_data: dict):
        """Send payment received notification."""
        await NotificationService.send_notification(
            user_id,
            "payment_received",
            {
                "invoice_id": payment_data.get("invoice_id"),
                "invoice_number": payment_data.get("invoice_number"),
                "amount": str(payment_data.get("amount")),
                "message": f"Payment received for invoice {payment_data.get('invoice_number')}"
            }
        )

class LiveUpdateService:
    """Service for sending live updates."""
    
    @staticmethod
    async def send_dashboard_update(user_id: int, dashboard_data: dict):
        """Send dashboard live update."""
        message = {
            "type": "dashboard_update",
            "data": dashboard_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await manager.send_personal_message(message, user_id)
    
    @staticmethod
    async def send_couple_update(user_id: int, couple_id: int, update_data: dict):
        """Send couple data update."""
        message = {
            "type": "couple_update",
            "couple_id": couple_id,
            "data": update_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await manager.send_personal_message(message, user_id)
    
    @staticmethod
    async def send_invoice_update(user_id: int, invoice_id: int, update_data: dict):
        """Send invoice data update."""
        message = {
            "type": "invoice_update",
            "invoice_id": invoice_id,
            "data": update_data,
            "timestamp": asyncio.get_event_loop().time()
        }
        await manager.send_personal_message(message, user_id)

# WebSocket endpoint handlers
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    """Main WebSocket endpoint for real-time communication."""
    try:
        # Authenticate user
        user = await get_current_user_ws(token, db)
        if not user:
            await websocket.close(code=4001, reason="Authentication failed")
            return
        
        # Connect to manager
        await manager.connect(websocket, user.id)
        
        # Send welcome message
        welcome_message = {
            "type": "connection_established",
            "user_id": user.id,
            "message": "Connected to Melbourne Celebrant Portal",
            "timestamp": asyncio.get_event_loop().time()
        }
        await websocket.send_text(json.dumps(welcome_message))
        
        # Handle incoming messages
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle different message types
                await handle_websocket_message(websocket, user.id, message, db)
                
        except WebSocketDisconnect:
            manager.disconnect(websocket)
        except Exception as e:
            logger.error("WebSocket error", user_id=user.id, error=str(e))
            manager.disconnect(websocket)
    
    except Exception as e:
        logger.error("WebSocket connection error", error=str(e))
        if websocket.client_state == WebSocketState.CONNECTED:
            await websocket.close(code=4000, reason="Internal server error")

async def handle_websocket_message(websocket: WebSocket, user_id: int, message: dict, db: Session):
    """Handle incoming WebSocket messages."""
    message_type = message.get("type")
    
    if message_type == "ping":
        # Respond to ping
        response = {
            "type": "pong",
            "timestamp": asyncio.get_event_loop().time()
        }
        await websocket.send_text(json.dumps(response))
    
    elif message_type == "subscribe":
        # Handle subscription to specific updates
        subscription_type = message.get("subscription_type")
        subscription_id = message.get("subscription_id")
        
        # Store subscription in connection data
        if websocket in manager.connection_data:
            if "subscriptions" not in manager.connection_data[websocket]:
                manager.connection_data[websocket]["subscriptions"] = []
            
            subscription = {
                "type": subscription_type,
                "id": subscription_id
            }
            manager.connection_data[websocket]["subscriptions"].append(subscription)
        
        # Confirm subscription
        response = {
            "type": "subscription_confirmed",
            "subscription_type": subscription_type,
            "subscription_id": subscription_id
        }
        await websocket.send_text(json.dumps(response))
    
    elif message_type == "unsubscribe":
        # Handle unsubscription
        subscription_type = message.get("subscription_type")
        subscription_id = message.get("subscription_id")
        
        if websocket in manager.connection_data and "subscriptions" in manager.connection_data[websocket]:
            subscriptions = manager.connection_data[websocket]["subscriptions"]
            manager.connection_data[websocket]["subscriptions"] = [
                s for s in subscriptions 
                if not (s["type"] == subscription_type and s["id"] == subscription_id)
            ]
        
        # Confirm unsubscription
        response = {
            "type": "unsubscription_confirmed",
            "subscription_type": subscription_type,
            "subscription_id": subscription_id
        }
        await websocket.send_text(json.dumps(response))
    
    else:
        # Unknown message type
        response = {
            "type": "error",
            "message": f"Unknown message type: {message_type}",
            "timestamp": asyncio.get_event_loop().time()
        }
        await websocket.send_text(json.dumps(response))
