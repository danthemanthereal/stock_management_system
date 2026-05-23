from uuid import UUID

from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from collections import defaultdict
from typing import List, Tuple, Optional
from finvizfinance.screener.overview import Overview

import traceback
from src.combining_stock_infos_llm.combine_stock import get_combination
from src.evaluation_component.evaluation import evaluate_new_information
from src.financial_metric_evaluator_component.financial_metric_evaluator import \
    get_satisfied_and_not_satisfied_financial_metrics
from src.database.models import FinancialMetric, IndustryProfile, ProfileMetricConfiguration, FinancialMetricCategory, \
    BoughtStock, StockSummary, User
from src.financial_metric_component.financial_metric import get_total_financial_metrics
from src.database.db import engine, SessionLocal
from sqlalchemy.orm import Session, joinedload
from src.database import models
from src.youtube_transcript_component.yt_transcript_component import \
    get_youtube_transcript_based_url
from src.summary_llm_component.gemini_llm_component import get_summary_of_gemini_with_url_context, \
    get_summary_of_gemini_of_transcript
import json
import re
from starlette.middleware.sessions import SessionMiddleware
import numpy as np
import pandas as pd
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
from pytube import extract
from itertools import groupby
from datetime import datetime, timedelta
from gnews import GNews
from dotenv import load_dotenv
import os
from src.authenticator_component.views import authentication_router
from src.authenticator_component.authenticator import get_current_user_id
from src.core.rate_limit import configure_rate_limit
from src.database.db import get_db

load_dotenv()

models.Base.metadata.create_all(bind=engine)


class BoughtStockCreate(BaseModel):
    name: str
    amount: float
    bought_price: float

    class Config:
        from_attributes = True


class SummaryRequest(BaseModel):
    url: str


app = FastAPI()

origins = [
    "*"
]

templates = Jinja2Templates(directory="templates")


app.include_router(authentication_router)

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

