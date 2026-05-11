from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from collections import defaultdict
from typing import List, Tuple
from combining_stock_infos_llm.combine_stock import get_combination
from financial_metric_evaluator_component.financial_metric_evaluator import \
    get_satisfied_and_not_satisfied_financial_metrics
from database.models import FinancialMetric
from financial_metric_component.financial_metric import get_total_financial_metrics
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


def group_financial_metrics_by_category(
    metrics: List[FinancialMetric],
) -> List[Tuple[str, List[FinancialMetric]]]:
    try:
        groups: dict[str, List[FinancialMetric]] = defaultdict(list)
        for m in metrics:
            raw = (m.category or "").strip()
            key = raw if raw else ""
            groups[key].append(m)
        ordered_keys = sorted(
            groups.keys(),
            key=lambda k: (1 if k == "" else 0, k.casefold()),
        )
        return [
            (
                k if k else "Ohne Kategorie",
                sorted(groups[k], key=lambda m: (m.name or "").casefold()),
            )
            for k in ordered_keys
        ]
    except Exception as e:
        return []


def group_financial_metrics_map_by_category(
    financial_metrics_map: dict,
    db: Session,
) -> List[dict]:
    try:
        if not financial_metrics_map:
            return []
        metric_names = list(financial_metrics_map.keys())
        rows = (
            db.query(FinancialMetric)
            .filter(FinancialMetric.name.in_(metric_names))
            .all()
        )
        name_to_category = {
            r.name: (r.category or "").strip() or "" for r in rows
        }
        groups: dict[str, dict] = defaultdict(dict)
        for name, values in financial_metrics_map.items():
            cat_key = name_to_category.get(name, "")
            groups[cat_key][name] = values
        ordered_keys = sorted(
            groups.keys(),
            key=lambda k: (1 if k == "" else 0, k.casefold()),
        )
        out: List[dict] = []
        for k in ordered_keys:
            inner = groups[k]
            sorted_metrics = {
                n: inner[n] for n in sorted(inner.keys(), key=str.casefold)
            }
            out.append(
                {
                    "category": k if k else "Ohne Kategorie",
                    "metrics": sorted_metrics,
                }
            )
        return out
    except Exception as e:
        return []

def group_metric_names_by_category(
    metric_names: List[str],
    db: Session,
) -> List[Tuple[str, List[str]]]:
    try:
        if not metric_names:
            return []
        names = list(metric_names)
        rows = (
            db.query(FinancialMetric)
            .filter(FinancialMetric.name.in_(set(names)))
            .all()
        )
        name_to_category = {
            r.name: (r.category or "").strip() or "" for r in rows
        }
        groups: dict[str, List[str]] = defaultdict(list)
        for n in names:
            cat = name_to_category.get(n, "")
            groups[cat].append(n)
        for k in groups:
            groups[k].sort(key=str.casefold)
        ordered_keys = sorted(
            groups.keys(),
            key=lambda k: (1 if k == "" else 0, k.casefold()),
        )
        return [(k if k else "Ohne Kategorie", groups[k]) for k in ordered_keys]
    except Exception as e:
        return []

def build_category_pair_summary(
    satisfied_by_category: List[Tuple[str, List[str]]],
    unsatisfied_by_category: List[Tuple[str, List[str]]],
) -> List[dict]:
    try:
        sat_map = {label: len(names) for label, names in satisfied_by_category}
        unsat_map = {label: len(names) for label, names in unsatisfied_by_category}
        all_labels = set(sat_map) | set(unsat_map)
        ordered = sorted(
            all_labels,
            key=lambda L: (1 if L == "Ohne Kategorie" else 0, L.casefold()),
        )
        rows: List[dict] = []
        for L in ordered:
            s = sat_map.get(L, 0)
            u = unsat_map.get(L, 0)
            rows.append(
                {
                    "category": L,
                    "satisfied": s,
                    "unsatisfied": u,
                    "total": s + u,
                }
            )
        return rows
    except Exception as e:
        return []


class Company(BaseModel):
    company_name: str
    strength: str
    weakness: str

class DeleteCompaniesRequest(BaseModel):
    companies: List[str]
@app.get("/")
def read_root(request: Request):
    try:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={}
        )
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request},
        )

