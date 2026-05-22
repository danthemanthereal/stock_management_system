from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from collections import defaultdict
from typing import List, Tuple, Optional
from finvizfinance.screener.overview import Overview
from evaluation_component.evaluation import evaluate_new_information
from combining_stock_infos_llm.combine_stock import get_combination
from financial_metric_evaluator_component.financial_metric_evaluator import \
    get_satisfied_and_not_satisfied_financial_metrics
from database.models import FinancialMetric, IndustryProfile, ProfileMetricConfiguration, FinancialMetricCategory, \
    BoughtStock, StockSummary
from financial_metric_component.financial_metric import get_total_financial_metrics
from database.db import engine, SessionLocal
from sqlalchemy.orm import Session, joinedload
from database import models
from youtube_transcript_component.yt_transcript_component import \
    get_youtube_transcript_based_url
from summary_llm_component.gemini_llm_component import get_summary_of_gemini_with_url_context, \
    get_summary_of_gemini_of_transcript
import json
import re
import numpy as np
import pandas as pd
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
from pytube import extract
from itertools import groupby
from datetime import datetime, timedelta
from gnews import GNews

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # oder ["*"] zum Testen
    allow_credentials=True,
    allow_methods=["*"],  # wichtig für OPTIONS!
    allow_headers=["*"],
)

with open("locales/de.json", "r", encoding="utf-8") as f:
    de_translations = json.load(f)
with open("locales/en.json", "r", encoding="utf-8") as f:
    en_translations = json.load(f)

translations = {"de": de_translations, "en": en_translations}

templates = Jinja2Templates(directory="templates")


def render_localized(template_name: str, request: Request, context: dict):
    locale = get_locale(request)
    lang_dict = translations.get(locale, translations["en"])

    def translate(key: str) -> str:
        return lang_dict.get(key, key)

    context["_"] = translate
    context["current_locale"] = locale

    return templates.TemplateResponse(request, template_name, context)

def get_locale(request: Request) -> str:
    lang = request.query_params.get("lang")
    if lang in ["de", "en"]:
        return lang

    lang = request.cookies.get("preferred_lang")
    if lang in ["de", "en"]:
        return lang

    accept_language = request.headers.get("Accept-Language", "")
    if "de" in accept_language.lower():
        return "de"

    return "en"


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def metric_ids_for_branch_profile_from_form(form) -> List[int]:
    hidden = form.get("profile_selected_metric_ids")
    if hidden is not None and str(hidden).strip():
        parts = [x.strip() for x in str(hidden).split(",") if x.strip()]
        try:
            return sorted({int(x) for x in parts})
        except ValueError:
            pass
    listed = form.getlist("metric_ids")
    if listed:
        try:
            return sorted({int(x) for x in listed})
        except ValueError:
            pass
    found = set()
    for key, _ in form.multi_items():
        m = re.match(r"^is_active_(\d+)$", str(key))
        if m:
            found.add(int(m.group(1)))
    return sorted(found)


def group_financial_metrics_by_category(
        metrics: List[FinancialMetric],
) -> List[Tuple[str, List[FinancialMetric]]]:
    try:
        groups: dict[str, List[FinancialMetric]] = defaultdict(list)
        for m in metrics:
            raw = m.category_name
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
            .options(joinedload(FinancialMetric.category_rel))
            .filter(FinancialMetric.name.in_(metric_names))
            .all()
        )
        name_to_category = {
            r.name: r.category_name for r in rows
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
            .options(joinedload(FinancialMetric.category_rel))
            .filter(FinancialMetric.name.in_(set(names)))
            .all()
        )
        name_to_category = {
            r.name: r.category_name for r in rows
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


def merge_financial_summary_triples(
        combined: List[dict],
        benchmark: List[dict],
        development: List[dict],
) -> List[dict]:

    def to_map(rows: List[dict]) -> dict:
        return {r["category"]: dict(r) for r in rows}

    def enrich(row: Optional[dict]) -> dict:
        base = {"satisfied": 0, "unsatisfied": 0, "total": 0}
        if row:
            base.update(
                {
                    "satisfied": int(row.get("satisfied", 0)),
                    "unsatisfied": int(row.get("unsatisfied", 0)),
                    "total": int(row.get("total", 0)),
                }
            )
        t = base["total"]
        s, u = base["satisfied"], base["unsatisfied"]
        base["satisfied_pct"] = round(100.0 * s / t, 1) if t else None
        base["unsatisfied_pct"] = round(100.0 * u / t, 1) if t else None
        return base

    c_map = to_map(combined)
    b_map = to_map(benchmark)
    d_map = to_map(development)
    all_labels = set(c_map) | set(b_map) | set(d_map)
    ordered = sorted(
        all_labels,
        key=lambda L: (1 if L == "Ohne Kategorie" else 0, L.casefold()),
    )
    out: List[dict] = []
    for L in ordered:
        out.append(
            {
                "category": L,
                "combined": enrich(c_map.get(L)),
                "benchmark": enrich(b_map.get(L)),
                "development": enrich(d_map.get(L)),
            }
        )
    return out


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


def extract_video_id_by_url(url: str) -> str:
    try:
        return extract.video_id(url)
    except Exception as e:
        return ""


@app.post("/get-yt-transcript", response_class=HTMLResponse)
def get_yt_transcript(request: Request, url: str = Form(...)):
    try:
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
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request},
        )


