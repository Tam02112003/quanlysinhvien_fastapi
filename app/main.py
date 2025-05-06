from fastapi import FastAPI
from app.routes import students, classes

app = FastAPI(title="Student-Class Management API")

app.include_router(students.router)
app.include_router(classes.router)
