import traceback
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Request, Depends,Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from src.analysis_component.service import AnalysisService
from src.bought_stock_component.service import BoughtStockService
from fastapi.templating import Jinja2Templates
from src.database.db import get_db
from starlette.responses import HTMLResponse
from src.financial_metric_analysis_component.evaluation_ai_financial_metrics import FinancialMetricAIEvaluator
from src.kaparthies_llm_wiki_component.llm_wiki import LLMWiki
from src.utils.utils import render_localized
from src.authenticator_component.authenticator import get_current_user_id
from src.financial_metric_analysis_component.financial_metric_service import MetricsService
from dotenv import load_dotenv
from src.financial_metric_analysis_component.utils import merge_financial_summary_triples
from src.configs.used_model import  FINANCIAL_METRIC_EVALUATION_MODEL, LLM_WIKI_MODEL
from src.watchlist_component.service import WatchlistStockService

load_dotenv()

templates = Jinja2Templates(directory="templates")

analysis_router = APIRouter(prefix="/analysis", tags=["analysis"])

@analysis_router.get("/")
def analysis(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="analysis/analysis.html",
        context={"request": request})

@analysis_router.post("/get-summary-url", response_class=HTMLResponse)
async def analyze_url(request: Request,
                      url: str = Form(...),
                      db: AsyncSession = Depends(get_db)):
    try:

        analysis_service = AnalysisService(db)
        companies_array = await analysis_service.analyse_url(url)

        return templates.TemplateResponse(
            request=request,
            name="analysis/companies_overview.html",
            context={"request": request,
                     "companies": companies_array,
                     "url": url}
        )
    except Exception as e:
        traceback.print_exc()
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request},
        )

@analysis_router.post("/get-summary-by-yt-video", response_class=HTMLResponse)
async def get_yt_transcript(request: Request,
                            url: str = Form(...),
                            db: AsyncSession = Depends(get_db)):
    try:

        analysis_service = AnalysisService(db)
        companies_array = await analysis_service.analyse_yt_video(url)

        return templates.TemplateResponse(
            request=request,
            name="analysis/companies_overview.html",
            context={
                "request": request,
                "companies": companies_array,
                "yt_url":url
            }
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
async def show_saved_financial_metrics_page(
        request: Request,
        db: AsyncSession = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id),
):
    try:

        analysis_service = AnalysisService(db)

        return analysis_service.get_current_start_page(
            request=request,
        current_user_id=current_user_id)
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})

@analysis_router.post("/add-metric-to-current-template", response_class=HTMLResponse)
async def add_to_current_selected_template_new_financial_metric(
        request: Request,
        last_selected_branch_profile_id: int = Form(...),
        financial_metric_id: int = Form(...),
        reference_value: int = Form(...),
        should_rise: bool = Form(False),
        db: AsyncSession = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id)
):
    try:
        analysis_service = AnalysisService(db)

        await analysis_service.add_metric_to_profile(
            last_selected_branch_profile_id=last_selected_branch_profile_id,
            financial_metric_id=financial_metric_id,
            reference_value=reference_value,
            should_rise=should_rise,
            current_user_id=current_user_id
        )

        return analysis_service.get_current_start_page(
            request=request,
            current_user_id=current_user_id)
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})

@analysis_router.post("/create-new-template-with-current-properties", response_class=HTMLResponse)
async def create_new_template_of_current_financial_metrics_properties(
        request: Request,
        branch_profile_name: str = Form(...),
        metric_data_triplets: Optional[str] = Form(None),
        db: AsyncSession = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id)
):
    try:

        analysis_service = AnalysisService(db)

        await analysis_service.create_template_from_active_metrics(
            current_user_id=current_user_id,
            branch_profile_name=branch_profile_name,
            metric_data_triplets=metric_data_triplets
        )

        return analysis_service.get_current_start_page(
            request=request,
            current_user_id=current_user_id)
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})

@analysis_router.post("/change-selected-template")
async def change_selected_template(
        request: Request,
        branch_profile_id: int = Form(...),
        db: AsyncSession = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id)
):
    try:

        analysis_service = AnalysisService(db)

        await analysis_service.update_last_selected_template_id_of_current_user(
            template_id=branch_profile_id,
            current_user_id=current_user_id
        )

        return analysis_service.get_current_start_page(
            request=request,
            current_user_id=current_user_id)

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})

