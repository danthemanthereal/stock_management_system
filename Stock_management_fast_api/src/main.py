from uuid import UUID

from fastapi import FastAPI, Request, Form, Depends, HTTPException, status, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from collections import defaultdict
from typing import List, Tuple, Optional
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
import re
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
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
from src.analysis_component.views import analysis_router

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




