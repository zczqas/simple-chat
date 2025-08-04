import json
from typing import Dict, List
from fastapi import WebSocket
from dataclasses import dataclass

from src.sc_chat.models.user import User


@dataclass
class Connection:
    """Represents a WebSocket connection with user information."""

    websocket: WebSocket
    user: User
    room_id: int

    def __eq__(self, other):
        """Two connections are equal if they have the same websocket."""
        if not isinstance(other, Connection):
            return False
        return self.websocket == other.websocket

    def __hash__(self):
        """Hash based on websocket identity."""
        return hash(id(self.websocket))


class ConnectionManager:
    """Manages WebSocket connections for chat rooms."""

    def __init__(self):
        self.active_connections: Dict[int, List[Connection]] = {}
        self.connection_map: Dict[WebSocket, Connection] = {}

    async def connect(self, websocket: WebSocket, user: User, room_id: int):
        """Accept a new WebSocket connection and add to room."""
        await websocket.accept()

        connection = Connection(websocket=websocket, user=user, room_id=room_id)

        # Add to room connections
        if room_id not in self.active_connections:
            self.active_connections[room_id] = []
        self.active_connections[room_id].append(connection)

        # Add to connection map for easy lookup
        self.connection_map[websocket] = connection

        print(f"User {user.username} connected to room {room_id}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.connection_map:
            connection = self.connection_map[websocket]
            room_id = connection.room_id

            # Remove from room connections
            if room_id in self.active_connections:
                try:
                    self.active_connections[room_id].remove(connection)
                except ValueError:
                    # Connection not in list, which is fine
                    pass

                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]

            # Remove from connection map
            del self.connection_map[websocket]

            print(f"User {connection.user.username} disconnected from room {room_id}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Send a message to a specific WebSocket connection."""
        try:
            # Check if websocket is still in our connection map (i.e., still connected)
            if websocket not in self.connection_map:
                return False

            await websocket.send_text(message)
            return True
        except Exception as e:
            print(f"Error sending personal message: {e}")
            self.disconnect(websocket)
            return False

    async def broadcast_to_room(
        self, message: dict, room_id: int, exclude_websocket: WebSocket | None = None
    ):
        """Broadcast a message to all connections in a room."""
        if room_id not in self.active_connections:
            return

        message_text = json.dumps(message)
        disconnected_connections = []

        # Create a copy of the list to avoid modification during iteration
        connections_copy = self.active_connections[room_id][:]

        for connection in connections_copy:
            if exclude_websocket and connection.websocket == exclude_websocket:
                continue

            if connection.websocket not in self.connection_map:
                disconnected_connections.append(connection.websocket)
                continue

            try:
                await connection.websocket.send_text(message_text)
            except Exception as e:
                print(f"Error broadcasting to {connection.user.username}: {e}")
                disconnected_connections.append(connection.websocket)

        for websocket in disconnected_connections:
            self.disconnect(websocket)

    def get_room_users(self, room_id: int) -> List[User]:
        """Get list of users currently connected to a room."""
        if room_id not in self.active_connections:
            return []

        return [conn.user for conn in self.active_connections[room_id]]

    def get_connection_count(self, room_id: int) -> int:
        """Get number of active connections in a room."""
        if room_id not in self.active_connections:
            return 0
        return len(self.active_connections[room_id])

    def is_user_in_room(self, user_id: int, room_id: int) -> bool:
        """Check if a user is currently connected to a specific room."""
        if room_id not in self.active_connections:
            return False

        return any(conn.user.id == user_id for conn in self.active_connections[room_id])


manager = ConnectionManager()
