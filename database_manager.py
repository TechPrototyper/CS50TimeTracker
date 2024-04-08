from sqlmodel import create_engine, Session, SQLModel
from contextlib import contextmanager

class DatabaseManager:
    """
    Manages database connections and operations for the application.

    Provides methods to create the engine, create database tables, and manage sessions for executing database operations.

    Attributes:
        database_url (str): The database connection URL.
        engine: The SQLAlchemy engine for database connections, initialized to None.
    """
    def __init__(self, database_url: str):
        """
        Initializes the DatabaseManager with the provided database URL.

        Args:
            database_url (str): The database connection URL.
        """
        self.database_url = database_url
        self.engine = None

    def create_engine(self):
        """
        Creates the SQLAlchemy engine using the database URL provided during initialization.

        Sets the `echo` flag to True for logging SQL queries.
        """
        self.engine = create_engine(self.database_url, echo=True)

    def create_tables(self):
        """
        Creates all tables defined in the SQLModel metadata within the database.

        Raises:
            ValueError: If the engine has not been initialized before attempting to create tables.
        """
        if self.engine is None:
            raise ValueError("Engine ist nicht initialisiert.")
        SQLModel.metadata.create_all(self.engine)

    @contextmanager
    def session(self):
        """
        Context manager for database sessions.

        Yields a session bound to the engine and ensures that the session is committed on successful execution
        or rolled back in case of an exception. Finally, the session is closed.

        Yields:
            Session: A SQLAlchemy session bound to the engine.

        Raises:
            Any exception that occurs within the context block is propagated after performing a rollback.
        """
        session = Session(bind=self.engine)
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()