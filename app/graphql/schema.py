import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField

from app.models.user import User as UserModel
from app.models.post import Post as PostModel
from app.graphql.resolvers import (
    resolve_user,
    resolve_users,
    resolve_post,
    resolve_posts,
    create_user_mutation,
    update_user_mutation,
    delete_user_mutation,
    create_post_mutation,
    update_post_mutation,
    delete_post_mutation,
)


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (graphene.relay.Node,)


class Post(SQLAlchemyObjectType):
    class Meta:
        model = PostModel
        interfaces = (graphene.relay.Node,)


class Query(graphene.ObjectType):
    node = graphene.relay.Node.Field()
    user = graphene.Field(User, id=graphene.Int(required=True))
    users = SQLAlchemyConnectionField(User)
    post = graphene.Field(Post, id=graphene.Int(required=True))
    posts = SQLAlchemyConnectionField(Post)

    def resolve_user(self, info, id):
        return resolve_user(info, id)

    def resolve_users(self, info, **kwargs):
        return resolve_users(info, **kwargs)

    def resolve_post(self, info, id):
        return resolve_post(info, id)

    def resolve_posts(self, info, **kwargs):
        return resolve_posts(info, **kwargs)


class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)

    user = graphene.Field(lambda: User)

    @staticmethod
    def mutate(root, info, username, email):
        return create_user_mutation(root, info, username, email)


class UpdateUser(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        username = graphene.String()
        email = graphene.String()

    user = graphene.Field(lambda: User)

    @staticmethod
    def mutate(root, info, id, username=None, email=None):
        return update_user_mutation(root, info, id, username, email)


class DeleteUser(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, id):
        return delete_user_mutation(root, info, id)


class CreatePost(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String()
        user_id = graphene.Int(required=True)

    post = graphene.Field(lambda: Post)

    @staticmethod
    def mutate(root, info, title, content=None, user_id=None):
        return create_post_mutation(root, info, title, content, user_id)


class UpdatePost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        content = graphene.String()

    post = graphene.Field(lambda: Post)

    @staticmethod
    def mutate(root, info, id, title=None, content=None):
        return update_post_mutation(root, info, id, title, content)


class DeletePost(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, id):
        return delete_post_mutation(root, info, id)


class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()
    create_post = CreatePost.Field()
    update_post = UpdatePost.Field()
    delete_post = DeletePost.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)