@app.post("/companies")
async def receive_company(company: Company, db: Session = Depends(get_db)):
    db_company = db.query(models.StockSummary).filter_by(name=company.company_name).first()

    if db_company:
        current_strengths = db_company.strength
        current_weakness = db_company.weakness
        strengths, weaknesses = get_combination(current_strengths, current_weakness, company.strength, company.weakness)
        db_company.strength = "\n".join(f"• {s}" for s in strengths)
        db_company.weakness = "\n".join(f"• {w}" for w in weaknesses)
        db.commit()
        db.refresh(db_company)
        trajectory, reasoning, recommendation = evaluate_new_information(current_strengths, company.strength,current_weakness, company.weakness)
        print("retrun in if")
        return {
            "message": "Firma aktualisiert!",
            "id": db_company.id,
            "trajectory": trajectory,
            "reasoning": reasoning,
            "recommendation": recommendation
        }

    else:
        print("in else ")
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
    try:
        companies = db.query(models.StockSummary).filter(models.StockSummary.is_on_watch_list == True).all()

        return templates.TemplateResponse(request=request,
                                          name="saved_companies_overview.html",
                                          context={"request": request, "companies": companies
                                                   })
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request}
        )


@app.post("/find-potential-stocks", response_class=HTMLResponse)
def scrape_tradingview(request: Request):
    try:


        return templates.TemplateResponse(request=request,
                                          name="find_candidates.html",
                                          context={})
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request}
        )


@app.post("/get-financial-metrics", response_class=HTMLResponse)
def get_financial_metrics_by_guro_focus_end_point(request: Request, company: str = Form(...),
                                                  db: Session = Depends(get_db)):
    try:
        financial_metrics_map = get_total_financial_metrics(db, company)
        satisfied_metrics, unsatisfied_metrics, satisfied_benchmarks, unsatisfied_benchmarks, satisfied_development, unsatisfied_development = get_satisfied_and_not_satisfied_financial_metrics(
            financial_metrics_map, db)
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

        summary_combined = build_category_pair_summary(
            satisfied_metrics_by_category,
            unsatisfied_metrics_by_category,
        )
        summary_benchmark = build_category_pair_summary(
            satisfied_benchmarks_by_category,
            unsatisfied_benchmarks_by_category,
        )
        summary_development = build_category_pair_summary(
            satisfied_development_by_category,
            unsatisfied_development_by_category,
        )

        return render_localized(
            request=request,
            template_name="show_financial_metrics.html",
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
                "summary_wide_by_category": merge_financial_summary_triples(
                    summary_combined,
                    summary_benchmark,
                    summary_development,
                ),
            })
    except Exception as e:
        print(e)
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request}
        )


@app.api_route("/show-saved-financial-metrics", methods=["GET", "POST"], response_class=HTMLResponse)
def show_saved_financial_metrics_page(
        request: Request,
        branch_profile_id: Optional[int] = Form(None),
        db: Session = Depends(get_db)
):
    try:
        selected_id = branch_profile_id
        if request.method == "GET":
            query_id = request.query_params.get("branch_profile_id")
            selected_id = int(query_id) if query_id else 1

        if not selected_id:
            selected_id = 1

        branch_profiles = db.query(IndustryProfile).all()

        configs = (
            db.query(ProfileMetricConfiguration)
            .join(FinancialMetric)
            .outerjoin(FinancialMetricCategory, FinancialMetric.category_id == FinancialMetricCategory.id)
            .filter(ProfileMetricConfiguration.profile_id == selected_id)
            .order_by(FinancialMetricCategory.name)
            .all()
        )

        metrics_by_category = []
        for category_name, group in groupby(
                configs,
                lambda x: x.metric.category_rel.name if x.metric.category_rel else "— keine —"
        ):
            group_list = list(group)
            if group_list:
                metrics_by_category.append((category_name, group_list))

        all_available_metrics = db.query(FinancialMetric).order_by(FinancialMetric.name).all()

        return render_localized(
            template_name="show_saved_financial_metrics.html",
            request=request,
            context={
                "branch_profiles": branch_profiles,
                "selected_branch_profile_id": selected_id,
                "metrics_by_category": metrics_by_category,
                "displayed_metrics_count": len(configs),
                "all_available_metrics": all_available_metrics
            }
        )
    except Exception as e:
        print(f"Error: {e}")
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})

