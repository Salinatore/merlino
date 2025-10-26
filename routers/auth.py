from fastapi import APIRouter, Form, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from models import User
from auth_utils import hash_password, verify_password
from dependencies import get_db, templates

router = APIRouter()

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
def register(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password too short")
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username exists")

    user = User(username=username, hashed_password=hash_password(password))
    db.add(user)
    db.commit()
    return RedirectResponse("/login", status_code=303)

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
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


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)
