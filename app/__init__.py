import os
from typing import Callable

from fastapi import FastAPI, Request, Response
from sqlalchemy.orm import sessionmaker
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .database import engine, SessionLocal
from .models.user import User
from .models.post import Post
from .schemas.user_schema import UserSchema
from .schemas.post_schema import PostSchema
from .graphql.schema import schema as graphql_schema
from .middleware.validation_middleware import ValidationMiddleware
from .utils.logger import get_logger

logger = get_logger(__name__)

def create_app() -> FastAPI:
    app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

    @app.on_event("startup")
    async def startup():
        try:
            engine.begin()
            User.metadata.create_all(bind=engine)
            Post.metadata.create_all(bind=engine)
        finally:
            engine.dispose()

    @app.middleware("http")
    async def db_session_middleware(request: Request, call_next: Callable):
        request.state.db = SessionLocal()
        response = await call_next(request)
        request.state.db.close()
        return response

    app.add_middleware(BaseHTTPMiddleware, dispatch=ValidationMiddleware)

    @app.get("/health", tags=["Health"])
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/graphql")
    async def graphql_endpoint(request: Request):
        data = await request.json()
        context = {"request": request}
        result = await graphql_schema.execute(
            query=data.get("query"),
            variable_values=data.get("variables"),
            operation_name=data.get("operationName"),
            context_value=context,
        )
        return Response(content=result.to_json(), media_type="application/json")

    @app.on_event("shutdown")
    async def shutdown():
        SessionLocal.remove()
        engine.dispose()

    return app

app = create_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)