from uuid import UUID

from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import List, Tuple, Optional
from src.database.models import FinancialMetric, IndustryProfile, ProfileMetricConfiguration, FinancialMetricCategory, \
    BoughtStock, StockSummary, User
from src.database.db import engine, SessionLocal
from sqlalchemy.orm import Session
from src.database import models

from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from src.authenticator_component.views import authentication_router
from src.authenticator_component.authenticator import get_current_user_id
from src.core.rate_limit import configure_rate_limit
from src.database.db import get_db
from src.portfolio_component.views import portfolio_router
from src.watchlist_component.views import watchlist_router
from src.analysis_component.views import analysis_router
from src.bought_stock_component.views import bought_stock_router

load_dotenv()

models.Base.metadata.create_all(bind=engine)




class SummaryRequest(BaseModel):
    url: str


app = FastAPI()

origins = [
    "*"
]

templates = Jinja2Templates(directory="templates")


app.include_router(authentication_router)
app.include_router(portfolio_router)
app.include_router(watchlist_router)
app.include_router(analysis_router)
app.include_router(bought_stock_router)

configure_rate_limit(app)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SECRET_KEY"),
    session_cookie="sid",
    max_age=86400,
    same_site="lax",
    https_only=False
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def show_index_page(request: Request, user: Optional[UUID] = Depends(get_current_user_id)):
    try:

        return templates.TemplateResponse(
            request=request,
            name="index.html", context={
                "request": request,
                "user": user
            })
    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            request=request,
            name="error.html"
        )

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=303)


@app.get("/success", response_class=HTMLResponse)
async def success_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="success.html",
        context={"request": request}
    )










