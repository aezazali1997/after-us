from sqlmodel import create_engine, Session, SQLModel
from ..config import DATABASE_URL

# Create engine with proper connection string
connection_string = str(DATABASE_URL).replace("postgresql", "postgresql+psycopg")

engine = create_engine(
    connection_string,
    connect_args={"sslmode": "require"},
    pool_recycle=300,
    pool_size=10,
    echo=True,
)


def create_db_and_tables():
    """Create database tables."""
    # SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)


def get_session():
    """Get database session."""
    with Session(engine) as session:
        yield session
