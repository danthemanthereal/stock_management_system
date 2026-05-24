import traceback
from itertools import groupby
from typing import List, Tuple, Optional
from uuid import UUID
from fastapi import APIRouter, Request, Depends, BackgroundTasks, Form, requests, Query
from sqlalchemy.orm import Session
from src.database import db
from src.database.models import User
from fastapi.templating import Jinja2Templates
from src.database.db import get_db
import json
import requests
from starlette.responses import HTMLResponse
from src.summary_llm_component.gemini_llm_component import \
    get_summary_of_gemini_with_url_context
from src.summary_llm_component.gemini_llm_component import get_summary_of_gemini_of_transcript
from src.youtube_transcript_component.yt_transcript_component import get_summary_of_yt_video
from src.find_potential_stocks_component.find_potential_stocks import \
    find_potential_stocks_for_current_user
from src.utils.utils import render_localized
from src.financial_metric_analysis_component.financial_metric_analysis import \
    merge_financial_summary_triples, build_category_pair_summary, group_metric_names_by_category, \
    group_financial_metrics_map_by_category, get_total_financial_metrics
from src.financial_metric_evaluator_component.financial_metric_evaluator import \
    get_satisfied_and_not_satisfied_financial_metrics
from src.authenticator_component.authenticator import get_current_user_id
from src.database.models import IndustryProfile, ProfileMetricConfiguration, FinancialMetric, \
    FinancialMetricCategory
from datetime import datetime, timedelta
from gnews import GNews
from src.analysis_component.service import get_available_metrics

templates = Jinja2Templates(directory="templates")

analysis_router = APIRouter(prefix="/analysis", tags=["analysis"])

@analysis_router.get("/")
def analysis(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="analysis/analysis.html",
        context={"request": request})


@analysis_router.post("/get-summary-url", response_class=HTMLResponse)
async def analyze_url(request: Request, url: str = Form(...)):
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

@analysis_router.post("/get-summary-by-yt-video", response_class=HTMLResponse)
def get_yt_transcript(request: Request, url: str = Form(...)):
    try:

        transcript = get_summary_of_yt_video(url)
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

@analysis_router.post("/find-potential-stocks", response_class=HTMLResponse)
def find_potential_stocks_page(request: Request):
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


@analysis_router.post("/find-candidates")
def find_potential_stocks(filters: dict):
    return find_potential_stocks_for_current_user(filters)


@analysis_router.post("/get-financial-metrics", response_class=HTMLResponse)
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

@analysis_router.api_route("/show-saved-financial-metrics", methods=["GET", "POST"],response_class=HTMLResponse)
def show_saved_financial_metrics_page(
        request: Request,
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id),
):
    try:


        available_metrics = get_available_metrics(db)

        return render_localized(
            template_name="analysis/show_saved_financial_metrics.html",
            request=request,
            context={
                "available_metrics": available_metrics
            }
        )
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})


@analysis_router.get("/get-news")
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
        name="show_news.html",
        context={
            "news_articles": headline_url
        }
    )
