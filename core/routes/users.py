from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.schemas import user as schemas
from core.crud import user as crud
from core.dependencies import get_database_session
from core.config import settings
from jose import JWTError, jwt
from passlib.context import CryptContext

router = APIRouter()

# JWT Authentication setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify that a plain password matches the hashed password.

    Args:
        plain_password (str): The plain text password to check.
        hashed_password (str): The hashed password to check against.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Generate a hashed version of the given password.

    Args:
        password (str): The plain text password to hash.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token with the given data.

    Args:
        data (dict): The data to include in the token.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_database_session)
) -> schemas.User:
    """
    Retrieve the current user based on the provided JWT token.

    Args:
        token (str): The JWT token to decode and verify.
        db (Session): The database session to use for user lookup.

    Returns:
        User: The user object if the token is valid, otherwise raises an HTTPException.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    
    except JWTError:
        raise credentials_exception
    
    user = crud.get_user_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/token", response_model=schemas.Token)
def login_for_access_token(
    db: Session = Depends(get_database_session),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict:
    """
    Authenticate a user and provide an access token.

    Args:
        db (Session): The database session to use for user authentication.
        form_data (OAuth2PasswordRequestForm): The form data containing username and password.

    Returns:
        dict: The access token and token type if authentication is successful.
    """
    user = crud.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/users/", response_model=schemas.User)
def create_user(
    user: schemas.UserCreate, db: Session = Depends(get_database_session)
) -> schemas.User:
    """
    Register a new user in the system.

    Args:
        user (UserCreate): The user data for the new user.
        db (Session): The database session to use for user creation.

    Returns:
        User: The newly created user object.

    Raises:
        HTTPException: If the email is already registered.
    """
    hashed_password = get_password_hash(user.password)
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user, hashed_password=hashed_password)