@analysis_router.get("/edit-metric-of-current-template/{last_selected_branch_profile_id}/{metric_id}")
async def show_edit_financial_metric_of_current_template(
        request: Request,
        last_selected_branch_profile_id: int,
        metric_id: int,
        db: AsyncSession = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id)
):

    analysis_service = AnalysisService(db)

    template = await analysis_service.get_template_by_id(template_id=last_selected_branch_profile_id)

    metric = await analysis_service.get_metric_by_id(metric_id=metric_id)

    metric_categories = analysis_service.get_all_metric_categories()

    config = analysis_service.get_get_config_by_metric_and_template_id(
        metric_id=metric_id,
        last_selected_branch_profile_id=last_selected_branch_profile_id, )

    return render_localized(
        template_name="analysis/edit_metric.html",
        request=request,
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
async def update_metric_of_current_template(
        request: Request,
        config_id: int,
        db: AsyncSession = Depends(get_db),
        name: str = Form(...),
        unit: str = Form(...),
        should_rise: bool = Form(False),
        reference_value: float = Form(None),
        is_active: bool = Form(False),
        current_user_id: UUID = Depends(get_current_user_id)
):
    try:

        analysis_service = AnalysisService(db)

        await analysis_service.get_update_template_metric_configuration(
            config_id=config_id,
            new_reference_value=int(reference_value),
            should_rise=should_rise,
            is_active=is_active,
        )

        return analysis_service.get_current_start_page(
            request=request,
            current_user_id=current_user_id
        )
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(request=request, name="error.html", context={"request": request})

@analysis_router.post("/delete-selected-metrics-for-this-template")
async def delete_selected_metrics_for_this_template(
        request: Request,
        selected_branch_id: int = Form(...),
        metric_ids: Optional[str] = Form(None),
        db: AsyncSession = Depends(get_db),
        current_user_id: UUID = Depends(get_current_user_id)
):
    try:

        analysis_service = AnalysisService(db)

        await analysis_service.delete_metrics_of_current_template(
            selected_template_id=selected_branch_id,
            metric_ids=metric_ids,
        )

        return analysis_service.get_current_start_page(
            request=request,
            current_user_id=current_user_id
        )

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
def find_potential_stocks(filters: dict,
                          db: AsyncSession = Depends(get_db),):
    analysis_service = AnalysisService(db)

    return analysis_service.find_potential_stock_of_filter(filters)

@analysis_router.get("/get-financial-metrics", response_class=HTMLResponse)
async def get_evaluation_of_financial_metrics_of_current_user_last_selected_template(request: Request,
                                                                                     company: str,
                                                  db: AsyncSession = Depends(get_db),
                                                  current_user_id: UUID = Depends(get_current_user_id)):
    try:
        financial_metric_service = MetricsService(db)
        (data_by_category,
         satisfied_metrics_by_category,
         unsatisfied_metrics_by_category,
         satisfied_benchmarks_by_category,
         unsatisfied_benchmarks_by_category,
         satisfied_development_by_category,
         unsatisfied_development_by_category,
         summary_combined,
         summary_benchmark,
         summary_development) = await financial_metric_service.get_evaluation_of_over_all_reference_value_development(
            company_name=company, current_user_id=current_user_id
        )
        years = ["2022", "2023", "2024", "2025"]

        ai_financial_metric_evaluator = FinancialMetricAIEvaluator(
            model_name=FINANCIAL_METRIC_EVALUATION_MODEL
        )
        ai_evaluation = ""
        """ai_evaluation = ai_financial_metric_evaluator.evaluate_financial_metrics(
            satisfied_by_category= satisfied_metrics_by_category,
        unsatisfied_by_category = unsatisfied_metrics_by_category,
        satisfied_only_reference_value = satisfied_benchmarks_by_category,
        unsatisfied_only_reference_value= unsatisfied_benchmarks_by_category,
        satisfied_only_development= satisfied_development_by_category,
        unsatisfied_only_development= unsatisfied_development_by_category,
        )"""

        llm_wiki = LLMWiki(
            db=db,
            groq_model_name=LLM_WIKI_MODEL
        )

        watchlist_stock_service = WatchlistStockService(db)

        bought_stock_service = BoughtStockService(db)

        if await bought_stock_service.user_already_bought_stock(current_user_id=current_user_id,
                                                                ticker=company):
            current_bought_stock = await  bought_stock_service.get_of_current_user_stock_by_name(
                current_user_id=current_user_id,
                ticker=company
            )
            bought_stock_id = current_bought_stock.id
            (
                new_combined_strengths,
                new_combined_weakness,
                new_combined_wiki
            ) = await llm_wiki.ingest(
                watch_list_stock_id=None,
                bought_stock_id=bought_stock_id,
                company_name="",
                ticker=company,
                new_strengths="",
                new_weaknesses="",
                new_content=ai_evaluation
            )
            await bought_stock_service.update_strength_weakness_wiki_page_of_stock(
                bought_stock_obj=current_bought_stock,
                new_strength=new_combined_strengths,
                new_weakness=new_combined_weakness,
                new_wiki_page=new_combined_wiki
            )
        elif await watchlist_stock_service.check_if_user_has_stock_already_in_watchlist(current_user_id=current_user_id,
                                                                                        ticker=company):
            current_watch_list_stock = await watchlist_stock_service.get_current_stock_of_user(
                current_user_id=current_user_id,
                ticker_of_stock=company,
            )

            current_watch_list_stock_id = current_watch_list_stock.id

            (
                new_combined_strengths,
                new_combined_weakness,
                new_combined_wiki
            ) = await llm_wiki.ingest(
                watch_list_stock_id=current_watch_list_stock_id,
                bought_stock_id=None,
                company_name="",
                ticker=company,
                new_strengths="",
                new_weaknesses="",
                new_content=ai_evaluation
            )

            await watchlist_stock_service.update_strength_weakness_wiki_page_of_watchlist_stock(
                watchlist_stock_obj=current_watch_list_stock,
                new_strength=new_combined_strengths,
                new_weakness=new_combined_weakness,
                new_wiki_page=new_combined_wiki
            )

        return render_localized(
            request=request,
            template_name="analysis/show_financial_metrics.html",
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
                "evaluation": ai_evaluation,
            })
    except Exception as e:
        print(e)
        traceback.print_exc()
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request}
        )

@analysis_router.get("/get-news")
def get_news_of_stock_with_finnhub(request: Request, stock: str = Query(...),
                                   db: AsyncSession = Depends(get_db)):

    analysis_service = AnalysisService(db)

    headline_url = analysis_service.get_headline_url_dict(stock)

    return templates.TemplateResponse(
        request=request,
        name="analysis/show_news.html",
        context={
            "news_articles": headline_url
        }
    )
