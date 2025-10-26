from fastapi import APIRouter, Form, Depends, Request, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from models import Game, UserInGame
from dependencies import get_db

router = APIRouter()

@router.post("/games/create")
def create_game(name: str = Form(...), db: Session = Depends(get_db), request: Request = None):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse("/login", status_code=303)
    if db.query(Game).filter(Game.name == name).first():
        raise HTTPException(400, "Game name exists")
    game = Game(name=name)
    db.add(game)
    db.commit()
    db.refresh(game)
    db.add(UserInGame(user_id=user_id, game_id=game.id))
    db.commit()
    return RedirectResponse("/dashboard", 303)


@router.post("/games/join/{game_id}")
def join_game(game_id: int, db: Session = Depends(get_db), request: Request = None):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    # Check if already in the game
    existing = db.query(UserInGame).filter_by(user_id=user_id, game_id=game_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Already joined this game")

    uig = UserInGame(user_id=user_id, game_id=game_id)
    db.add(uig)
    db.commit()

    return RedirectResponse(url="/dashboard", status_code=303)