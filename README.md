# Simple Chat - Real-time WebSocket Chat Application

A real-time chat application built with FastAPI, WebSockets, PostgreSQL, and JWT authentication. Features include user authentication, chat rooms, message history, and comprehensive API documentation.

## Features

- **Real-time Messaging**: WebSocket-based chat with instant message delivery
- **User Authentication**: JWT-based authentication with role-based access control (RBAC)
- **Chat Rooms**: Support for multiple chat rooms with room-based messaging
- **Message History**: Paginated message history with cursor-based pagination
- **User Management**: User registration, login, and profile management
- **API Documentation**: Comprehensive Swagger/OpenAPI documentation
- **Database Migration**: Alembic-based database migrations
- **Docker Support**: Containerized application with Docker Compose
- **Connection Management**: Robust WebSocket connection handling with automatic cleanup

## Tech Stack

- **Backend**: FastAPI (Python 3.13)
- **Database**: PostgreSQL 15
- **Authentication**: JWT tokens with PassLib and Bcrypt
- **WebSockets**: Native FastAPI WebSocket support
- **ORM**: SQLAlchemy 2.0 with AsyncPG
- **Migrations**: Alembic
- **Containerization**: Docker & Docker Compose
- **Code Quality**: Black, Flake8, MyPy, isort

## Prerequisites

- Docker and Docker Compose
- Python 3.13+ (for local development)
- Poetry (for dependency management)

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd socket-chat
   ```

2. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Set up the database**

   ```bash
   # Run migrations
   make revision m='Migration message'

   make migrate
   ```

4. **Start the application**

   ```bash
   make docker-up
   ```

5. **Access the application**
   - API Documentation: <http://localhost:8000/docs>
   - WebSocket endpoint: ws://localhost:8000/api/v1/ws/{room_id}

## API Authentication  

### Getting Started

1. **Register a new user**

   ```bash
   POST /api/v1/auth/register
   {
     "username": "your_username",
     "email": "your_email@example.com",
     "password": "your_password"
   }
   ```

2. **Login to get JWT token**

   ```bash
   POST /api/v1/auth/login
   {
     "username": "your_username",
     "password": "your_password"
   }
   ```

3. **Use the token for authenticated requests**

   ```bash
   Authorization: Bearer <your_jwt_token>
   ```

## WebSocket Chat Usage

### Message Formats

#### Send a Messages

```json
{
    "type": "message",
    "content": "Hello, world!"
}
```

#### Fetch Message History

```json
{
    "type": "fetch_messages",
    "cursor": 123,
    "limit": 50
}
```

## Project Structure

```
socket-chat/
├── src/sc_chat/
│   ├── api/v1/                 # API endpoints
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── chat_docs.py       # Chat documentation
│   │   ├── rooms.py           # Room management
│   │   └── user.py            # User management
│   ├── core/
│   │   └── config.py          # Application configuration
│   ├── database/
│   │   ├── base.py            # Database base classes
│   │   └── conn.py            # Database connection
│   ├── models/                # SQLAlchemy models
│   │   ├── user.py
│   │   ├── room.py
│   │   └── message.py
│   ├── repository/            # Data access layer
│   ├── schemas/               # Pydantic schemas
│   ├── security/              # Authentication & authorization
│   ├── websocket/             # WebSocket handlers
│   │   ├── auth.py            # WebSocket authentication
│   │   ├── chat.py            # Chat WebSocket endpoint
│   │   └── connection_manager.py # Connection management
│   └── main.py                # FastAPI application
├── alembic/                   # Database migrations
├── tests/                     # Test files
├── docker-compose.yml         # Docker services
├── Dockerfile                 # Docker image
└── pyproject.toml            # Poetry dependencies
```

## Database Schema

### Users

- Authentication and user profile information
- Role-based access control (admin, user)

### Rooms

- Chat room management
- Room metadata and settings

### Messages

- Chat messages with timestamps
- User and room associations
- Pagination support

## API Documentation

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>
- **WebSocket Info**: GET /api/v1/chat/websocket-info
