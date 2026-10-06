from fastapi import FastAPI

app = FastAPI(
    description="This is the FastAPI LinkedIn clone project. It is a simple implementation of a LinkedIn-like application using FastAPI.",
    version="1.0.0",
    title="FastAPI LinkedIn Clone Project",
)

@app.get("/")
def read_root():
    return {"FastAPI : Linkedin clone project": "Welcome to the FastAPI LinkedIn clone project!"}