@app.post("/get-summary", response_class=HTMLResponse)
async def analyze(request: Request, url: str = Form(...)):
    try:
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
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request},
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
         current_strengths = db_company.strength
         current_weakness =  db_company.weakness
         strengths, weaknesses = get_combination(current_strengths, current_weakness, company.strength, company.weakness)
         db_company.strength = "\n".join(f"• {s}" for s in strengths)
         db_company.weakness = "\n".join(f"• {w}" for w in weaknesses)
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
    financial_metrics_map =  get_total_financial_metrics(db, company)
    satisfied_metrics, unsatisfied_metrics, satisfied_benchmarks, unsatisfied_benchmarks, satisfied_development, unsatisfied_development = get_satisfied_and_not_satisfied_financial_metrics(financial_metrics_map, db)
    years = ["2022", "2023", "2024", "2025"]
    data_by_category = group_financial_metrics_map_by_category(
        financial_metrics_map, db
    )
    satisfied_metrics_by_category = group_metric_names_by_category(
        satisfied_metrics, db
    )
    unsatisfied_metrics_by_category = group_metric_names_by_category(
        unsatisfied_metrics, db
    )
    satisfied_benchmarks_by_category = group_metric_names_by_category(
        satisfied_benchmarks, db
    )
    unsatisfied_benchmarks_by_category = group_metric_names_by_category(
        unsatisfied_benchmarks, db
    )
    satisfied_development_by_category = group_metric_names_by_category(
        satisfied_development, db
    )
    unsatisfied_development_by_category = group_metric_names_by_category(
        unsatisfied_development, db
    )

    return templates.TemplateResponse(
        request=request,
        name="show_financial_metrics.html",
        context=
        {
            "request": request,
            "data_by_category": data_by_category,
            "years": years,
            "satisfied_metrics_by_category": satisfied_metrics_by_category,
            "unsatisfied_metrics_by_category": unsatisfied_metrics_by_category,
            "satisfied_benchmarks_by_category": satisfied_benchmarks_by_category,
            "unsatisfied_benchmarks_by_category": unsatisfied_benchmarks_by_category,
            "satisfied_development_by_category": satisfied_development_by_category,
            "unsatisfied_development_by_category": unsatisfied_development_by_category,
            "summary_combined_by_category": build_category_pair_summary(
                satisfied_metrics_by_category,
                unsatisfied_metrics_by_category,
            ),
            "summary_benchmark_by_category": build_category_pair_summary(
                satisfied_benchmarks_by_category,
                unsatisfied_benchmarks_by_category,
            ),
            "summary_development_by_category": build_category_pair_summary(
                satisfied_development_by_category,
                unsatisfied_development_by_category,
            ),
        })

@app.post("/show-saved-financial-metrics", response_class=HTMLResponse)
def show_saved_financial_metrics_page(request: Request, db: Session = Depends(get_db)):
    metrics = db.query(models.FinancialMetric).all()
    return templates.TemplateResponse(
    request=request,
        name="show_saved_financial_metrics.html",
        context={
            "request": request,
            "metrics_by_category": group_financial_metrics_by_category(metrics),
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
            "metrics_by_category": group_financial_metrics_by_category(metrics),
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
    category: str = Form(...),
    is_active: bool = Form(False),
    db: Session = Depends(get_db)
):
    metric = db.query(FinancialMetric).filter(FinancialMetric.id == metric_id).first()

    metric.name = name
    metric.should_rise = should_rise
    metric.reference_value = reference_value
    metric.unit = unit
    metric.category = category
    metric.is_active = is_active

    db.commit()

    metrics = db.query(models.FinancialMetric).all()
    return templates.TemplateResponse(
        request=request,
        name="show_saved_financial_metrics.html",
        context={
            "request": request,
            "metrics_by_category": group_financial_metrics_by_category(metrics),
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

@app.post("/metrics/delete-multiple")
def delete_metrics(
    request: Request,
    metric_ids: List[int] = Form(...),
    db: Session = Depends(get_db)
):
    metrics = db.query(FinancialMetric).filter(FinancialMetric.id.in_(metric_ids)).all()

    for metric in metrics:
        db.delete(metric)

    db.commit()

    metrics = db.query(FinancialMetric).all()
    return templates.TemplateResponse(
        request=request,
        name="show_saved_financial_metrics.html",
        context={
            "request": request,
            "metrics_by_category": group_financial_metrics_by_category(metrics),
        }
    )

@app.post("/delete-saved-companies", response_class=HTMLResponse)
def delete_saved_companies(
        request: Request,
    data: DeleteCompaniesRequest,
    db: Session = Depends(get_db)
):
    if not data.companies:
        return {"message": "Keine Companies übergeben", "deleted": 0}

    db.query(models.StockSummary)\
        .filter(models.StockSummary.name.in_(data.companies))\
        .delete(synchronize_session=False)

    db.commit()

    companies = db.query(models.StockSummary).all()

    return templates.TemplateResponse(request=request,
                                      name="saved_companies_overview.html",
                                      context={"request": request, "companies": companies
                                               })