from fastapi import FastAPI
import uvicorn
from app.api.v1 import student_router

app = FastAPI()
app.include_router(student_router.router, prefix="/students", tags=["Students Route"])




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)