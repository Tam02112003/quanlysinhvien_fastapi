from fastapi import FastAPI
from app.routes import students, classes,search,auth
app = FastAPI(title="Auth-Student-Class-Search Management API")

app.include_router(students.router)
app.include_router(classes.router)
app.include_router(search.router)
app.include_router(auth.router)
