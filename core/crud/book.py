from sqlalchemy.orm import Session
from core.models.book import Book
from core.schemas.book import BookCreate, BookUpdate


def create_book(db: Session, book: BookCreate, user_id: int):
    """
    Create a new book entry in the database.

    Args:
        db (Session): The database session to use for the operation.
        book (BookCreate): The data required to create a new book.
        user_id (int): The ID of the user who is the author of the book.

    Returns:
        Book: The newly created book object with all its attributes.
    """
    db_book = Book(**book.dict(), author_id=user_id)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book


def get_books_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 10):
    """
    Retrieve a list of books created by a specific user.

    Args:
        db (Session): The database session to use for the operation.
        user_id (int): The ID of the user whose books are being queried.
        skip (int, optional): The number of records to skip. Defaults to 0.
        limit (int, optional): The maximum number of records to return. Defaults to 10.

    Returns:
        List[Book]: A list of book objects created by the specified user.
    """
    return (
        db.query(Book)
        .filter(Book.author_id == user_id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_book(db: Session, book_id: int, user_id: int):
    """
    Retrieve a specific book by its ID, ensuring it belongs to the current user.

    Args:
        db (Session): The database session to use for the operation.
        book_id (int): The ID of the book to retrieve.
        user_id (int): The ID of the user to whom the book must belong.

    Returns:
        Book or None: The book object if found, otherwise None.
    """
    return db.query(Book).filter(Book.id == book_id, Book.author_id == user_id).first()


def delete_book(db: Session, book_id: int, user_id: int):
    """
    Delete a specific book by its ID, ensuring it belongs to the current user.

    Args:
        db (Session): The database session to use for the operation.
        book_id (int): The ID of the book to delete.
        user_id (int): The ID of the user to whom the book must belong.

    Returns:
        Book or None: The deleted book object if found and deleted, otherwise None.
    """
    db_book = (
        db.query(Book).filter(Book.id == book_id, Book.author_id == user_id).first()
    )
    if db_book:
        db.delete(db_book)
        db.commit()
    return db_book


def update_book_status(db: Session, book: Book, book_update: BookUpdate):
    """
    Update the status (and optionally the title) of a specific book.

    Args:
        db (Session): The database session to use for the operation.
        book (Book): The existing book object to be updated.
        book_update (BookUpdate): The updated data for the book, including new status and optionally a new title.

    Returns:
        Book: The updated book object with refreshed attributes.
    """
    if book_update.title:
        book.title = book_update.title
    book.status = book_update.status
    db.commit()
    db.refresh(book)
    return book
