import datetime
from typing import List, Optional

import graphene
from sqlalchemy.exc import IntegrityError, NoResultFound

from app.database import SessionLocal
from app.models.user import User
from app.models.post import Post
from app.schemas.user_schema import UserSchema
from app.schemas.post_schema import PostSchema


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


class CreateUser(graphene.Mutation):
    class Arguments:
        username: graphene.String(required=True)
        email: graphene.String(required=True)

    user = graphene.Field(UserSchema)

    def mutate(self, info, username: str, email: str):
        with SessionLocal() as session:
            new_user = User(username=username, email=email)
            session.add(new_user)
            try:
                session.commit()
                session.refresh(new_user)
            except IntegrityError as exc:
                session.rollback()
                raise graphene.GraphQLError(str(exc.orig))
            return CreateUser(user=new_user)


class UpdateUser(graphene.Mutation):
    class Arguments:
        id: graphene.Int(required=True)
        username: Optional[graphene.String]
        email: Optional[graphene.String]

    user = graphene.Field(UserSchema)

    def mutate(self, info, id: int, username: Optional[str] = None, email: Optional[str] = None):
        with SessionLocal() as session:
            try:
                user = session.query(User).filter_by(id=id).one()
            except NoResultFound:
                raise graphene.GraphQLError(f"User with id {id} not found")
            if username is not None:
                user.username = username
            if email is not None:
                user.email = email
            try:
                session.commit()
                session.refresh(user)
            except IntegrityError as exc:
                session.rollback()
                raise graphene.GraphQLError(str(exc.orig))
            return UpdateUser(user=user)


class DeleteUser(graphene.Mutation):
    class Arguments:
        id: graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id: int):
        with SessionLocal() as session:
            try:
                user = session.query(User).filter_by(id=id).one()
            except NoResultFound:
                raise graphene.GraphQLError(f"User with id {id} not found")
            session.delete(user)
            session.commit()
            return DeleteUser(ok=True)


class CreatePost(graphene.Mutation):
    class Arguments:
        title: graphene.String(required=True)
        content: graphene.String(required=True)
        author_id: graphene.Int(required=True)

    post = graphene.Field(PostSchema)

    def mutate(self, info, title: str, content: str, author_id: int):
        with SessionLocal() as session:
            try:
                author = session.query(User).filter_by(id=author_id).one()
            except NoResultFound:
                raise graphene.GraphQLError(f"Author with id {author_id} not found")
            new_post = Post(title=title, content=content, created_at=datetime.datetime.utcnow(), author=author)
            session.add(new_post)
            try:
                session.commit()
                session.refresh(new_post)
            except IntegrityError as exc:
                session.rollback()
                raise graphene.GraphQLError(str(exc.orig))
            return CreatePost(post=new_post)


class UpdatePost(graphene.Mutation):
    class Arguments:
        id: graphene.Int(required=True)
        title: Optional[graphene.String]
        content: Optional[graphene.String]

    post = graphene.Field(PostSchema)

    def mutate(self, info, id: int, title: Optional[str] = None, content: Optional[str] = None):
        with SessionLocal() as session:
            try:
                post = session.query(Post).filter_by(id=id).one()
            except NoResultFound:
                raise graphene.GraphQLError(f"Post with id {id} not found")
            if title is not None:
                post.title = title
            if content is not None:
                post.content = content
            try:
                session.commit()
                session.refresh(post)
            except IntegrityError as exc:
                session.rollback()
                raise graphene.GraphQLError(str(exc.orig))
            return UpdatePost(post=post)


class DeletePost(graphene.Mutation):
    class Arguments:
        id: graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(self, info, id: int):
        with SessionLocal() as session:
            try:
                post = session.query(Post).filter_by(id=id).one()
            except NoResultFound:
                raise graphene.GraphQLError(f"Post with id {id} not found")
            session.delete(post)
            session.commit()
            return DeletePost(ok=True)


class Query(graphene.ObjectType):
    user = graphene.Field(UserSchema, id=graphene.Int(required=True))
    users = graphene.List(UserSchema)
    post = graphene.Field(PostSchema, id=graphene.Int(required=True))
    posts = graphene.List(PostSchema)

    def resolve_user(self, info, id: int):
        with SessionLocal() as session:
            try:
                user = session.query(User).filter_by(id=id).one()
            except NoResultFound:
                raise graphene.GraphQLError(f"User with id {id} not found")
            return user

    def resolve_users(self, info):
        with SessionLocal() as session:
            return session.query(User).all()

    def resolve_post(self, info, id: int):
        with SessionLocal() as session:
            try:
                post = session.query(Post).filter_by(id=id).one()
            except NoResultFound:
                raise graphene.GraphQLError(f"Post with id {id} not found")
            return post

    def resolve_posts(self, info):
        with SessionLocal() as session:
            return session.query(Post).all()


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()