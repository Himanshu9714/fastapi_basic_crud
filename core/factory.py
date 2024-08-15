from core.config import Settings
from fastapi import FastAPI
from core.routes import books, users
from core.db.base import Base


def create_app(settings: Settings):
    app = FastAPI(title="Core")
    setup_routes(app)
    
    from core.db.session import engine
    Base.metadata.create_all(bind=engine)
    
    return app


def setup_routes(app: FastAPI):
    app.include_router(books.router, prefix="/books", tags=["books"])
    app.include_router(users.router, prefix="/users", tags=["users"])