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
from src.portfolio_component.views import portfolio_router
from src.watchlist_component.views import watchlist_router

load_dotenv()

models.Base.metadata.create_all(bind=engine)

class Company(BaseModel):
    company_name: str
    strength: str
    weakness: str


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
async def receive_company(
        company: Company,
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id),
):
    db_company = db.query(models.StockSummary).filter_by(
        name=company.company_name,
        user_id=current_user_id
    ).first()

    if db_company:
        current_strengths = db_company.strength
        current_weakness = db_company.weakness
        strengths, weaknesses = get_combination(current_strengths, current_weakness, company.strength, company.weakness)
        db_company.strength = "\n".join(f"• {s}" for s in strengths)
        db_company.weakness = "\n".join(f"• {w}" for w in weaknesses)
        db.commit()
        db.refresh(db_company)
        trajectory, reasoning, recommendation = evaluate_new_information(current_strengths, company.strength,
                                                                         current_weakness, company.weakness)

        return {
            "message": "Firma aktualisiert!",
            "id": db_company.id,
            "trajectory": trajectory,
            "reasoning": reasoning,
            "recommendation": recommendation
        }

    else:
        db_company = models.StockSummary(
            name=company.company_name,
            strength=company.strength,
            weakness=company.weakness,
            is_on_watch_list=True,
            user_id=current_user_id
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
def show_companies(request: Request, db: Session = Depends(get_db), current_user_id: UUID = Depends(get_current_user_id)):
    try:
        companies = db.query(models.StockSummary).filter(
            models.StockSummary.is_on_watch_list == True,
            models.StockSummary.user_id == current_user_id
        ).all()

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
        print("".join(traceback.format_exc()))
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request}
        )


@app.api_route("/show-saved-financial-metrics", methods=["GET", "POST"], response_class=HTMLResponse)
def show_saved_financial_metrics_page(
        request: Request,
        branch_profile_id: Optional[int] = Form(None),
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id),
):
    try:
        selected_id = branch_profile_id
        if request.method == "GET":
            query_id = request.query_params.get("branch_profile_id")

        user_id = db.query(User).filter(User.user_name == current_user_id).first().id

        if not selected_id:
            selected_id = db.query(IndustryProfile).join(User).filter(User.id == user_id).first().id
        print("sel id", selected_id)
        branch_profiles = db.query(IndustryProfile).filter(IndustryProfile.user_id == current_user_id).all()

        configs = (
            db.query(ProfileMetricConfiguration)
            .join(FinancialMetric)
            .join(IndustryProfile)
            .outerjoin(FinancialMetricCategory, FinancialMetric.category_id == FinancialMetricCategory.id)
            .filter(ProfileMetricConfiguration.profile_id == selected_id, IndustryProfile.user_id == user_id)
            .order_by(FinancialMetricCategory.name)
            .all()
        )
        print("configs:", configs)


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
    request: Request,
    selected_branch_id: int = Form(...),
    financial_metric_id: int = Form(...),
    reference_value: int = Form(...),
    should_rise: bool = Form(False),
    db: Session = Depends(get_db),
    current_user_id: UUID = Depends(get_current_user_id),
):
    profile = db.query(IndustryProfile).filter(
        IndustryProfile.id == selected_branch_id,
        IndustryProfile.user_id == current_user_id,
    ).first()
    if not profile:

        general_profile = db.query(IndustryProfile).filter_by(
                name="Allgemein",
                user_id=current_user_id
        ).first()
        if general_profile:
            profile = general_profile
            selected_branch_id = general_profile.id
        else:
            profile = IndustryProfile(
                    name="Allgemein",
                    user_id=current_user_id
            )
            db.add(profile)
            db.commit()
            db.refresh(profile)
            selected_branch_id = profile.id


    metric = db.query(FinancialMetric).filter(FinancialMetric.id == financial_metric_id).first()
    if not metric:
        raise HTTPException(status_code=400, detail="Metrik nicht gefunden")

    existing = db.query(ProfileMetricConfiguration).filter_by(
        profile_id=selected_branch_id,
        metric_id=metric.id,
    ).first()
    if existing:

        existing.reference_value = reference_value
        existing.should_rise = should_rise
        existing.is_active = True
    else:
        new_config = ProfileMetricConfiguration(
            profile_id=selected_branch_id,
            metric_id=metric.id,
            should_rise=should_rise,
            reference_value=reference_value,
            is_active=True,
        )
        db.add(new_config)

    db.commit()
    return RedirectResponse(
        url=f"/show-saved-financial-metrics?branch_profile_id={selected_branch_id}",
        status_code=303,
    )


@app.post("/metrics/branch-profiles/create", response_class=HTMLResponse)
async def create_branch_profile(
        request: Request,
        branch_profile_name: str = Form(...),
        metric_data_triplets: str = Form(""),
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id),
):
    try:
        new_profile = IndustryProfile(name=branch_profile_name, user_id=current_user_id)
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
        current_user_id: UUID = Depends(get_current_user_id),
):
    if profile_id != 1:
        db.query(IndustryProfile).filter(IndustryProfile.id == profile_id,
                                         IndustryProfile.user_id == current_user_id).delete()
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
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id),
):
    metric = db.query(FinancialMetric).filter(FinancialMetric.id == metric_id).first()
    metric.name = name
    metric.unit = unit
    metric.category_id = int(category_id) if category_id.strip() else None

    config = db.query(ProfileMetricConfiguration).join(IndustryProfile).filter(
        ProfileMetricConfiguration.profile_id == profile_id,
        ProfileMetricConfiguration.metric_id == metric_id,
        IndustryProfile.user_id == current_user_id
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
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id),
):
    metric = db.query(FinancialMetric).filter(FinancialMetric.id == metric_id).first()
    user_id = db.query(User).filter(User.user_name == current_user_id).first().id
    if not profile_id:
        profile_id = db.query(IndustryProfile).join(User).filter(User.id == user_id).first().id
    profile = db.query(IndustryProfile).filter(IndustryProfile.id == profile_id,
                                               IndustryProfile.user_id == user_id).first()

    config = (
        db.query(ProfileMetricConfiguration)
        .join(IndustryProfile)
        .filter(
            ProfileMetricConfiguration.profile_id == profile_id,
            ProfileMetricConfiguration.metric_id == metric_id,
            IndustryProfile.user_id == current_user_id
        )
        .first()
    )

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
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id),
):
    id_list = [int(i) for i in metric_ids.split(",") if i.strip()]
    if selected_branch_id == 1:
        db.query(FinancialMetric).filter(FinancialMetric.id.in_(id_list)).delete(synchronize_session=False)
    else:
        (
            db.query(ProfileMetricConfiguration)
            .join(IndustryProfile)
            .filter(
                ProfileMetricConfiguration.profile_id == selected_branch_id,
                ProfileMetricConfiguration.metric_id.in_(id_list),
                IndustryProfile.user_id == current_user_id
            )
            .delete(synchronize_session=False)
        )
    db.commit()
    return RedirectResponse(url=f"/show-saved-financial-metrics?branch_profile_id={selected_branch_id}",
                            status_code=303)

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

with open("locales/de.json", "r", encoding="utf-8") as f:
    de_translations = json.load(f)
with open("locales/en.json", "r", encoding="utf-8") as f:
    en_translations = json.load(f)


templates = Jinja2Templates(directory="templates")











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



