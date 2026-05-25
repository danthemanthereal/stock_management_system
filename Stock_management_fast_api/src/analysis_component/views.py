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
from src.financial_metric_analysis_component.financial_metric_service import MetricsService
from src.template_component.service import TemplateService
from src.financial_metric_category_component.service import FinancialMetricCategoryService
from src.template_metric_component.service import TemplateMetricService
from src.find_potential_stocks_component.find_potential_stocks import FindPotentialStocks
from src.strength_weakness_company_component.strenth_weakness_comapany import \
    StrengthWeaknessOfCompanyComponent

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
        strength_weakness_company_component = StrengthWeaknessOfCompanyComponent()
        companies_array = strength_weakness_company_component.get_summary_of_gemini_with_url_context(url)

        if isinstance(companies_array, str):
            try:
                companies_array = json.loads(companies_array)
            except json.JSONDecodeError:
                companies_array = []

        return templates.TemplateResponse(
            request=request,
            name="analysis/companies_overview.html",
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

        strength_weakness_company_component = StrengthWeaknessOfCompanyComponent()
        companies_array = strength_weakness_company_component.get_strength_weakness_of_youtube(url)

        if isinstance(companies_array, str):
            try:
                companies_array = json.loads(companies_array)
            except json.JSONDecodeError:
                companies_array = []

        return templates.TemplateResponse(
            request=request,
            name="analysis/companies_overview.html",
            context={"request": request, "companies": companies_array}
        )
    except Exception as e:
        print(e)
        traceback.print_exc()
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request},
        )


@analysis_router.api_route("/show-saved-financial-metrics", methods=["GET", "POST"], response_class=HTMLResponse)
def show_saved_financial_metrics_page(
        request: Request,
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id),
):
    try:
        financial_metric_service = MetricsService(db)
        template_service = TemplateService(db)
        last_selected_branch_profile_id = template_service.get_last_selected_template_id_of_user(current_user_id)
        available_metrics = financial_metric_service.get_available_metrics()
        current_user_created_templates = template_service.get_current_user_created_templates(current_user_id)
        financial_metrics_of_last_selected_template_per_category = financial_metric_service.get_all_financial_metrics_of_last_selected_template_per_category(
            last_selected_branch_profile_id)

        return render_localized(
            template_name="analysis/show_saved_financial_metrics.html",
            request=request,
            context={
                "available_metrics": available_metrics,
                "last_selected_branch_profile_id": last_selected_branch_profile_id,
                "branch_profiles": current_user_created_templates,
                "financial_metrics_of_last_selected_template_per_category": financial_metrics_of_last_selected_template_per_category,
            }
        )
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})


@analysis_router.post("/add-metric-to-current-template", response_class=HTMLResponse)
def add_to_current_selected_template_new_financial_metric(
        request: Request,
        last_selected_branch_profile_id: int = Form(...),
        financial_metric_id: int = Form(...),
        reference_value: float = Form(...),
        should_rise: bool = Form(False),
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id)
):
    try:
        financial_metric_service = MetricsService(db)
        financial_metric_service.add_metric_to_profile(
            profile_id=last_selected_branch_profile_id,
            metric_id=financial_metric_id,
            reference_value=reference_value,
            should_rise=should_rise,
            user_id=current_user_id
        )
        financial_metric_service = MetricsService(db)
        template_service = TemplateService(db)
        last_selected_branch_profile_id = template_service.get_last_selected_template_id_of_user(current_user_id)
        available_metrics = financial_metric_service.get_available_metrics()
        current_user_created_templates = template_service.get_current_user_created_templates(current_user_id)
        financial_metrics_of_last_selected_template_per_category = financial_metric_service.get_all_financial_metrics_of_last_selected_template_per_category(
            last_selected_branch_profile_id)

        return render_localized(
            template_name="analysis/show_saved_financial_metrics.html",
            request=request,
            context={
                "available_metrics": available_metrics,
                "last_selected_branch_profile_id": last_selected_branch_profile_id,
                "branch_profiles": current_user_created_templates,
                "financial_metrics_of_last_selected_template_per_category": financial_metrics_of_last_selected_template_per_category,
            }
        )
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})


@analysis_router.post("/create-new-template-with-current-properties", response_class=HTMLResponse)
def create_new_template_of_current_financial_metrics_properties(
        request: Request,
        branch_profile_name: str = Form(...),
        metric_data_triplets: Optional[str] = Form(None),
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id)
):
    try:
        template_service = TemplateService(db)
        (template_service.create_template_from_active_metrics(
            user_id=current_user_id,
            new_profile_name=branch_profile_name,
            triplets_str=metric_data_triplets))
        financial_metric_service = MetricsService(db)
        template_service = TemplateService(db)
        last_selected_branch_profile_id = template_service.get_last_selected_template_id_of_user(current_user_id)
        available_metrics = financial_metric_service.get_available_metrics()
        current_user_created_templates = template_service.get_current_user_created_templates(current_user_id)
        financial_metrics_of_last_selected_template_per_category = financial_metric_service.get_all_financial_metrics_of_last_selected_template_per_category(
            last_selected_branch_profile_id)

        return render_localized(
            template_name="analysis/show_saved_financial_metrics.html",
            request=request,
            context={
                "available_metrics": available_metrics,
                "last_selected_branch_profile_id": last_selected_branch_profile_id,
                "branch_profiles": current_user_created_templates,
                "financial_metrics_of_last_selected_template_per_category": financial_metrics_of_last_selected_template_per_category,

            })
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})


