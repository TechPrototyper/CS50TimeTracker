from sqlmodel import Field, SQLModel, Relationship
from typing import Optional, List
from datetime import datetime

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
    state: str = Field(default="active")  # In der Praxis vielleicht besser ein Enum nutzen
    archive_date: Optional[datetime] = None
    tracking_count: int = Field(default=0)
    created_at: datetime = Field(default_factory=datetime.now(datetime.timezone.utc))
    user_id: int = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="projects")
    trackings: List["Tracking"] = Relationship(back_populates="project")

class Tracking(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date_time: datetime = Field(default_factory=datetime.now(datetime.timezone.utc))
    user_id: int = Field(foreign_key="user.id")
    project_id: Optional[int] = Field(default=None, foreign_key="project.id")
    action: str  # Aktionstyp, z.B. "Arbeitsbeginn", "Pause", etc.
    message: Optional[str] = None
    user: User = Relationship(back_populates="trackings")
    project: Optional[Project] = Relationship(back_populates="trackings")

    