@app.post("/metrics/create", response_class=HTMLResponse)
def create_metric(
        selected_branch_id: int = Form(1),
        name: str = Form(...),
        unit: str = Form(...),
        reference_value: int = Form(...),
        should_rise: bool = Form(False),
        category_id: str = Form(""),
        db: Session = Depends(get_db)
):
    new_metric = FinancialMetric(
        name=name, unit=unit
    )
    if category_id.strip():
        new_metric.category_id = int(category_id)

    db.add(new_metric)
    db.flush()

    new_config = ProfileMetricConfiguration(
        profile_id=selected_branch_id,
        metric_id=new_metric.id,
        should_rise=should_rise,
        reference_value=reference_value,
        is_active=True
    )
    db.add(new_config)
    db.commit()
    return RedirectResponse(url=f"/show-saved-financial-metrics?branch_profile_id={selected_branch_id}",
                            status_code=303)


@app.post("/metrics/branch-profiles/create", response_class=HTMLResponse)
async def create_branch_profile(
        request: Request,
        branch_profile_name: str = Form(...),
        # Wir fangen hier das Triplett-Feld aus dem JavaScript ab
        metric_data_triplets: str = Form(""),
        db: Session = Depends(get_db)
):
    try:
        new_profile = IndustryProfile(name=branch_profile_name)
        db.add(new_profile)
        db.flush()

        if metric_data_triplets:

            triplet_list = [t.strip() for t in metric_data_triplets.split(",") if t.strip()]

            for triplet in triplet_list:
                if "|" in triplet:
                    parts = triplet.split("|")

                    if len(parts) == 3:
                        m_id = int(parts[0])

                        ref_value = int(parts[1]) if parts[1].isdigit() else 0

                        base_metric = db.query(FinancialMetric).filter(FinancialMetric.id == m_id).first()

                        if base_metric:
                            new_config = ProfileMetricConfiguration(
                                profile_id=new_profile.id,
                                metric_id=m_id,
                                reference_value=ref_value,
                                is_active=True
                            )
                            db.add(new_config)

        db.commit()

        return RedirectResponse(
            url=f"/show-saved-financial-metrics?branch_profile_id={new_profile.id}",
            status_code=303
        )

    except Exception as e:
        db.rollback()
        print(f"Fehler beim Erstellen des Branchenprofils: {e}")
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request}
        )
@app.post("/metrics/branch-profiles/{profile_id}/delete", response_class=HTMLResponse)
def delete_branch_profile(
        profile_id: int,
        db: Session = Depends(get_db),
):
    if profile_id != 1:
        db.query(IndustryProfile).filter(IndustryProfile.id == profile_id).delete()
        db.commit()
    return RedirectResponse(url="/show-saved-financial-metrics?branch_profile_id=1", status_code=303)


@app.post("/metrics/update/{profile_id}/{metric_id}")
def update_metric(
        profile_id: int,
        metric_id: int,
        name: str = Form(...),
        unit: str = Form(...),
        category_id: str = Form(""),
        should_rise: bool = Form(False),
        reference_value: int = Form(0),
        is_active: bool = Form(False),
        db: Session = Depends(get_db)
):
    metric = db.query(FinancialMetric).filter(FinancialMetric.id == metric_id).first()
    metric.name = name
    metric.unit = unit
    metric.category_id = int(category_id) if category_id.strip() else None

    config = db.query(ProfileMetricConfiguration).filter(
        ProfileMetricConfiguration.profile_id == profile_id,
        ProfileMetricConfiguration.metric_id == metric_id
    ).first()

    if not config:
        config = ProfileMetricConfiguration(profile_id=profile_id, metric_id=metric_id)
        db.add(config)

    config.should_rise = should_rise
    config.reference_value = reference_value
    config.is_active = is_active

    db.commit()

    return RedirectResponse(
        url=f"/show-saved-financial-metrics?branch_profile_id={profile_id}",
        status_code=303
    )


