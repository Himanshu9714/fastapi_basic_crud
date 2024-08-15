from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.crud import book as crud
from core.schemas import book as schemas
from core.schemas.user import User as UserSchema
from core.routes.users import get_current_user
from core.dependencies import get_database_session
from typing import List

router = APIRouter()


@router.post("/", response_model=schemas.Book)
def create_book(
    book: schemas.BookCreate,
    db: Session = Depends(get_database_session),
    current_user: UserSchema = Depends(get_current_user),
):
    """
    Create a new book.

    - **title**: The title of the book you are reading
    - **status**: The reading status of the book (`read` or `to_read`)

    Returns the newly created book.
    """
    return crud.create_book(db=db, book=book, user_id=current_user.id)


@router.get("/", response_model=List[schemas.Book])
def read_books(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_database_session),
    current_user: UserSchema = Depends(get_current_user),
):
    """
    Retrieve a list of books belonging to the current user.

    - **skip**: Number of items to skip.
    - **limit**: Maximum number of items to return.

    Returns a list of books.
    """
    books = crud.get_books_by_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return books


@router.get("/{book_id}", response_model=schemas.Book)
def read_book(
    book_id: int,
    db: Session = Depends(get_database_session),
    current_user: UserSchema = Depends(get_current_user),
):
    """
    Retrieve details of a specific book by its ID for the current user.

    - **book_id**: The ID of the book to retrieve.

    Returns the book details if found, otherwise raises a 404 error.
    """
    book = crud.get_book(db=db, book_id=book_id, user_id=current_user.id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.delete("/{book_id}", response_model=schemas.Book)
def delete_book(
    book_id: int,
    db: Session = Depends(get_database_session),
    current_user: UserSchema = Depends(get_current_user),
):
    """
    Delete a specific book by its ID for the current user.

    - **book_id**: The ID of the book to delete.

    Returns the deleted book details if successful, otherwise raises a 404 error.
    """
    book = crud.delete_book(db=db, book_id=book_id, user_id=current_user.id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book


@router.put("/{book_id}", response_model=schemas.Book)
def update_book_status(
    book_id: int,
    book_update: schemas.BookUpdate,
    db: Session = Depends(get_database_session),
    current_user: UserSchema = Depends(get_current_user),
):
    """
    Update the status of a specific book by its ID for the current user.

    - **book_id**: The ID of the book to update.
    - **status**: The new reading status of the book.

    Returns the updated book details if successful, otherwise raises a 404 error.
    """
    book = crud.get_book(db=db, book_id=book_id, user_id=current_user.id)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    updated_book = crud.update_book_status(db=db, book=book, book_update=book_update)
    return updated_book
