"""
PyX WebSocket Rooms & Presence
Real-time collaboration features with Zen Mode access.
"""
import asyncio
import json
from typing import Dict, Set, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field
from weakref import WeakSet


@dataclass
class Client:
    """Represents a connected WebSocket client"""
    id: str
    websocket: Any
    user_id: Optional[str] = None
    user_data: Dict = field(default_factory=dict)
    rooms: Set[str] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.now)
    
    async def send(self, data: dict):
        """Send message to this client"""
        try:
            await self.websocket.send_text(json.dumps(data))
        except Exception as e:
            print(f"[WS] Error sending to {self.id}: {e}")
    
    async def send_text(self, text: str):
        """Send raw text to this client"""
        try:
            await self.websocket.send_text(text)
        except Exception as e:
            print(f"[WS] Error sending to {self.id}: {e}")


class Room:
    """Represents a WebSocket room/channel"""
    
    def __init__(self, name: str):
        self.name = name
        self.clients: Dict[str, Client] = {}
        self.metadata: Dict = {}
        self.created_at = datetime.now()
    
    def join(self, client: Client):
        """Add client to room"""
        self.clients[client.id] = client
        client.rooms.add(self.name)
    
    def leave(self, client: Client):
        """Remove client from room"""
        if client.id in self.clients:
            del self.clients[client.id]
        client.rooms.discard(self.name)
    
    async def broadcast(self, data: dict, exclude: str = None):
        """Send message to all clients in room"""
        for client_id, client in self.clients.items():
            if client_id != exclude:
                await client.send(data)
    
    def get_presence(self) -> List[dict]:
        """Get list of connected users in room"""
        return [
            {
                "client_id": c.id,
                "user_id": c.user_id,
                "user_data": c.user_data,
                "connected_at": c.connected_at.isoformat()
            }
            for c in self.clients.values()
        ]
    
    @property
    def count(self) -> int:
        """Number of clients in room"""
        return len(self.clients)


