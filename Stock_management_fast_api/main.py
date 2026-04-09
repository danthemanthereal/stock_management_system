from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from database.db import engine, SessionLocal
from sqlalchemy.orm import Session
from database import models
from youtube_transcript_component.yt_transcript_component import \
    get_youtube_transcript_based_url
from gemini_component.gemini_llm_component import get_summary_of_gemini_with_url_context, \
    get_summary_of_gemini_of_transcript
import json
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests

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


@app.post("/get-yt-transcript", response_class=HTMLResponse)
def get_yt_transcript(request: Request, video_id: str = Form(...)):
    transcript = get_youtube_transcript_based_url(video_id)
    companies_array = get_summary_of_gemini_of_transcript(transcript)
    print(companies_array)
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
    print(company)
    db_company = models.StockSummary(
        name=company.company_name,
        strength=company.strength,
        weakness=company.weakness
    )

    db.add(db_company)
    db.commit()
    db.refresh(db_company)

    return {"message": "Company gespeichert!", "id": db_company.id}

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

@app.post("/find-potential-stocks")
def scrape_tradingview(db: Session = Depends(get_db)):
    url = "https://scanner.tradingview.com/america/scan?label-product=screener-stock"

    payload = {
        "columns": [
            "ticker-view", "close", "market_cap_basic",
            "price_earnings_ttm", "market"
            "sector", "AnalystRating", "AnalystRating.tr"
        ],
        "filter": [
            {"left": "close", "operation": "in_range", "right": [10, 100]}
        ],
        "markets": ["america"],
        "options": {"lang": "en"},
        "range": [0, 20],
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
        sector = current_stock_info[4]
        country = current_stock_info[5]
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







    print(potential_stocks[0])
    return RedirectResponse(url="/", status_code=303)
