from fastapi import FastAPI
from routers.test_router import router as test_router
from routers.question_router import router as question_router



app = FastAPI(
    title="Test API"
)

app.include_router(test_router)
app.include_router(question_router)
