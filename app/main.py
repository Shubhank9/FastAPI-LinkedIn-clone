from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import test_db_connection
from app.routers import auth
from app.routers import profile


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting application...")

    try:
        test_db_connection()
        print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")
        raise

    yield

    print("Shutting down application...")



app = FastAPI(
    description="This is the FastAPI LinkedIn clone project. It is a simple implementation of a LinkedIn-like application using FastAPI.",
    version="1.0.0",
    title="FastAPI LinkedIn Clone Project",
    lifespan=lifespan
)

@app.get("/")
def read_root():
    return {"FastAPI : Linkedin clone project": "Welcome to the FastAPI LinkedIn clone project!"}

app.include_router(auth.router)
app.include_router(profile.router)