# SITR Architecture Documentation

## Table of Contents
- [Overview](#overview)
- [Design Principles](#design-principles)
- [Layer Architecture](#layer-architecture)
- [Core Components](#core-components)
- [Data Flow](#data-flow)
- [API Design](#api-design)
- [Database Schema](#database-schema)
- [Key Design Decisions](#key-design-decisions)

---

## Overview

SITR follows a **Domain-Driven Design (DDD)** architecture with clear separation of concerns across multiple layers. The system is designed to be extensible, testable, and maintainable while providing a clean CLI interface backed by a complete REST API.

### Architecture at a Glance

```
┌─────────────────────────────────────────────────────────────┐
│                     Presentation Layer                       │
│  ┌──────────────────────┐       ┌────────────────────────┐  │
│  │   CLI (Typer + Rich) │       │   Future: Web UI       │  │
│  └──────────┬───────────┘       └────────────────────────┘  │
└─────────────┼───────────────────────────────────────────────┘
              │ HTTP/REST
┌─────────────▼───────────────────────────────────────────────┐
│                     API Client Layer                         │
│  • Server auto-start logic                                   │
│  • HTTP request handling with retries                        │
│  • Error handling and transformation                         │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│                      API Layer (FastAPI)                     │
│  • Request validation (Pydantic)                             │
│  • Response serialization                                    │
│  • CORS middleware                                           │
│  • 16 REST endpoints                                         │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│                      Service Layer                           │
│  • TimeManagementService (business logic)                    │
│  • Transaction management                                    │
│  • Workflow orchestration                                    │
│  • Validation rules                                          │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│                    Repository Layer                          │
│  • BaseRepository (generic CRUD)                             │
│  • UserRepository                                            │
│  • ProjectRepository                                         │
│  • TrackingRepository                                        │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│                     Domain Models                            │
│  • User (SQLModel)                                           │
│  • Project (SQLModel)                                        │
│  • Tracking (SQLModel)                                       │
│  • Enums (ActionType, ProjectState)                          │
└─────────────┬───────────────────────────────────────────────┘
              │
┌─────────────▼───────────────────────────────────────────────┐
│                      Database Layer                          │
│  • SQLite                                                    │
│  • SQLAlchemy (via SQLModel)                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Design Principles

### 1. Domain-Driven Design (DDD)

The codebase is organized around the business domain (time tracking) rather than technical concerns:

- **Domain Models** (`sitr_models.py`) - Pure business entities
- **Repositories** - Data access abstraction
- **Services** - Business logic and orchestration
- **API** - External interface

### 2. Single Responsibility Principle

Each component has one clear purpose:

- **CLI** - User interaction
- **API Client** - HTTP communication
- **API Server** - Request/response handling
- **Service Layer** - Business rules
- **Repositories** - Data persistence

### 3. Dependency Inversion

Higher-level modules don't depend on lower-level modules:

```python
# Service depends on abstraction (Repository interface)
# Not on concrete implementation (SQLAlchemy)
service = TimeManagementService(user_repo, project_repo, tracking_repo)
```

### 4. SQLModel Magic

Using SQLModel provides:
- **Single source of truth** - One model for DB and API
- **Type safety** - Pydantic validation + SQLAlchemy ORM
- **No impedance mismatch** - snake_case throughout
- **Automatic serialization** - No custom serializers needed

---

## Layer Architecture

### 1. Presentation Layer

**Files**: `sitr_cli.py`

**Responsibilities**:
- Parse user commands
- Display formatted output (Rich tables)
- Error handling and user feedback
- Call API Client for all operations

**Key Features**:
- Typer for command structure
- Rich for beautiful terminal output
- No direct database access
- All operations go through API

```python
@user_app.command("list")
def list_users():
    """List all registered users."""
    client = get_client()
    users = client.list_users()
    # Display with Rich table
```

### 2. API Client Layer

**Files**: `api_client.py`

**Responsibilities**:
- HTTP communication with API server
- Server auto-start logic
- Request retry mechanisms
- Error transformation

**Key Features**:

```python
class APIClient:
    def _ensure_server_running(self):
        """Start server if not running."""
        if not self._check_health():
            self.server_manager.start()
    
    def _make_request(self, method, endpoint, data=None):
        """Make HTTP request with auto-start."""
        self._ensure_server_running()
        # Retry logic with exponential backoff
```

### 3. API Layer

**Files**: `sitr_api.py`

**Responsibilities**:
- REST endpoint definitions
- Request validation
- Response serialization
- CORS configuration

**Endpoint Structure**:

```python
@app.post("/api/users", response_model=UserResponse)
def create_user(user_data: UserCreate):
    db_manager = get_db_manager()
    user_repo = UserRepository(db_manager, User)
    user = user_repo.add({
        "first_name": user_data.first_name,
        # ...
    })
    return user
```

**Response Models** (Pydantic):

```python
class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: str
    middle_initial: Optional[str] = None
    last_active: Optional[datetime] = None
    
    model_config = {"from_attributes": True}
```

### 4. Service Layer

**Files**: `time_management_service.py`

**Responsibilities**:
- Business logic enforcement
- Workflow orchestration
- Transaction coordination
- Complex state management

**Key Workflows**:

#### Project Handover Logic
```python
def start_project(self, user_id: int, project_name: str):
    # 1. End any currently running project
    current_project = self._get_active_project(user_id)
    if current_project:
        self.end_project(user_id, current_project.name)
    
    # 2. Start new project
    self.tracking_repo.add({
        "user_id": user_id,
        "project_id": project.id,
        "action_type": ActionType.START_PROJECT,
        # ...
    })
```

#### Auto-Cleanup on End Day
```python
def end_day(self, user_id: int):
    # Close all open projects
    # End all active breaks
    # Create END_DAY tracking entry
```

### 5. Repository Layer

**Files**: `database_repositories.py`

**Responsibilities**:
- CRUD operations
- Query abstraction
- Database session management
- Entity-specific queries

**Base Repository Pattern**:

```python
class BaseRepository:
    def add(self, obj_dict: dict):
        obj = self.model(**obj_dict)
        self.session.add(obj)
        self.session.commit()
        return obj
    
    def get(self, obj_id: int):
        return self.session.get(self.model, obj_id)
    
    def list_all(self):
        return self.session.exec(
            select(self.model)
        ).all()
```

**Specialized Repositories**:

```python
class UserRepository(BaseRepository):
    def get_by_email(self, email: str):
        return self.session.exec(
            select(User).where(User.email == email)
        ).first()

class ProjectRepository(BaseRepository):
    def get_active_projects(self, user_id: int):
        return self.session.exec(
            select(Project)
            .where(Project.owner_id == user_id)
            .where(Project.state == ProjectState.ACTIVE)
        ).all()
```

### 6. Domain Model Layer

**Files**: `sitr_models.py`, `enums.py`

**Responsibilities**:
- Define business entities
- Relationships
- Constraints

**Models**:

```python
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    middle_initial: Optional[str] = Field(default=None, max_length=1)
    last_name: str
    email: str = Field(sa_column_kwargs={"unique": True})
    last_active: Optional[datetime] = None
    projects: List["Project"] = Relationship(back_populates="owner")
    trackings: List["Tracking"] = Relationship(back_populates="user")

class Project(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    state: ProjectState = Field(default=ProjectState.ACTIVE)
    owner_id: int = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="projects")
    trackings: List["Tracking"] = Relationship(back_populates="project")

class Tracking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    project_id: Optional[int] = Field(foreign_key="project.id")
    action_type: ActionType
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    message: Optional[str] = None
```

**Enums**:

```python
class ActionType(str, Enum):
    START_DAY = "start_day"
    END_DAY = "end_day"
    START_PROJECT = "start_project"
    END_PROJECT = "end_project"
    START_BREAK = "start_break"
    END_BREAK = "end_break"

class ProjectState(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
```

---

## Core Components

### 1. Server Manager

**File**: `server_manager.py`

**Purpose**: Manage uvicorn server lifecycle

**Features**:
- Platform-independent process management (psutil)
- PID file handling
- Health checks via HTTP
- Log capture

```python
class ServerManager:
    def start(self) -> Tuple[bool, str]:
        """Start the server as subprocess."""
        process = subprocess.Popen([
            sys.executable,
            os.path.join(self.project_root, "sitr_api.py")
        ])
        self._save_pid(process.pid)
    
    def stop(self) -> Tuple[bool, str]:
        """Stop the server gracefully."""
        pid = self._read_pid()
        if pid and self._is_sitr_server(pid):
            psutil.Process(pid).terminate()
    
    def is_running(self) -> bool:
        """Check if server is running and healthy."""
        return self._check_health()
```

### 2. Configuration Manager

**File**: `config_manager.py`

**Purpose**: Manage application configuration

**Features**:
- Singleton pattern
- JSON-based storage (`~/.sitrconfig`)
- Auto-migration from old format
- Type-safe getters/setters

```python
class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def get_current_user_id(self) -> Optional[int]:
        """Get selected user ID."""
        return self.config.get("current_user_id")
    
    def set_current_user(self, user_id: int, email: str):
        """Save current user selection."""
        self.config["current_user_id"] = user_id
        self.config["current_user_email"] = email
        self._save_config()
```

### 3. Database Manager

**File**: `database_manager.py`

**Purpose**: Database connection and session management

```python
class DatabaseManager:
    def __init__(self, db_url: str = "sqlite:///sitr.db"):
        self.engine = create_engine(db_url)
        SQLModel.metadata.create_all(self.engine)
    
    @contextmanager
    def get_db(self):
        """Context manager for database sessions."""
        session = Session(self.engine)
        try:
            yield session
        finally:
            session.close()
```

---

## Data Flow

### Example: Starting a Project

```
┌──────────────────────────────────────────────────────────┐
│ 1. User Input                                            │
│    $ python sitr_cli.py start "CS50 Project"             │
└──────────────┬───────────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────────┐
│ 2. CLI Layer (sitr_cli.py)                               │
│    • Parse command and arguments                         │
│    • Get API client                                      │
│    • Call client.start_project("CS50 Project")           │
└──────────────┬───────────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────────┐
│ 3. API Client (api_client.py)                            │
│    • Check if server is running                          │
│    • Auto-start server if needed                         │
│    • POST /api/projects/start with JSON payload          │
└──────────────┬───────────────────────────────────────────┘
               │ HTTP
┌──────────────▼───────────────────────────────────────────┐
│ 4. API Layer (sitr_api.py)                               │
│    • Validate request (Pydantic)                         │
│    • Extract project_name from request                   │
│    • Call service layer                                  │
└──────────────┬───────────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────────┐
│ 5. Service Layer (time_management_service.py)            │
│    • Get current user from config                        │
│    • Check for active project                            │
│    • End active project if exists (handover)             │
│    • Start new project                                   │
└──────────────┬───────────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────────┐
│ 6. Repository Layer (database_repositories.py)           │
│    • Create Tracking entry                               │
│    • Insert into database                                │
│    • Commit transaction                                  │
└──────────────┬───────────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────────┐
│ 7. Database (SQLite)                                     │
│    • Store tracking record                               │
│    • Update project state if needed                      │
└──────────────┬───────────────────────────────────────────┘
               │
┌──────────────▼───────────────────────────────────────────┐
│ 8. Response Flow (back up the chain)                     │
│    • Repository returns Tracking object                  │
│    • Service returns with timestamp                      │
│    • API serializes to JSON                              │
│    • Client receives response                            │
│    • CLI displays: ✓ Started working on 'CS50 Project'  │
└──────────────────────────────────────────────────────────┘
```

---

## API Design

### REST Principles

The API follows REST conventions:

- **Resources** - Users, Projects, Workdays, Breaks
- **HTTP Methods** - GET (read), POST (create/action), PUT (update), DELETE (remove)
- **Status Codes** - 200 (OK), 201 (Created), 400 (Bad Request), 404 (Not Found), 500 (Server Error)
- **JSON** - Request and response bodies

### Endpoint Categories

#### Health Check
```
GET /health
Response: {"status": "healthy"}
```

#### User Management
```
POST   /api/users              # Create user
GET    /api/users              # List all users
GET    /api/users/{email}      # Get user by email
PUT    /api/users/{email}      # Update user
DELETE /api/users/{email}      # Delete user
POST   /api/users/{email}/select  # Select active user
```

#### Workday Management
```
POST   /api/workday/start      # Start workday
POST   /api/workday/end        # End workday
```

#### Project Management
```
POST   /api/projects           # Create project
GET    /api/projects           # List active projects
POST   /api/projects/start     # Start working on project
POST   /api/projects/end       # End work on project
POST   /api/projects/archive   # Archive project
```

#### Break Management
```
POST   /api/breaks/start       # Start break
POST   /api/breaks/end         # End break
POST   /api/breaks/continue    # Resume work after break
```

### Request/Response Models

Using Pydantic for validation:

```python
# Request
class ProjectStartRequest(BaseModel):
    project_name: str

# Response
class ProjectStartResponse(BaseModel):
    success: bool
    message: str
    project_name: str
    timestamp: datetime
```

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────────┐
│       User          │
├─────────────────────┤
│ id (PK)             │
│ first_name          │
│ middle_initial      │
│ last_name           │
│ email (UNIQUE)      │
│ last_active         │
└──────────┬──────────┘
           │ 1
           │ owns
           │
           │ N
┌──────────▼──────────┐
│      Project        │
├─────────────────────┤
│ id (PK)             │
│ name                │
│ state               │
│ owner_id (FK)       │
│ created_at          │
│ archive_date        │
└──────────┬──────────┘
           │ 1
           │ tracks
           │
           │ N
┌──────────▼──────────┐
│     Tracking        │
├─────────────────────┤
│ id (PK)             │
│ user_id (FK)        │
│ project_id (FK)     │
│ action_type         │
│ timestamp           │
│ message             │
└─────────────────────┘
```

### Table Details

#### User Table
- **Purpose**: Store user information
- **Key Constraints**: Email must be unique
- **Relationships**: One-to-many with Projects and Tracking

#### Project Table
- **Purpose**: Store project definitions
- **States**: ACTIVE, ARCHIVED
- **Relationships**: Many-to-one with User, one-to-many with Tracking

#### Tracking Table
- **Purpose**: Store all time tracking events
- **Action Types**: START_DAY, END_DAY, START_PROJECT, END_PROJECT, START_BREAK, END_BREAK
- **Relationships**: Many-to-one with User and Project

---

## Key Design Decisions

### 1. Why SQLModel Over Pure SQLAlchemy?

**Decision**: Use SQLModel for all models

**Rationale**:
- Single model definition for DB and API
- Built-in Pydantic validation
- Type safety without duplication
- Automatic serialization with `from_attributes=True`

**Trade-off**: Slightly less flexibility than pure SQLAlchemy, but massive reduction in boilerplate.

### 2. Why Separate API Client?

**Decision**: CLI doesn't call service layer directly

**Rationale**:
- Clear separation of concerns
- API can be used by other clients (web, mobile)
- Server can run independently
- Easier testing and mocking

**Trade-off**: Additional HTTP overhead, but enables future multi-client architecture.

### 3. Why Auto-Start Server?

**Decision**: CLI automatically starts API server if not running

**Rationale**:
- Better user experience (no manual server management)
- Reduces friction for casual use
- Server starts on-demand

**Trade-off**: Slightly slower first command, but transparent to user.

### 4. Why Configuration File?

**Decision**: Use `~/.sitrconfig` instead of command-line flags

**Rationale**:
- Persistent user selection
- No need to pass user ID with every command
- Easy to extend with preferences
- Standard practice for CLI tools

**Trade-off**: One more file to manage, but improves UX significantly.

### 5. Why Snake Case Throughout?

**Decision**: Use `snake_case` for all fields (DB and API)

**Rationale**:
- Python convention
- No impedance mismatch
- SQLModel works seamlessly
- No custom serializers needed

**Trade-off**: API doesn't follow typical REST camelCase convention, but consistency is more valuable.

### 6. Why Handover Logic?

**Decision**: Starting a new project automatically ends the previous one

**Rationale**:
- Matches real human behavior
- Prevents parallel projects (mental context switching is rare)
- Cleaner data (no orphaned open projects)

**Trade-off**: Can't track truly parallel work, but this is intentional design choice.

### 7. Why Break Resume Logic?

**Decision**: Breaks remember which project was active

**Rationale**:
- Natural workflow: "I was working on X, took a break, now I'm back to X"
- Reduces commands needed
- More accurate time tracking

**Trade-off**: Can't easily switch projects after a break without explicit command.

---

## Performance Considerations

### Database

- **SQLite** is sufficient for single-user local usage
- All queries are simple (no complex joins)
- Indexes on `email` (unique constraint) and foreign keys
- Session lifecycle properly managed (context managers)

### API Server

- **Uvicorn** (ASGI) is fast and lightweight
- No authentication overhead (local-only use)
- Minimal middleware (only CORS for future use)
- Stateless design (no session management)

### CLI

- **Lazy imports** - API client only loaded when needed
- **Health check** - Single HTTP request before operations
- **Rich** - Terminal rendering is fast even with complex tables

---

## Security Considerations

### Current State (Local-Only)

- No authentication (server binds to localhost)
- No authorization (single user per instance)
- No encryption (local SQLite file)

### Future Enhancements

If deploying to network:
- Add JWT authentication
- Implement user roles
- Use HTTPS
- Switch to PostgreSQL with encrypted connections
- Add rate limiting

---

## Testing Strategy

### Unit Tests

- Repository layer tests (CRUD operations)
- Service layer tests (business logic)
- Model validation tests

### Integration Tests

- API endpoint tests
- Full workflow tests
- Database transaction tests

### CLI Tests

- Command parsing tests
- Output formatting tests
- Error handling tests

---

## Future Architecture Considerations

### Scalability

To support multi-user deployment:
1. Add authentication middleware
2. Switch to PostgreSQL
3. Add Redis for session management
4. Deploy with Docker
5. Add load balancer

### Extensibility

The architecture supports:
- **Web UI** - Use same API
- **Mobile app** - Use same API
- **Analytics engine** - Read from tracking table
- **Plugins** - Service layer can be extended
- **Integrations** - API can call external services

### Observability

Can be added:
- Structured logging (structlog)
- Metrics (Prometheus)
- Tracing (OpenTelemetry)
- Error tracking (Sentry)

---

## Conclusion

SITR's architecture demonstrates:

✅ **Clean separation of concerns** - Each layer has clear responsibility  
✅ **DDD principles** - Domain model drives design  
✅ **Type safety** - SQLModel + Pydantic throughout  
✅ **Extensibility** - Easy to add new clients or features  
✅ **Testability** - Each component can be tested independently  
✅ **Maintainability** - Clear structure and documentation  

The architecture started as a CS50 project design but evolved into a production-grade system that balances simplicity with professional software engineering practices.

---

*For implementation details and completion summary, see [PROJECT_COMPLETE.md](PROJECT_COMPLETE.md)*
