from sqlalchemy.orm import Session
from core.models.user import User
from core.schemas.user import UserCreate


def get_user_by_username(db: Session, username: str):
    """
    Retrieve a user from the database by their username.

    Args:
        db (Session): The database session to use for the operation.
        username (str): The username of the user to retrieve.

    Returns:
        User or None: The user object if found, otherwise None.
    """
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str):
    """
    Retrieve a user from the database by their email address.

    Args:
        db (Session): The database session to use for the operation.
        email (str): The email address of the user to retrieve.

    Returns:
        User or None: The user object if found, otherwise None.
    """
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, user: UserCreate, hashed_password: str):
    """
    Create a new user in the database.

    Args:
        db (Session): The database session to use for the operation.
        user (UserCreate): The user data used to create the new user.
        hashed_password (str): The hashed password for the new user.

    Returns:
        User: The newly created user object with all its attributes.
    """
    db_user = User(
        username=user.username, email=user.email, hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