@app.get("/metrics/edit/{profile_id}/{metric_id}", response_class=HTMLResponse)
def edit_metric_page(
        request: Request,
        profile_id: int,
        metric_id: int,
        db: Session = Depends(get_db)
):
    metric = db.query(FinancialMetric).filter(FinancialMetric.id == metric_id).first()

    profile = db.query(IndustryProfile).filter(IndustryProfile.id == profile_id).first()

    config = db.query(ProfileMetricConfiguration).filter(
        ProfileMetricConfiguration.profile_id == profile_id,
        ProfileMetricConfiguration.metric_id == metric_id
    ).first()

    if not config:
        config = ProfileMetricConfiguration(
            profile_id=profile_id,
            metric_id=metric_id,
            is_active=True,
            should_rise=True,
            reference_value=0
        )

    metric_categories = db.query(FinancialMetricCategory).all()

    return templates.TemplateResponse(
        request=request,
        name="edit_metric.html",
        context={
            "request": request,
            "metric": metric,
            "profile": profile,
            "config": config,
            "metric_categories": metric_categories
        }
    )


@app.post("/metrics/delete-multiple")
def delete_metrics(
        metric_ids: str = Form(...),
        selected_branch_id: int = Form(1),
        db: Session = Depends(get_db)
):
    id_list = [int(i) for i in metric_ids.split(",") if i.strip()]
    if selected_branch_id == 1:
        db.query(FinancialMetric).filter(FinancialMetric.id.in_(id_list)).delete(synchronize_session=False)
    else:
        db.query(ProfileMetricConfiguration).filter(
            ProfileMetricConfiguration.profile_id == selected_branch_id,
            ProfileMetricConfiguration.metric_id.in_(id_list)
        ).delete(synchronize_session=False)
    db.commit()
    return RedirectResponse(url=f"/show-saved-financial-metrics?branch_profile_id={selected_branch_id}",
                            status_code=303)


@app.post("/delete-saved-companies", response_class=HTMLResponse)
def delete_saved_companies(
        request: Request,
        data: DeleteCompaniesRequest,
        db: Session = Depends(get_db)
):
    try:
        if not data.companies:
            return {"message": "Keine Companies übergeben", "deleted": 0}

        db.query(models.StockSummary) \
            .filter(models.StockSummary.name.in_(data.companies)) \
            .delete(synchronize_session=False)

        db.commit()

        companies = db.query(models.StockSummary).all()

        return templates.TemplateResponse(request=request,
                                          name="saved_companies_overview.html",
                                          context={"request": request, "companies": companies
                                                   })
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request}
        )


@app.get("/portfolio", response_class=HTMLResponse)
async def get_portfolio_page(request: Request, db: Session = Depends(get_db)):
    try:
        bought_stocks = db.query(BoughtStock).order_by(BoughtStock.ticker).all()

        return render_localized(
             template_name="portfolio.html",
             request=request,
            context={
                "request": request,
                "bought_stocks": bought_stocks,
            }
            )

    except Exception as e:
        print(f"Fehler beim Laden des Portfolios: {e}")
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})


@app.post("/portfolio/create")
async def create_portfolio_entry(
        name: str = Form(...),
        ticker: str = Form(...),
        bought_price: float = Form(...),
        amount: float = Form(...),
        db: Session = Depends(get_db)
):
    try:
        new_stock = BoughtStock(
            name=name.strip(),
            ticker=ticker.strip().upper(),
            bought_price=bought_price,
            amount=amount
        )
        db.add(new_stock)
        db.commit()

        return RedirectResponse(url="/portfolio", status_code=303)

    except Exception as e:
        db.rollback()
        print(f"Fehler beim Speichern der Aktie: {e}")
        return RedirectResponse(url="/portfolio", status_code=303)


