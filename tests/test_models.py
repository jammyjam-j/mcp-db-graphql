import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adjust path to import application modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.database import Base
from app.models.user import User
from app.models.post import Post


@pytest.fixture(scope="session")
def engine():
    return create_engine("sqlite:///:memory:", echo=False)


@pytest.fixture(scope="session")
def tables(engine):
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def session(engine, tables):
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_user_creation(session):
    user = User(username="alice", email="alice@example.com")
    session.add(user)
    session.commit()
    retrieved = session.query(User).filter_by(username="alice").one()
    assert retrieved.email == "alice@example.com"
    assert retrieved.id is not None


def test_user_uniqueness_constraints(session):
    user1 = User(username="bob", email="bob@example.com")
    session.add(user1)
    session.commit()
    with pytest.raises(Exception):
        duplicate = User(username="bob", email="bob@other.com")
        session.add(duplicate)
        session.commit()


def test_post_creation_and_relationship(session):
    user = User(username="charlie", email="charlie@example.com")
    session.add(user)
    session.flush()
    post1 = Post(title="First Post", content="Hello World!", author_id=user.id)
    post2 = Post(title="Second Post", content="Another entry", author_id=user.id)
    session.add_all([post1, post2])
    session.commit()
    retrieved_user = session.query(User).filter_by(username="charlie").one()
    assert len(retrieved_user.posts) == 2
    titles = {p.title for p in retrieved_user.posts}
    assert titles == {"First Post", "Second Post"}


def test_post_deletion_cascade(session):
    user = User(username="dave", email="dave@example.com")
    session.add(user)
    session.flush()
    post = Post(title="To be deleted", content="Delete me", author_id=user.id)
    session.add(post)
    session.commit()
    session.delete(user)
    session.commit()
    remaining_posts = session.query(Post).filter_by(author_id=user.id).all()
    assert len(remaining_posts) == 0


def test_user_repr(session):
    user = User(username="eve", email="eve@example.com")
    session.add(user)
    session.commit()
    retrieved = session.query(User).first()
    assert repr(retrieved) == f"<User id={retrieved.id} username=EVE>"


def test_post_repr(session):
    user = User(username="frank", email="frank@example.com")
    session.add(user)
    session.flush()
    post = Post(title="Sample", content="Content", author_id=user.id)
    session.add(post)
    session.commit()
    retrieved = session.query(Post).first()
    assert repr(retrieved) == f"<Post id={retrieved.id} title=SAMPLE>"


def test_email_validation(session):
    with pytest.raises(ValueError):
        User(username="invalid", email="not-an-email")


def test_username_length_constraint(session):
    long_username = "x" * 256
    with pytest.raises(ValueError):
        User(username=long_username, email="valid@example.com")


def test_post_content_non_empty(session):
    user = User(username="george", email="george@example.com")
    session.add(user)
    session.flush()
    with pytest.raises(ValueError):
        Post(title="No Content", content="", author_id=user.id)


def test_query_filters(session):
    users = [
        User(username="hannah", email="hannah1@example.com"),
        User(username="hannah", email="hannah2@example.com"),
        User(username="ian", email="ian@example.com")
    ]
    session.add_all(users)
    session.commit()
    results = session.query(User).filter_by(username="hannah").all()
    assert len(results) == 2
    emails = {u.email for u in results}
    assert emails == {"hannah1@example.com", "hannah2@example.com"}


def test_post_ordering(session):
    user = User(username="jack", email="jack@example.com")
    session.add(user)
    session.flush()
    titles = ["B", "A", "C"]
    posts = [Post(title=t, content="c", author_id=user.id) for t in titles]
    session.add_all(posts)
    session.commit()
    ordered = session.query(Post).order_by(Post.title.asc()).all()
    assert [p.title for p in ordered] == ["A", "B", "C"]


def test_pagination(session):
    user = User(username="kate", email="kate@example.com")
    session.add(user)
    session.flush()
    for i in range(10):
        session.add(Post(title=f"Post {i}", content="x", author_id=user.id))
    session.commit()
    first_page = session.query(Post).order_by(Post.id).limit(3).all()
    second_page = session.query(Post).order_by(Post.id).offset(3).limit(3).all()
    assert len(first_page) == 3
    assert len(second_page) == 3
    assert first_page[0].title == "Post 0"
    assert second_page[0].title == "Post 3"


def test_update_user_email(session):
    user = User(username="leo", email="leo@example.com")
    session.add(user)
    session.commit()
    user.email = "new@leodomain.com"
    session.commit()
    updated = session.query(User).filter_by(id=user.id).one()
    assert updated.email == "new@leodomain.com"


def test_update_post_title(session):
    user = User(username="mia", email="mia@example.com")
    session.add(user)
    session.flush()
    post = Post(title="Old Title", content="content", author_id=user.id)
    session.add(post)
    session.commit()
    post.title = "New Title"
    session.commit()
    updated = session.query(Post).filter_by(id=post.id).one()
    assert updated.title == "New Title"


def test_soft_delete_flag(session):
    user = User(username="nina", email="nina@example.com")
    session.add(user)
    session.commit()
    user.is_active = False
    session.commit()
    inactive_user = session.query(User).filter_by(id=user.id, is_active=False).one()
    assert inactive_user.username == "NINA"


def test_query_exclusion_of_inactive(session):
    active = User(username="oliver", email="oliver@example.com")
    inactive = User(username="peter", email="peter@example.com", is_active=False)
    session.add_all([active, inactive])
    session.commit()
    results = session.query(User).filter_by(is_active=True).all()
    assert len(results) == 1
    assert results[0].username == "OLIVER"


def test_bulk_insertion(session):
    users = [User(username=f"user{i}", email=f"user{i}@example.com") for i in range(5)]
    session.bulk_save_objects(users)
    session.commit()
    count = session.query(User).count()
    assert count >= 5


def test_transaction_rollback(session):
    user1 = User(username="q", email="q@example.com")
    session.add(user1)
    session.flush()
    try:
        user2 = User(username="q", email="duplicate@example.com")
        session.add(user2)
        session.commit()
    except Exception:
        session.rollback()
    remaining = session.query(User).filter_by(username="q").count()
    assert remaining == 1


def test_relationship_backref(session):
    user = User(username="ram", email="ram@example.com")
    session.add(user)
    session.flush()
    post = Post(title="Backref Test", content="content", author=user)
    session.add(post)
    session.commit()
    retrieved_user = session.query(User).filter_by(id=user.id).one()
    assert len(retrieved_user.posts) == 1
    assert retrieved_user.posts[0].title == "BACKREF TEST"