import pytest
from httpx import AsyncClient

from app.config import settings
from app.database import get_db_session, Base, engine
from app.models.user import User
from app.models.post import Post
from app.__init__ import app


@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(autouse=True)
async def seed_data(db_session):
    user = User(username="alice", email="alice@example.com")
    db_session.add(user)
    await db_session.flush()
    post1 = Post(title="First", content="Hello World", author_id=user.id)
    post2 = Post(title="Second", content="Another Post", author_id=user.id)
    db_session.add_all([post1, post2])
    await db_session.commit()


@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_get_user_by_username(client):
    query = """
    query GetUser($username: String!) {
      user(username: $username) {
        id
        username
        email
        posts {
          title
          content
        }
      }
    }
    """
    variables = {"username": "alice"}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()["data"]
    user_data = data["user"]
    assert user_data["username"] == "alice"
    assert user_data["email"] == "alice@example.com"
    posts = user_data["posts"]
    assert len(posts) == 2
    titles = {p["title"] for p in posts}
    assert {"First", "Second"} == titles


@pytest.mark.asyncio
async def test_get_post_by_id(client):
    query = """
    query GetPost($id: Int!) {
      post(id: $id) {
        id
        title
        content
        author {
          username
        }
      }
    }
    """
    variables = {"id": 1}
    response = await client.post("/graphql", json={"query": query, "variables": variables})
    assert response.status_code == 200
    data = response.json()["data"]
    post_data = data["post"]
    assert post_data["title"] == "First"
    assert post_data["author"]["username"] == "alice"


@pytest.mark.asyncio
async def test_create_user_mutation(client):
    mutation = """
    mutation CreateUser($username: String!, $email: String!) {
      createUser(username: $username, email: $email) {
        id
        username
        email
      }
    }
    """
    variables = {"username": "bob", "email": "bob@example.com"}
    response = await client.post("/graphql", json={"query": mutation, "variables": variables})
    assert response.status_code == 200
    data = response.json()["data"]
    user_data = data["createUser"]
    assert user_data["username"] == "bob"
    assert user_data["email"] == "bob@example.com"


@pytest.mark.asyncio
async def test_create_post_mutation(client):
    mutation = """
    mutation CreatePost($title: String!, $content: String!, $authorId: Int!) {
      createPost(title: $title, content: $content, authorId: $authorId) {
        id
        title
        content
        author {
          username
        }
      }
    }
    """
    variables = {"title": "New Post", "content": "Content here", "authorId": 1}
    response = await client.post("/graphql", json={"query": mutation, "variables": variables})
    assert response.status_code == 200
    data = response.json()["data"]
    post_data = data["createPost"]
    assert post_data["title"] == "New Post"
    assert post_data["author"]["username"] == "alice"


@pytest.mark.asyncio
async def test_invalid_user_query(client):
    query = """
    query {
      user(username: "nonexistent") {
        id
      }
    }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    errors = response.json().get("errors")
    assert errors is not None
    assert any("not found" in e["message"] for e in errors)


@pytest.mark.asyncio
async def test_invalid_post_query(client):
    query = """
    query {
      post(id: 999) {
        id
      }
    }
    """
    response = await client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    errors = response.json().get("errors")
    assert errors is not None
    assert any("not found" in e["message"] for e in errors)