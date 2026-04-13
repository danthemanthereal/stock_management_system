from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from database.models import FinancialMetric
from financial_metric_component.financial_metric import get_financial_metrics_by_guro_focus
from database.db import engine, SessionLocal
from sqlalchemy.orm import Session
from database import models
from youtube_transcript_component.yt_transcript_component import \
    get_youtube_transcript_based_url
from summary_llm_component.gemini_llm_component import get_summary_of_gemini_with_url_context, \
    get_summary_of_gemini_of_transcript
import json
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
from pytube import extract

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

origins = [
   "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # oder ["*"] zum Testen
    allow_credentials=True,
    allow_methods=["*"],     # wichtig für OPTIONS!
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Company(BaseModel):
    company_name: str
    strength: str
    weakness: str
@app.get("/")
def read_root(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )

@app.post("/get-summary", response_class=HTMLResponse)
async def analyze(request: Request, url: str = Form(...)):

    companies_array = get_summary_of_gemini_with_url_context(url)

    if isinstance(companies_array, str):
        try:
            companies_array = json.loads(companies_array)
        except json.JSONDecodeError:
            companies_array = []

    return templates.TemplateResponse(
        request=request,
        name="companies_overview.html",
        context={"request": request, "companies": companies_array}
    )


def extract_video_id_by_url(url: str) ->str:
    return extract.video_id(url)
@app.post("/get-yt-transcript", response_class=HTMLResponse)
def get_yt_transcript(request: Request, url : str = Form(...)):
    video_id = extract_video_id_by_url(url)
    transcript = get_youtube_transcript_based_url(video_id)
    companies_array = get_summary_of_gemini_of_transcript(transcript)

    if isinstance(companies_array, str):
        try:
            companies_array = json.loads(companies_array)
        except json.JSONDecodeError:
            companies_array = []

    return templates.TemplateResponse(
        request=request,
        name="companies_overview.html",
        context={"request": request, "companies": companies_array}
    )


@app.post("/companies")
async def receive_company(company: Company, db: Session = Depends(get_db)):
    db_company = db.query(models.StockSummary).filter_by(name=company.company_name).first()

    if db_company:
        if company.strength:
            if db_company.strength:
                db_company.strength += f" • {company.strength}"
            else:
                db_company.strength = company.strength

        if company.weakness:
            if db_company.weakness:
                db_company.weakness += f" • {company.weakness}"
            else:
                db_company.weakness = company.weakness

        db.commit()
        db.refresh(db_company)
        return {"message": "Firma aktualisiert!", "id": db_company.id}

    else:
        db_company = models.StockSummary(
            name=company.company_name,
            strength=company.strength,
            weakness=company.weakness
        )
        db.add(db_company)
        db.commit()
        db.refresh(db_company)
        return {"message": "Firma gespeichert!", "id": db_company.id}

@app.get("/success", response_class=HTMLResponse)
async def success_page(request: Request):
    return templates.TemplateResponse(
         request=request,
        name="success.html",
        context={"request": request}
    )


@app.get("/saved-companies", response_class=HTMLResponse)
def show_companies(request: Request, db: Session = Depends(get_db)):
    companies = db.query(models.StockSummary).all()

    return templates.TemplateResponse(request=request,
         name="saved_companies_overview.html",
         context={"request": request, "companies": companies
    })

@app.post("/find-potential-stocks", response_class=HTMLResponse)
def scrape_tradingview(request: Request):
    url = "https://scanner.tradingview.com/america/scan?label-product=screener-stock"

    payload = {
        "columns": [
            "ticker-view", "close", "market_cap_basic",
            "price_earnings_ttm", "market",
            "sector", "AnalystRating", "AnalystRating.tr"
        ],
        "filter": [
            {"left": "close", "operation": "in_range", "right": [10, 100]}, # stock price filter
            {"left": "AnalystRating", "operation": "in_range", "right": ["Buy", "StrongBuy"]},
            {"left": "Perf.YTD", "operation": "greater", "right": 10}, # Performance of the year
            {"left": "return_on_equity_fq", "operation": "in_range", "right": [20,30]},  # return on equity filter r
            {"left": "sector", "operation": "in_range", "right": [""]},  # welche Sektroren betrachtet werden
            {"left": "total_revenue_yoy_growth_ttm", "operation": "greater", "right": 10},  # Performance von umsatzwachstum
        ],
        "markets": ["america"], # filter für betrachtende länder
        "options": {"lang": "en"},
        "range": [0, 100],
        "sort": {"sortBy": "market_cap_basic", "sortOrder": "desc"}
    }

    response = requests.post(url, json=payload)
    data = response.json()

    potential_stocks = []
    for item in data["data"]:
        current_stock_info = item["d"]

        name = current_stock_info[0]["description"]
        price = current_stock_info[1]
        market_cap = current_stock_info[2]
        p_e_rating = current_stock_info[3]
        country = current_stock_info[4]
        sector = current_stock_info[5]
        analyst_rating = current_stock_info[6]
        analyst_rating_tr = current_stock_info[7]
        potential_stocks.append({
            'name': name,
            'price': price,
            'market_cap': market_cap,
            'sector': sector,
            'country': country,
            'p_e_rating': p_e_rating,
            'analyst_rating': analyst_rating,
            'analyst_rating_tr': analyst_rating_tr
        })

    return templates.TemplateResponse(request=request,
                                      name="show-potential-stocks.html",
                                      context={"request": request, "stocks": potential_stocks
    })


@app.post("/get-financial-metrics", response_class=HTMLResponse)
def get_financial_metrics_by_guro_focus_end_point(request: Request, company: str = Form(...), db: Session = Depends(get_db)):
    financial_metrics_map = get_financial_metrics_by_guro_focus(company, db)

    years = ["2022", "2023", "2024", "2025"]

    return templates.TemplateResponse(
        request=request,
        name="show_financial_metrics.html",
        context=
        {
            "request": request,
            "data": financial_metrics_map,
            "years": years
        })

@app.post("/show-saved-financial-metrics", response_class=HTMLResponse)
def show_saved_financial_metrics_page(request: Request, db: Session = Depends(get_db)):
    metrics = db.query(models.FinancialMetric).all()
    return templates.TemplateResponse(
    request=request,
        name="show_saved_financial_metrics.html",
        context={
            "request": request,
            "metrics": metrics
        }
    )

@app.post("/metrics/create", response_class=HTMLResponse)
def create_metric(
    request: Request,
    name: str = Form(...),
    should_rise: bool = Form(False),
    reference_value: int = Form(...),
    unit: str = Form(...),
    db: Session = Depends(get_db)
):
    metric = FinancialMetric(
        name=name,
        should_rise=should_rise,
        reference_value=reference_value,
        unit=unit
    )

    db.add(metric)
    db.commit()
    db.refresh(metric)

    metrics = db.query(models.FinancialMetric).all()
    return templates.TemplateResponse(
        request=request,
        name="show_saved_financial_metrics.html",
        context={
            "request": request,
            "metrics": metrics
        }
    )

@app.post("/metrics/update/{metric_id}", response_class=HTMLResponse)
def update_metric(
    request: Request,
    metric_id: int,
    name: str = Form(...),
    should_rise: bool = Form(False),
    reference_value: int = Form(...),
    unit: str = Form(...),
    db: Session = Depends(get_db)
):
    metric = db.query(FinancialMetric).filter(FinancialMetric.id == metric_id).first()

    metric.name = name
    metric.should_rise = should_rise
    metric.reference_value = reference_value
    metric.unit = unit

    db.commit()

    metrics = db.query(models.FinancialMetric).all()
    return templates.TemplateResponse(
        request=request,
        name="show_saved_financial_metrics.html",
        context={
            "request": request,
            "metrics": metrics
        }
    )

@app.get("/metrics/edit/{metric_id}")
def edit_metric_page(metric_id: int, request: Request, db: Session = Depends(get_db)):
    metric = db.query(FinancialMetric).filter(FinancialMetric.id == metric_id).first()

    return templates.TemplateResponse(
        request=request,
        name ="edit_metric.html",
        context={"request": request, "metric": metric}
    )

@app.post("/metrics/delete/{metric_id}")
def delete_metric(
        request: Request,
        metric_id: int, db: Session = Depends(get_db)):
    metric = db.query(FinancialMetric).filter(FinancialMetric.id == metric_id).first()

    db.delete(metric)
    db.commit()


    metrics = db.query(models.FinancialMetric).all()
    return templates.TemplateResponse(
    request=request,
    name="show_saved_financial_metrics.html",
    context={
        "request": request,
        "metrics": metrics
        }
    )
