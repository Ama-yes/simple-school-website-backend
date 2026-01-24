from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
from app.api.v1 import student_router, admin_router, teacher_router
from app.core.logging import setup_logger
from app.db.database import engine
from app.models.models import Base
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    
    yield
    


app = FastAPI(lifespan=lifespan)
app.include_router(student_router.router, prefix="/student", tags=["Students Route"])
app.include_router(teacher_router.router, prefix="/teacher", tags=["Teachers Route"])
app.include_router(admin_router.router, prefix="/admin", tags=["Admins Route"])

logger = setup_logger()

@app.exception_handler(Exception)
async def handle_except(request: Request, exception: Exception):
    logger.error(f"Error processing {request.method} {request.url}", exc_info=exception)
    return JSONResponse(status_code=500, content={"detail": str(exception)})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)