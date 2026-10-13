from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.db.database import test_db_connection
from app.routers import auth , profile , post , education , experience , skill , company , institution , user


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

app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(post.router)
app.include_router(experience.router)
app.include_router(education.router)
app.include_router(skill.skills_router)
app.include_router(skill.user_skills_router)
app.include_router(company.router)
app.include_router(institution.router)
app.include_router(user.router)
