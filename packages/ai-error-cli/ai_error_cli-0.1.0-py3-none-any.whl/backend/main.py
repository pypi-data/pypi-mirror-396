from fastapi import FastAPI
from backend.routes.error_explainer import router as error_router

app = FastAPI(
    title="AI Error Explainer API",
    version="1.0.0"
)

app.include_router(error_router)