class ZenWebSocket:
    """
    Zen Mode WebSocket - Real-time rooms and presence.
    
    Usage:
        from pyx import ws
        
        # In your event handler
        @event
        async def on_connect(client):
            ws.authenticate(client, user_id="123", user_data={"name": "John"})
        
        @event
        async def join_chat(data, client):
            room_id = data["room_id"]
            ws.join(f"chat:{room_id}", client)
            ws.broadcast(f"chat:{room_id}", {
                "type": "user_joined",
                "user": client.user_data
            })
        
        @event
        async def send_message(data, client):
            room_id = data["room_id"]
            ws.broadcast(f"chat:{room_id}", {
                "type": "message",
                "from": client.user_id,
                "text": data["text"]
            })
        
        @event
        async def leave_chat(data, client):
            room_id = data["room_id"]
            ws.leave(f"chat:{room_id}", client)
        
        # Get who's online
        users = ws.presence(f"chat:{room_id}")
    """
    
    def __init__(self):
        self._clients: Dict[str, Client] = {}
        self._rooms: Dict[str, Room] = {}
        self._handlers: Dict[str, List[Callable]] = {}
        self._client_counter = 0
    
    # ====================
    # Client Management
    # ====================
    
    def connect(self, websocket, user_id: str = None, user_data: dict = None) -> Client:
        """
        Register a new WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket instance
            user_id: Optional user identifier
            user_data: Optional user metadata
            
        Returns:
            Client instance
        """
        import secrets
        client_id = f"client_{secrets.token_hex(8)}"
        
        client = Client(
            id=client_id,
            websocket=websocket,
            user_id=user_id,
            user_data=user_data or {}
        )
        
        self._clients[client_id] = client
        
        # Trigger connect handlers
        self._trigger("connect", client)
        
        return client
    
    def disconnect(self, client: Client):
        """
        Handle client disconnection.
        Removes from all rooms and cleans up.
        """
        # Leave all rooms
        for room_name in list(client.rooms):
            self.leave(room_name, client)
        
        # Remove from clients
        if client.id in self._clients:
            del self._clients[client.id]
        
        # Trigger disconnect handlers
        self._trigger("disconnect", client)
    
    def authenticate(self, client: Client, user_id: str, user_data: dict = None):
        """
        Associate user identity with client.
        
        Args:
            client: Client instance
            user_id: User identifier
            user_data: Optional user metadata (name, avatar, etc.)
        """
        client.user_id = user_id
        if user_data:
            client.user_data.update(user_data)
    
    def get_client(self, client_id: str) -> Optional[Client]:
        """Get client by ID"""
        return self._clients.get(client_id)
    
    def get_client_by_user(self, user_id: str) -> List[Client]:
        """Get all clients for a user (user may have multiple connections)"""
        return [c for c in self._clients.values() if c.user_id == user_id]
    
    # ====================
    # Room Management  
    # ====================
    
    def join(self, room_name: str, client: Client) -> Room:
        """
        Join a room/channel.
        
        Args:
            room_name: Room identifier (e.g., "chat:room-123")
            client: Client to add
            
        Returns:
            Room instance
        """
        # Create room if doesn't exist
        if room_name not in self._rooms:
            self._rooms[room_name] = Room(room_name)
        
        room = self._rooms[room_name]
        room.join(client)
        
        # Trigger join handlers
        self._trigger("join", client, room_name)
        
        return room
    
    def leave(self, room_name: str, client: Client):
        """
        Leave a room/channel.
        
        Args:
            room_name: Room identifier
            client: Client to remove
        """
        if room_name in self._rooms:
            room = self._rooms[room_name]
            room.leave(client)
            
            # Trigger leave handlers
            self._trigger("leave", client, room_name)
            
            # Cleanup empty rooms
            if room.count == 0:
                del self._rooms[room_name]
    
    def get_room(self, room_name: str) -> Optional[Room]:
        """Get room by name"""
        return self._rooms.get(room_name)
    
    # ====================
    # Messaging
    # ====================
    
    async def broadcast(self, room_name: str, data: dict, exclude_client: Client = None):
        """
        Broadcast message to all clients in a room.
        
        Args:
            room_name: Room to broadcast to
            data: Message data
            exclude_client: Optional client to exclude (usually sender)
        """
        room = self._rooms.get(room_name)
        if room:
            exclude_id = exclude_client.id if exclude_client else None
            await room.broadcast(data, exclude=exclude_id)
    
    async def send_to(self, client: Client, data: dict):
        """Send message to specific client"""
        await client.send(data)
    
    async def send_to_user(self, user_id: str, data: dict):
        """Send message to all connections of a user"""
        clients = self.get_client_by_user(user_id)
        for client in clients:
            await client.send(data)
    
    async def broadcast_all(self, data: dict):
        """Broadcast to all connected clients"""
        for client in self._clients.values():
            await client.send(data)
    
    # ====================
    # Presence
    # ====================
    
    def presence(self, room_name: str) -> List[dict]:
        """
        Get list of users in a room.
        
        Returns:
            List of user presence data
        """
        room = self._rooms.get(room_name)
        if room:
            return room.get_presence()
        return []
    
    def count(self, room_name: str = None) -> int:
        """
        Get number of clients.
        
        Args:
            room_name: If provided, count for specific room
            
        Returns:
            Number of connected clients
        """
        if room_name:
            room = self._rooms.get(room_name)
            return room.count if room else 0
        return len(self._clients)
    
    def rooms_for(self, client: Client) -> List[str]:
        """Get list of rooms a client is in"""
        return list(client.rooms)
    
    # ====================
    # Event Handlers
    # ====================
    
    def on(self, event: str):
        """
        Decorator to register event handlers.
        
        Events:
            - connect: Client connected
            - disconnect: Client disconnected
            - join: Client joined a room
            - leave: Client left a room
        
        Usage:
            @ws.on("connect")
            def on_connect(client):
                print(f"Client connected: {client.id}")
            
            @ws.on("join")
            def on_join(client, room_name):
                print(f"{client.id} joined {room_name}")
        """
        def decorator(func):
            if event not in self._handlers:
                self._handlers[event] = []
            self._handlers[event].append(func)
            return func
        return decorator
    
    def _trigger(self, event: str, *args):
        """Trigger event handlers"""
        handlers = self._handlers.get(event, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    asyncio.create_task(handler(*args))
                else:
                    handler(*args)
            except Exception as e:
                print(f"[WS] Error in {event} handler: {e}")
    
    # ====================
    # Room Metadata
    # ====================
    
    def set_room_data(self, room_name: str, key: str, value: Any):
        """Set metadata on a room"""
        room = self._rooms.get(room_name)
        if room:
            room.metadata[key] = value
    
    def get_room_data(self, room_name: str, key: str = None) -> Any:
        """Get metadata from a room"""
        room = self._rooms.get(room_name)
        if room:
            if key:
                return room.metadata.get(key)
            return room.metadata
        return None
    
    # ====================
    # Statistics
    # ====================
    
    def stats(self) -> dict:
        """Get WebSocket statistics"""
        return {
            "total_clients": len(self._clients),
            "total_rooms": len(self._rooms),
            "rooms": {
                name: {
                    "clients": room.count,
                    "created_at": room.created_at.isoformat()
                }
                for name, room in self._rooms.items()
            }
        }


# Zen Mode instance
ws = ZenWebSocket()


__all__ = ['ws', 'ZenWebSocket', 'Client', 'Room']
