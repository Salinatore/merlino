from database import SessionLocal
from fastapi.templating import Jinja2Templates


templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
