from fastapi import FastAPI
import uvicorn
from app.api.v1 import student_router, admin_router

app = FastAPI()
app.include_router(student_router.router, prefix="/student", tags=["Students Route"])
app.include_router(admin_router.router, prefix="/admin", tags=["Admins Route"])




if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)