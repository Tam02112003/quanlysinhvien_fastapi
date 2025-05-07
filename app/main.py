from fastapi import FastAPI
from app.routes import students, classes
from app.routes import search
app = FastAPI(title="Student-Class-Search Management API")

app.include_router(students.router)
app.include_router(classes.router)
app.include_router(search.router)
