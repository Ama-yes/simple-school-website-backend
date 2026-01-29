from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi_limiter import FastAPILimiter
import uvicorn
from app.api.v1 import student_router, admin_router, teacher_router
from app.core.logging import setup_logger
from app.db.database import engine
from app.models.models import Base
from app.core.caching import async_redis_client
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    
    await FastAPILimiter.init(async_redis_client)
    
    yield
    
    await async_redis_client.close()


app = FastAPI(lifespan=lifespan)
app.include_router(student_router.router, prefix="/student", tags=["Students Route"])
app.include_router(teacher_router.router, prefix="/teacher", tags=["Teachers Route"])
app.include_router(admin_router.router, prefix="/admin", tags=["Admins Route"])

logger = setup_logger()

@app.exception_handler(Exception)
async def handle_except(request: Request, exception: Exception):
    logger.error(f"Error processing {request.method} {request.url}", exc_info=exception)
    if isinstance(exception, ValueError):
        return JSONResponse(status_code=400, content={"detail": str(exception)})
    else:
        return JSONResponse(status_code=500, content={"detail": "Unexpected error occurred!"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)