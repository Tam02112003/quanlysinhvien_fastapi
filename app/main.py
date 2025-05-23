from fastapi import FastAPI ,Request
from app.routes import students, classes,search,auth
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from app.database import lifespan
import logging


app = FastAPI(lifespan=lifespan)

app.add_middleware(GZipMiddleware, minimum_size=1000)

logger = logging.getLogger(__name__)
# Middleware giới hạn kích thước request
@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    MAX_SIZE = 1 * 1024 * 1024  # 1MB
    content_length = request.headers.get("content-length")

    if content_length and int(content_length) > MAX_SIZE:
        return JSONResponse(
            {"error": "Request too large"},
            status_code=413
        )

    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Request error: {str(e)}")
        raise

app.include_router(students.router)
app.include_router(classes.router)
app.include_router(search.router)
app.include_router(auth.router)
