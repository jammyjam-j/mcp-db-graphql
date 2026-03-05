from datetime import datetime

import marshmallow as ma
from marshmallow import validates, ValidationError
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field

from app.models.post import Post


class PostSchema(SQLAlchemySchema):
    class Meta:
        model = Post
        load_instance = True
        sqla_session = None

    id = auto_field(dump_only=True)
    title = auto_field(required=True)
    content = auto_field(required=True)
    author_id = auto_field(required=True, data_key="authorId")
    created_at = auto_field(dump_only=True, data_key="createdAt")
    updated_at = auto_field(dump_only=True, data_key="updatedAt")

    @validates("title")
    def validate_title(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Title must be a non-empty string.")
        if len(value) > 255:
            raise ValidationError("Title cannot exceed 255 characters.")

    @validates("content")
    def validate_content(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Content must be a non-empty string.")


class PostCreateSchema(ma.Schema):
    title = ma.Str(required=True)
    content = ma.Str(required=True)
    author_id = ma.Int(required=True, data_key="authorId")

    @validates("title")
    def validate_title(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Title must be a non-empty string.")
        if len(value) > 255:
            raise ValidationError("Title cannot exceed 255 characters.")

    @validates("content")
    def validate_content(self, value):
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Content must be a non-empty string.")


class PostUpdateSchema(ma.Schema):
    title = ma.Str()
    content = ma.Str()

    @validates("title")
    def validate_title(self, value):
        if value is None:
            return
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Title must be a non-empty string.")
        if len(value) > 255:
            raise ValidationError("Title cannot exceed 255 characters.")

    @validates("content")
    def validate_content(self, value):
        if value is None:
            return
        if not isinstance(value, str) or not value.strip():
            raise ValidationError("Content must be a non-empty string.")


def serialize_post(post: Post) -> dict:
    schema = PostSchema()
    return schema.dump(post)


def deserialize_post(data: dict) -> Post:
    schema = PostCreateSchema()
    validated_data = schema.load(data)
    post = Post(**validated_data)
    post.created_at = datetime.utcnow()
    post.updated_at = datetime.utcnow()
    return post


def update_post(post: Post, data: dict) -> Post:
    schema = PostUpdateSchema()
    validated_data = schema.load(data, partial=True)
    for key, value in validated_data.items():
        setattr(post, key, value)
    post.updated_at = datetime.utcnow()
    return post