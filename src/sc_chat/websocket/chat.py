import json

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session

from src.sc_chat.database.conn import get_db
from src.sc_chat.repository.chat_repository import ChatRepository
from src.sc_chat.websocket.connection_manager import manager
from src.sc_chat.websocket.auth import (
    authenticate_websocket,
    extract_token_from_websocket,
)

router = APIRouter(tags=["WebSocket Chat"])


def get_chat_repository(db: Session = Depends(get_db)) -> ChatRepository:
    """Dependency to get chat repository instance."""
    return ChatRepository(db)


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: int):
    token = extract_token_from_websocket(websocket)
    if not token:
        await websocket.close(code=1008, reason="Missing authentication token")
        return

    user = await authenticate_websocket(websocket, token)
    if not user:
        return

    db: Session = next(get_db())
    chat_repo = ChatRepository(db)

    try:
        room = chat_repo.get_room_by_id(room_id)
        if not room:
            await websocket.close(code=1008, reason="Room not found")
            return

        await manager.connect(websocket, user, room_id)

        try:
            messages, has_more = chat_repo.get_recent_messages(room_id, limit=50)

            message_responses = []
            for msg in messages:
                message_response = {
                    "id": msg.id,
                    "content": msg.content,
                    "user_id": msg.user_id,
                    "username": msg.user.username,
                    "room_id": msg.room_id,
                    "created_at": msg.created_at.isoformat(),
                }
                message_responses.append(message_response)

            success = await manager.send_personal_message(
                json.dumps(
                    {
                        "type": "messages_history",
                        "data": {
                            "messages": message_responses,
                            "has_more": has_more,
                            "next_cursor": messages[-1].id
                            if messages and has_more
                            else None,
                        },
                    }
                ),
                websocket,
            )
            if not success:
                return

        except Exception as e:
            print(f"Error fetching recent messages: {e}")
            success = await manager.send_personal_message(
                json.dumps(
                    {"type": "error", "message": "Failed to fetch recent messages"}
                ),
                websocket,
            )
            if not success:
                return

        while True:
            try:
                if websocket not in manager.connection_map:
                    break

                data = await websocket.receive_text()
                message_data = json.loads(data)

                message_type = message_data.get("type")

                if message_type == "message":
                    content = message_data.get("content", "").strip()
                    if not content:
                        success = await manager.send_personal_message(
                            json.dumps(
                                {
                                    "type": "error",
                                    "message": "Message content cannot be empty",
                                }
                            ),
                            websocket,
                        )
                        if not success:
                            break
                        continue

                    try:
                        new_message = chat_repo.create_message(
                            content, getattr(user, "id"), room_id
                        )

                        message_response = {
                            "id": new_message.id,
                            "content": new_message.content,
                            "user_id": new_message.user_id,
                            "username": user.username,
                            "room_id": new_message.room_id,
                            "created_at": new_message.created_at.isoformat(),
                        }

                        await manager.broadcast_to_room(
                            {"type": "message", "data": message_response}, room_id
                        )

                    except Exception as e:
                        print(f"Error saving message: {e}")
                        success = await manager.send_personal_message(
                            json.dumps(
                                {"type": "error", "message": "Failed to save message"}
                            ),
                            websocket,
                        )
                        if not success:
                            break

                elif message_type == "fetch_messages":
                    cursor = message_data.get("cursor")
                    limit = min(message_data.get("limit", 50), 100)  # Max 100 messages

                    try:
                        messages, has_more = chat_repo.get_recent_messages(
                            room_id, limit, cursor
                        )

                        message_responses = []
                        for msg in messages:
                            message_response = {
                                "id": msg.id,
                                "content": msg.content,
                                "user_id": msg.user_id,
                                "username": msg.user.username,
                                "room_id": msg.room_id,
                                "created_at": msg.created_at.isoformat(),
                            }
                            message_responses.append(message_response)

                        success = await manager.send_personal_message(
                            json.dumps(
                                {
                                    "type": "messages_history",
                                    "data": {
                                        "messages": message_responses,
                                        "has_more": has_more,
                                        "next_cursor": messages[-1].id
                                        if messages and has_more
                                        else None,
                                    },
                                }
                            ),
                            websocket,
                        )
                        if not success:
                            break

                    except Exception as e:
                        print(f"Error fetching messages: {e}")
                        success = await manager.send_personal_message(
                            json.dumps(
                                {"type": "error", "message": "Failed to fetch messages"}
                            ),
                            websocket,
                        )
                        if not success:
                            break

                else:
                    success = await manager.send_personal_message(
                        json.dumps(
                            {
                                "type": "error",
                                "message": f"Unknown message type: {message_type}",
                            }
                        ),
                        websocket,
                    )
                    if not success:
                        break

            except WebSocketDisconnect:
                break
            except json.JSONDecodeError:
                success = await manager.send_personal_message(
                    json.dumps({"type": "error", "message": "Invalid JSON format"}),
                    websocket,
                )
                if not success:
                    break
            except Exception as e:
                print(f"Error processing message: {e}")
                error_msg = str(e).lower()
                if any(
                    phrase in error_msg
                    for phrase in ["disconnect", "websocket", "closed", "cannot call"]
                ):
                    print("WebSocket connection error detected, breaking loop")
                    break

                success = await manager.send_personal_message(
                    json.dumps(
                        {"type": "error", "message": "Error processing message"}
                    ),
                    websocket,
                )
                if not success:
                    break

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)
    finally:
        db.close()
