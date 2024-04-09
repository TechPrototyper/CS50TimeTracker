from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime, timezone

class User(SQLModel, table=True):
    """
    Represents a user in the system with associated projects and tracking entries.

    Attributes:
        id (Optional[int]): The unique identifier of the user, automatically generated.
        first_name (str): The user's first name.
        middle_initial (Optional[str]): The user's middle initial, if any.
        last_name (str): The user's last name.
        email (str): The user's email address, must be unique.
        last_active (Optional[datetime]): The last active timestamp of the user.
        projects (List["Project"]): A list of projects owned by the user.
        trackings (List["Tracking"]): A list of tracking entries associated with the user.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    middle_initial: Optional[str] = Field(default=None, max_length=1)
    last_name: str
    email: str = Field(sa_column_kwargs={"unique": True})
    last_active: Optional[datetime] = None
    projects: List["Project"] = Relationship(back_populates="owner")
    trackings: List["Tracking"] = Relationship(back_populates="user")

class Project(SQLModel, table=True):
    """
    Represents a project in the system with associated tracking entries.

    Attributes:
        id (Optional[int]): The unique identifier of the project, automatically generated.
        name (str): The name of the project.
        state (str): The current state of the project, defaults to 'active'. Consider using an Enum for practical usage.
        archive_date (Optional[datetime]): The timestamp when the project was archived.
        tracking_count (int): The number of tracking entries associated with the project.
        created_at (datetime): The creation timestamp of the project.
        user_id (int): The foreign key linking to the user who owns the project.
        owner (User): The user who owns the project.
        trackings (List["Tracking"]): A list of tracking entries associated with the project.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    state: str = Field(default="active")  # In der Praxis vielleicht besser ein Enum nutzen
    archive_date: Optional[datetime] = None
    tracking_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: int = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="projects")
    trackings: List["Tracking"] = Relationship(back_populates="project")

class Tracking(SQLModel, table=True):
    """
    Represents a tracking entry in the system, linked to a user and optionally a project.

    Attributes:
        id (Optional[int]): The unique identifier of the tracking entry, automatically generated.
        date_time (datetime): The timestamp of the tracking entry.
        user_id (int): The foreign key linking to the associated user.
        project_id (Optional[int]): The foreign key linking to the associated project, if any.
        action (str): The type of action, e.g., 'Work Start', 'Break', etc.
        message (Optional[str]): An optional message associated with the tracking entry.
        user (User): The user associated with the tracking entry.
        project (Optional[Project]): The project associated with the tracking entry, if any.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    date_time: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: int = Field(foreign_key="user.id")
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    action: str  # Aktionstyp, z.B. "Arbeitsbeginn", "Pause", etc.
    message: Optional[str] = None
    user: User = Relationship(back_populates="trackings")
    project: Optional[Project] = Relationship(back_populates="trackings")

    