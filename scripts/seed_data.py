import logging
import sys
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from app.database import engine
from app.models.user import User
from app.models.post import Post

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def seed_users(session):
    users_data = [
        {"username": "alice", "email": "alice@example.com"},
        {"username": "bob", "email": "bob@example.com"},
        {"username": "carol", "email": "carol@example.com"},
    ]
    users = []
    for data in users_data:
        user = User(**data)
        session.add(user)
        users.append(user)
    return users


def seed_posts(session, users):
    posts_data = [
        {
            "title": "Hello World",
            "content": "This is the first post.",
            "author_id": users[0].id,
        },
        {
            "title": "Second Post",
            "content": "More content here.",
            "author_id": users[1].id,
        },
        {
            "title": "Carol's Thoughts",
            "content": "Thoughts by Carol.",
            "author_id": users[2].id,
        },
    ]
    posts = []
    for data in posts_data:
        post = Post(**data)
        session.add(post)
        posts.append(post)
    return posts


def seed():
    logger.info("Starting database seeding process.")
    try:
        session = SessionLocal()
        session.execute("SELECT 1")
        logger.debug("Database connection verified.")
    except SQLAlchemyError as exc:
        logger.error(f"Failed to connect to the database: {exc}")
        sys.exit(1)

    try:
        logger.info("Creating tables if they do not exist.")
        engine.begin()  # ensure a transactional context
        User.__table__.create(bind=engine, checkfirst=True)
        Post.__table__.create(bind=engine, checkfirst=True)

        logger.info("Inserting users.")
        users = seed_users(session)

        logger.info("Committing user inserts.")
        session.commit()

        logger.info("Fetching fresh user instances with IDs.")
        session.refresh(users[0])
        session.refresh(users[1])
        session.refresh(users[2])

        logger.info("Inserting posts.")
        seed_posts(session, users)

        logger.info("Committing post inserts.")
        session.commit()
        logger.info("Database seeding completed successfully.")
    except SQLAlchemyError as exc:
        logger.error(f"An error occurred during seeding: {exc}")
        session.rollback()
        sys.exit(1)
    finally:
        session.close()


if __name__ == "__main__":
    seed()