import json
from typing import Any, Dict

from graphql import GraphQLSchema, parse, validate, ExecutionContext
from graphql.language.ast import DocumentNode
from graphql.execution.middleware import MiddlewareManager
from graphql.type.definition import GraphQLError

from app.config import settings
from app.database import db_session
from app.models.user import User
from app.models.post import Post
from app.schemas.user_schema import user_schema
from app.schemas.post_schema import post_schema


class ValidationMiddleware:
    def __init__(self, schema: GraphQLSchema):
        self.schema = schema

    def __call__(
        self,
        next_,
        root: Any,
        info: ExecutionContext,
        *args,
        **kwargs,
    ) -> Any:
        document: DocumentNode = parse(info.context["query"])
        errors = validate(self.schema, document)
        if errors:
            raise GraphQLError(
                json.dumps([{"message": err.message} for err in errors])
            )
        return next_(root, info, *args, **kwargs)


def create_middleware_manager(schema: GraphQLSchema) -> MiddlewareManager:
    validator = ValidationMiddleware(schema)
    manager = MiddlewareManager(validator)
    return manager


def get_user_by_id(user_id: int) -> User | None:
    session = db_session()
    try:
        return session.query(User).filter(User.id == user_id).first()
    finally:
        session.close()


def get_post_by_id(post_id: int) -> Post | None:
    session = db_session()
    try:
        return session.query(Post).filter(Post.id == post_id).first()
    finally:
        session.close()


def serialize_user(user: User) -> Dict[str, Any]:
    if not user:
        return {}
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
    }


def serialize_post(post: Post) -> Dict[str, Any]:
    if not post:
        return {}
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author_id": post.author_id,
        "created_at": post.created_at.isoformat(),
    }


def validate_input(data: Dict[str, Any], schema) -> None:
    errors = []
    for field in data:
        if field not in schema.fields:
            errors.append(f"Field '{field}' is not defined in the schema.")
    if errors:
        raise ValueError(json.dumps(errors))


def serialize_response(result: Any) -> Any:
    if isinstance(result, User):
        return serialize_user(result)
    if isinstance(result, Post):
        return serialize_post(result)
    if isinstance(result, list):
        return [serialize_response(item) for item in result]
    return result