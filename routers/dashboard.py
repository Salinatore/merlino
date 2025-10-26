from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from models import Game
from dependencies import get_db, templates

router = APIRouter()

@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    games = db.query(Game).all()
    return templates.TemplateResponse("dashboard.html", {"request": request, "games": games})