@analysis_router.post("/change-selected-template")
def change_selected_template(
        request: Request,
        branch_profile_id: int = Form(...),
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id)
):
    try:
        financial_metric_service = MetricsService(db)
        template_service = TemplateService(db)
        template_service.update_last_selected_template_id(branch_profile_id, current_user_id)
        last_selected_branch_profile_id = template_service.get_last_selected_template_id_of_user(current_user_id)
        available_metrics = financial_metric_service.get_available_metrics()
        current_user_created_templates = template_service.get_current_user_created_templates(current_user_id)
        financial_metrics_of_last_selected_template_per_category = financial_metric_service.get_all_financial_metrics_of_last_selected_template_per_category(
            last_selected_branch_profile_id)

        return render_localized(
            template_name="analysis/show_saved_financial_metrics.html",
            request=request,
            context={
                "available_metrics": available_metrics,
                "last_selected_branch_profile_id": last_selected_branch_profile_id,
                "branch_profiles": current_user_created_templates,
                "financial_metrics_of_last_selected_template_per_category": financial_metrics_of_last_selected_template_per_category,

            })

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})


@analysis_router.get("/edit-metric-of-current-template/{last_selected_branch_profile_id}/{metric_id}")
def show_edit_financial_metric_of_current_template(
        request: Request,
        last_selected_branch_profile_id: int,
        metric_id: int,
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id)
):
    template_service = TemplateService(db)
    financial_metric_service = MetricsService(db)
    financial_metric_category_service = FinancialMetricCategoryService(db)
    financial_metric_template_service = TemplateMetricService(db)

    template = template_service.get_template_by_id(last_selected_branch_profile_id)
    metric = financial_metric_service.get_financial_metric_by_id(metric_id)
    metric_categories = financial_metric_category_service.get_all_metric_categories()
    config = financial_metric_template_service.get_config_by_metric_and_template_id(metric_id,
                                                                                    last_selected_branch_profile_id)

    return templates.TemplateResponse(
        request=request,
        name="analysis/edit_metric.html",
        context={
            "request": request,
            "active_page": "Kennzahl bearbeiten",
            "profile": template,
            "metric": metric,
            "config": config,
            "metric_categories": metric_categories,
            "selected_branch_profile_id": last_selected_branch_profile_id,
        })


@analysis_router.post("/update-metric-of-current-template-config/{config_id}")
def update_metric_of_current_template(
        request: Request,
        config_id: int,
        db: Session = Depends(get_db),
        name: str = Form(...),
        unit: str = Form(...),
        should_rise: bool = Form(False),
        reference_value: float = Form(None),
        is_active: bool = Form(False),
        current_user_id: UUID = Depends(get_current_user_id)
):
    try:
        financial_metric_template_service = TemplateMetricService(db)
        financial_metric_template_service.update_template_metric_configuration(
            config_id=config_id,
            new_reference_value=reference_value,
            should_rise=should_rise,
            is_active=is_active,
        )

        financial_metric_service = MetricsService(db)
        template_service = TemplateService(db)
        last_selected_branch_profile_id = template_service.get_last_selected_template_id_of_user(current_user_id)
        available_metrics = financial_metric_service.get_available_metrics()
        current_user_created_templates = template_service.get_current_user_created_templates(current_user_id)
        financial_metrics_of_last_selected_template_per_category = financial_metric_service.get_all_financial_metrics_of_last_selected_template_per_category(
            last_selected_branch_profile_id)

        return render_localized(
            template_name="analysis/show_saved_financial_metrics.html",
            request=request,
            context={
                "available_metrics": available_metrics,
                "last_selected_branch_profile_id": last_selected_branch_profile_id,
                "branch_profiles": current_user_created_templates,
                "financial_metrics_of_last_selected_template_per_category": financial_metrics_of_last_selected_template_per_category,

            })
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})


@analysis_router.post("/delete-selected-metrics-for-this-template")
def delete_selected_metrics_for_this_template(
        request: Request,
        selected_branch_id: int = Form(...),
        metric_ids: Optional[str] = Form(None),
        db: Session = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id)
):
    try:
        ids_to_delete = [int(id_str.strip()) for id_str in metric_ids.split(",") if id_str.strip()]
        template_metric_service = TemplateMetricService(db)
        template_metric_service.delete_metrics_of_current_template(selected_branch_id, ids_to_delete)
        financial_metric_service = MetricsService(db)
        template_service = TemplateService(db)
        last_selected_branch_profile_id = template_service.get_last_selected_template_id_of_user(current_user_id)
        available_metrics = financial_metric_service.get_available_metrics()
        current_user_created_templates = template_service.get_current_user_created_templates(current_user_id)
        financial_metrics_of_last_selected_template_per_category = financial_metric_service.get_all_financial_metrics_of_last_selected_template_per_category(
            last_selected_branch_profile_id)

        return render_localized(
            template_name="analysis/show_saved_financial_metrics.html",
            request=request,
            context={
                "available_metrics": available_metrics,
                "last_selected_branch_profile_id": last_selected_branch_profile_id,
                "branch_profiles": current_user_created_templates,
                "financial_metrics_of_last_selected_template_per_category": financial_metrics_of_last_selected_template_per_category,

            })


    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})









@analysis_router.post("/find-potential-stocks", response_class=HTMLResponse)
def find_potential_stocks_page(request: Request):
    try:

        return templates.TemplateResponse(request=request,
                                          name="analysis/find_candidates.html",
                                          context={})
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request}
        )


@analysis_router.post("/find-candidates")
def find_potential_stocks(filters: dict):
    find_potential_stocks_component = FindPotentialStocks()
    return find_potential_stocks_component.find_potential_stocks_for_current_user(filters)


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
