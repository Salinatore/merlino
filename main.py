from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from routers import auth, dashboard, games

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecretkey123")
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(games.router)

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    """
    Home page. For now, no login yet.
    """
    return templates.TemplateResponse("home.html", {"request": request})