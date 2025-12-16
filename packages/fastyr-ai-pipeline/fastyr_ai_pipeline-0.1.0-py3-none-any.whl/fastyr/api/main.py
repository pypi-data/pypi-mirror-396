from fastapi import FastAPI
import uvicorn
from strawberry.fastapi import GraphQLRouter
import structlog
from fastyr.api.graphql.schema import schema
from fastyr.api.controllers.health_controller import router as health_router
from fastyr.api.controllers.pipeline_controller import router as pipeline_router
from fastyr.api.controllers.auth_controller import router as auth_router
from fastyr.infrastructure.database.connection import init_db
from fastapi.middleware.cors import CORSMiddleware

logger = structlog.get_logger(__name__)

app = FastAPI(
    title="Fastyr AI Pipeline",
    description="Enterprise-grade AI pipeline for STT, LLM, and TTS processing"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL setup
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")

# REST endpoints
app.include_router(health_router)
app.include_router(pipeline_router)
app.include_router(auth_router)

@app.on_event("startup")
async def startup_event():
    logger.info("Initializing application...")
    await init_db()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)