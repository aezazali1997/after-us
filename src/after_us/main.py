from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import Field, SQLModel, create_engine, Session, select
from todo_app import setting
from contextlib import asynccontextmanager

connection_string: str = str(setting.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg"
)

engine = create_engine(
    connection_string,
    connect_args={"sslmode": "require"},
    pool_recycle=300,
    pool_size=10,
    echo=True,
)


class Todo(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    content: str = Field(index=True, min_length=3, max_length=60)
    is_completed: bool = Field(default=False)


@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    yield


app: FastAPI = FastAPI(lifespan=lifespan)


def with_session():
    with Session(engine) as session:
        yield session


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.post(
    "/todos",
    response_model=Todo,
)
async def create_todo(todo: Todo, session: Session = Depends(with_session)):
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo


@app.get("/todos", response_model=list[Todo])
def get_todos(session: Session = Depends(with_session)):
    todos = session.exec(select(Todo)).all()
    return todos


@app.get("/todos/{todo_id}", response_model=Todo)
def get_todo(todo_id: int, session: Session = Depends(with_session)):
    select_query = select(Todo).where(Todo.id == todo_id)
    todo = session.exec(select_query).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@app.patch("/todos/{todo_id}", response_model=Todo)
def update_todo(todo_id: int, todo: Todo, session: Session = Depends(with_session)):
    select_query = select(Todo).where(Todo.id == todo_id)
    existing = session.exec(select_query).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Todo not found")
    existing.content = todo.content
    existing.is_completed = todo.is_completed
    session.add(existing)
    session.commit()
    session.refresh(existing)
    return existing


@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int, session: Session = Depends(with_session)):
    select_query = select(Todo).where(Todo.id == todo_id)
    todo = session.exec(select_query).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    session.delete(todo)
    session.commit()
    return {
        "message": "Todo deleted successfully",
    }
