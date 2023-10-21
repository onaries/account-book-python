import os
from fastapi import FastAPI, Form, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_pagination import add_pagination
from sqlalchemy import event
from app.routes import router as api_router
from fastapi.middleware.cors import CORSMiddleware
from models import MainCategory, Category
from database import get_db
from pytz import timezone
from init import init, create_account_card_list, create_asset_list, create_loan_list

app = FastAPI()
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("", StaticFiles(directory="static", html=True), name="static")
templates = Jinja2Templates(directory="static")


@app.get("/")
async def serve_spa(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/{full_path:path}")
async def catch_all(request: Request, full_path: str):
    return templates.TemplateResponse("index.html", {"request": request})


@app.on_event("startup")
async def startup():
    db = next(get_db())
    if os.environ.get("ENV") != "test" and db.query(MainCategory).count() == 0:
        init(db)

        create_account_card_list(db)
        create_asset_list(db)
        create_loan_list(db)


@app.middleware("http")
async def add_timeout_header(request, call_next):
    timezone_name = "Asia/Seoul"
    timezone_obj = timezone(timezone_name)
    request.state.timezone = timezone_obj
    response = await call_next(request)
    return response


add_pagination(app)
