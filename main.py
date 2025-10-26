from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.middleware.sessions import SessionMiddleware

from database import SessionLocal
from models import User, Game, UserInGame
from auth import hash_password, verify_password

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="supersecretkey123")

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """
    Home page. For now, no login yet.
    """
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/register", response_class=HTMLResponse)
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register")
def register(
    username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)
):
    """
    Handle registration form submission
    """
    # Basic validation
    if len(password) < 8:
        raise HTTPException(
            status_code=400, detail="Password must be at least 8 characters"
        )

    # Check if username already exists
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")

    try:
        # Hash the password using direct bcrypt
        hashed_pw = hash_password(password)
    except Exception as e:
        print(f"Password hashing error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")

    try:
        # Create a new user
        user = User(username=username, hashed_password=hashed_pw)
        db.add(user)
        db.commit()

        return RedirectResponse(url="/login", status_code=303)
    except Exception as e:
        db.rollback()
        print(f"Registration error: {e}")
        raise HTTPException(status_code=500, detail="Registration failed")


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    request: Request = None,
):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    # Store login session
    request.session["user_id"] = user.id
    request.session["username"] = user.username

    return RedirectResponse(url="/dashboard", status_code=303)


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@app.get("/dashboard", response_class=HTMLResponse)
def games_page(request: Request, db: Session = Depends(get_db)):
    """
    Page showing available games to join or option to create a new one.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    games = db.query(Game).all()  # all games for now
    return templates.TemplateResponse(
        "dashboard.html", {"request": request, "games": games, "user_id": user_id}
    )


@app.post("/games/create")
def create_game(name: str = Form(...), db: Session = Depends(get_db), request: Request = None):
    user_id = request.session.get("user_id")
    if not user_id:
        return RedirectResponse(url="/login", status_code=303)

    # Check if name already exists
    if db.query(Game).filter(Game.name == name).first():
        raise HTTPException(status_code=400, detail="Game name already exists")

    game = Game(name=name)
    db.add(game)
    db.commit()
    db.refresh(game)

    # Auto-join the creator to the game
    uig = UserInGame(user_id=user_id, game_id=game.id)
    db.add(uig)
    db.commit()

    return RedirectResponse(url="/games", status_code=303)


@app.post("/games/join/{game_id}")
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

    return RedirectResponse(url="/games", status_code=303)