@app.post("/portfolio/update-multiple")
async def update_multiple_portfolio_entries(
        delete_ids: str = Form(""),
        update_triplets: str = Form(""),
        db: Session = Depends(get_db)
):
    try:
        if delete_ids:
            id_list_to_delete = [int(stock_id) for stock_id in delete_ids.split(",") if stock_id.strip()]
            if id_list_to_delete:
                db.query(BoughtStock).filter(BoughtStock.id.in_(id_list_to_delete)).delete(synchronize_session=False)

        if update_triplets:
            triplet_list = [t.strip() for t in update_triplets.split(",") if t.strip()]

            for triplet in triplet_list:
                if "|" in triplet:
                    parts = triplet.split("|")
                    if len(parts) == 3:
                        stock_id = int(parts[0])
                        new_price = float(parts[1])
                        new_amount = float(parts[2])

                        stock_entry = db.query(BoughtStock).filter(BoughtStock.id == stock_id).first()
                        if stock_entry:
                            stock_entry.bought_price = new_price
                            stock_entry.amount = new_amount

        db.commit()

        return RedirectResponse(url="/portfolio", status_code=303)

    except Exception as e:
        db.rollback()
        print(f"Fehler bei der Massenverarbeitung des Portfolios: {e}")
        return RedirectResponse(url="/portfolio", status_code=303)


@app.post("/api/bought-stocks", status_code=status.HTTP_201_CREATED)
def create_bought_stock(stock_data: BoughtStockCreate, db: Session = Depends(get_db)):
    existing_stock = db.query(BoughtStock).filter(BoughtStock.name == stock_data.name).first()

    if existing_stock:
        raise HTTPException(
            status_code=400,
            detail=f"Die Aktie '{stock_data.name}' wurde bereits eingebucht!"
        )

    generated_ticker = stock_data.name.replace(" ", "").upper()[:5]

    db_bought_stock = BoughtStock(
        name=stock_data.name,
        ticker=generated_ticker,
        amount=stock_data.amount,
        bought_price=stock_data.bought_price
    )

    try:
        db.add(db_bought_stock)
        current_stock = db.query(StockSummary).filter(StockSummary.name == stock_data.name).first()
        current_stock.is_on_watch_list = False
        db.commit()
        db.refresh(db_bought_stock)
        return {"status": "success", "message": "Aktie erfolgreich eingebucht", "data": db_bought_stock}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Datenbankfehler: {str(e)}")


@app.get("/get-news")
def get_news_of_stock_with_finnhub(request: Request, stock: str = Query(...)):
    finhub_api_key = "cqe2g6pr01qgmug3gjogcqe2g6pr01qgmug3gjp0"
    today = datetime.utcnow().date()
    two_days_ago = today - timedelta(days=2)
    url = f"https://finnhub.io/api/v1/company-news?symbol={stock}&from={two_days_ago}&to={today}&token={finhub_api_key}"
    response = requests.get(url)
    data = response.json()

    headline_url = []

    for news in data:
        headline_url.append({
            "headline": news["headline"],
            "url": news["url"],
        })


    google_news = GNews(language='de', country='DE', period='1d')

    meine_news = google_news.get_news(f'{stock}  Aktie news')

    for artikel in meine_news:
        headline_url.append({
            "headline": artikel['title'],
            "url": artikel['url']
        })

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "news": headline_url
        }
    )


@app.post("/api/get-summary")
async def get_summary_api(payload: SummaryRequest):
    target_url = payload.url

    ergebnis_text = get_summary_of_gemini_with_url_context(target_url)

    return {"summary": ergebnis_text}

@app.get("/watchlist")
def watch_list(request: Request, db: Session = Depends(get_db)):
    watch_list_stocks = db.query(models.StockSummary).filter(models.StockSummary.is_on_watch_list == True).all()
    return templates.TemplateResponse(request=request,
                                      name="watchlist.html",
                                      context={"request": request,
                                               "watch_list_stocks": watch_list_stocks
                                               })

@app.get("/analysis")
def analysis(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="analysis.html",
        context={"request": request})


@app.post("/find-candidates")
def screen(filters: dict):
    f = Overview()
    f.set_filter(filters_dict=filters)

    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    })


    import finvizfinance.util as util
    original_web_scrap = util.web_scrap

    def patched_web_scrap(url, params, timeout=30):  # Timeout erhöhen
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=timeout)
            resp.raise_for_status()
            return resp.text
        except requests.exceptions.Timeout as e:
            raise requests.exceptions.Timeout(f"Timeout für {url}: {e}")

    util.web_scrap = patched_web_scrap

    try:
        df = f.screener_view()
    finally:
        util.web_scrap = original_web_scrap

    df = df.astype(object)

    df = df.where(pd.notnull(df) & ~df.isin([np.inf, -np.inf]), None)

    return {
        "count": len(df),
        "data": df.to_dict(orient="records")
    }