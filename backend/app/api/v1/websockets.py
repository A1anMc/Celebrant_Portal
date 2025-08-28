"""
WebSocket API endpoints for real-time features.
Provides WebSocket connections for notifications and live updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from ...core.database import get_db
from ...core.websockets import websocket_endpoint, manager
from ...core.monitoring import logger

router = APIRouter(prefix="/ws", tags=["websockets"])

@router.websocket("/connect")
async def websocket_connection(
    websocket: WebSocket,
    token: str = Query(..., description="Authentication token"),
    db: Session = Depends(get_db)
):
    """WebSocket connection endpoint for real-time features."""
    await websocket_endpoint(websocket, token, db)

@router.get("/status")
async def websocket_status():
    """Get WebSocket connection status and statistics."""
    return {
        "total_connections": manager.get_connection_count(),
        "active_users": len(manager.active_connections),
        "connection_details": {
            user_id: {
                "connection_count": len(connections),
                "connected_at": [
                    manager.connection_data.get(conn, {}).get("connected_at", 0)
                    for conn in connections
                ]
            }
            for user_id, connections in manager.active_connections.items()
        }
    }

@router.post("/broadcast")
async def broadcast_message(message: dict, user_ids: Optional[list] = None):
    """Broadcast a message to connected users (admin only)."""
    try:
        if user_ids:
            await manager.broadcast_to_multiple_users(message, user_ids)
            logger.info("Message broadcasted to specific users", user_ids=user_ids)
        else:
            await manager.broadcast_to_all(message)
            logger.info("Message broadcasted to all users")
        
        return {"status": "success", "message": "Broadcast sent successfully"}
    
    except Exception as e:
        logger.error("Broadcast failed", error=str(e))
        return {"status": "error", "message": f"Broadcast failed: {str(e)}"}

@router.get("/user/{user_id}/connections")
async def get_user_connections(user_id: int):
    """Get connection information for a specific user."""
    connection_count = manager.get_user_connection_count(user_id)
    connections = manager.active_connections.get(user_id, [])
    
    connection_details = []
    for conn in connections:
        conn_data = manager.connection_data.get(conn, {})
        connection_details.append({
            "connected_at": conn_data.get("connected_at"),
            "subscriptions": conn_data.get("subscriptions", [])
        })
    
    return {
        "user_id": user_id,
        "connection_count": connection_count,
        "connections": connection_details
    }
