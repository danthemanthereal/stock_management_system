import traceback
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Request, Depends, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.analysis_component.schema import WikiUpdate
from src.analysis_component.service import AnalysisService
from fastapi.templating import Jinja2Templates
from src.database.db import get_db
from starlette.responses import HTMLResponse
from src.utils.utils import render_localized
from src.authenticator_component.authenticator import get_current_user_id
from dotenv import load_dotenv

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
                "yt_url": url
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

        return await analysis_service.get_current_start_page(
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

        return await analysis_service.get_current_start_page(
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

        return await analysis_service.get_current_start_page(
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

        return await analysis_service.get_current_start_page(
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

    metric_categories = await analysis_service.get_all_metric_categories()

    config = await analysis_service.get_get_config_by_metric_and_template_id(
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

        return await analysis_service.get_current_start_page(
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

        return await analysis_service.get_current_start_page(
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
async def find_potential_stocks(filters: dict,
                                db: AsyncSession = Depends(get_db), ):
    analysis_service = AnalysisService(db)

    return await analysis_service.find_potential_stock_of_filter(filters)


@analysis_router.get("/get-financial-metrics", response_class=HTMLResponse)
async def get_evaluation_of_financial_metrics_of_current_user_last_selected_template(request: Request,
                                                                                     company: str,
                                                                                     db: AsyncSession = Depends(get_db),
                                                                                     current_user_id: UUID = Depends(
                                                                                         get_current_user_id)):
    try:

        analysis_service = AnalysisService(db)

        return await analysis_service.get_eval_metric_page(
            company=company,
            current_user_id=current_user_id,
            request=request,
        )

    except Exception as e:
        print(e)
        traceback.print_exc()
        return templates.TemplateResponse(
            request=request,
            name="error.html",
            context={"request": request}
        )


@analysis_router.get("/get-news")
async def get_news_of_stock_with_finnhub(request: Request, stock: str = Query(...),
                                         db: AsyncSession = Depends(get_db)):
    analysis_service = AnalysisService(db)

    headline_url = await analysis_service.get_headline_url_dict(stock)

    return templates.TemplateResponse(
        request=request,
        name="analysis/show_news.html",
        context={
            "news_articles": headline_url
        }
    )


@analysis_router.get("/get-stock-market-news")
async def get_stock_market_news(request: Request,
                                db: AsyncSession = Depends(get_db)):
    try:
        analysis_service = AnalysisService(db)

        headline_analysis = await analysis_service.get_stock_market_analysis()
        return templates.TemplateResponse(
            request=request,
            name="analysis/show_news_stockmarket.html",
            context={
                "news_articles": headline_analysis
            }
        )

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(
            request=request,
            name="error.html",
        )


@analysis_router.get("/get-stock-market-wiki-page")
async def get_stock_market_wiki_page(request: Request,
                                     db: AsyncSession = Depends(get_db)
                                     ):
    try:
        analysis_service = AnalysisService(db)

        stock_market_wiki_page = await analysis_service.get_current_stock_market_wiki_page()
        return templates.TemplateResponse(
            request=request,
            name="analysis/stock_market_wiki_page.html",
            context={
                "stock_market_wiki_page": stock_market_wiki_page
            }
        )

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(
            request=request,
            name="error.html",
        )


@analysis_router.post("/update-stock-wiki", response_class=HTMLResponse)
async def update_stock_wiki(
        request: Request,
        data: WikiUpdate,
        db: AsyncSession = Depends(get_db)
):
    analysis_service = AnalysisService(db)

    await analysis_service.update_stock_market_wiki_page(data.new_text)

    stock_market_wiki_page = await analysis_service.get_current_stock_market_wiki_page()

    return templates.TemplateResponse(
        request=request,

        name="analysis/stock_market_wiki_page.html",
        context=
        {
            "request": request,
            "stock_market_wiki_page": stock_market_wiki_page
        }
    )


@analysis_router.get("/industry-wiki-page", response_class=HTMLResponse)
async def get_industry_wiki_page(request: Request,
                                 db: AsyncSession = Depends(get_db),
                                 current_user_id: UUID = Depends(get_current_user_id)):
    try:
        analysis_service = AnalysisService(db)

        wiki_pages = await analysis_service.get_industry_wiki_pages_of_current_user(current_user_id)

        return templates.TemplateResponse(
            request=request,

            name="analysis/wiki_pages_of_current_user_overview.html",
            context=
            {
                "request": request,
                "wiki_pages": wiki_pages
            }
        )

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(
            request=request,
            name="error.html",
        )


@analysis_router.get("/industry-edit-wiki-page")
async def get_industry_edit_wiki_page(request: Request,
                                      db: AsyncSession = Depends(get_db),
                                      current_user_id: UUID = Depends(get_current_user_id)
                                      ):
    try:
        analysis_service = AnalysisService(db)

        wiki_pages = await analysis_service.get_industry_wiki_pages_of_current_user(current_user_id)

        created_industries_of_current_user = await analysis_service.get_all_created_industries_of_current_user(
            current_user_id)

        return templates.TemplateResponse(
            request=request,

            name="analysis/edit_industry_of_current_user.html",
            context=
            {
                "request": request,
                "wiki_pages": wiki_pages,
                "created_industries_of_current_user": created_industries_of_current_user
            }
        )

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(
            request=request,
            name="error.html",
        )


@analysis_router.post("/add-to-current-user-new-industry")
async def add_to_current_user_new_industry(request: Request,
                                           industry_name: str = Form(...),
                                           db: AsyncSession = Depends(get_db),
                                           current_user_id: UUID = Depends(get_current_user_id)
                                           ):
    try:
        analysis_service = AnalysisService(db)
        await analysis_service.add_to_current_user_new_industry(industry_name, current_user_id)

        wiki_pages = await analysis_service.get_industry_wiki_pages_of_current_user(current_user_id)

        created_industries_of_current_user = await analysis_service.get_all_created_industries_of_current_user(
            current_user_id)

        return templates.TemplateResponse(
            request=request,

            name="analysis/edit_industry_of_current_user.html",
            context=
            {
                "request": request,
                "wiki_pages": wiki_pages,
                "created_industries_of_current_user": created_industries_of_current_user
            }
        )

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(
            request=request,
            name="error.html",
        )


@analysis_router.post("/update-wiki-page-current-selected-industry")
async def update_wiki_page_current_selected_industry(request: Request,
                                            db: AsyncSession = Depends(get_db),
                                            current_user_id: UUID = Depends(get_current_user_id),
                                            selected_industry: str = Form(...),
                                            input_link_or_text: str = Form(...),
                                            action: str = Form(...)
                                            ):
    try:
        analysis_service = AnalysisService(db)

        await analysis_service.update_wiki_of_current_selected_industry_of_current_user(
            current_user_id=current_user_id,
            industry_name=selected_industry,
            input_link_or_text=input_link_or_text,
            action=action
        )

        wiki_pages =  await analysis_service.get_industry_wiki_pages_of_current_user(current_user_id)

        created_industries_of_current_user = await analysis_service.get_all_created_industries_of_current_user(
            current_user_id)

        return templates.TemplateResponse(
            request=request,

            name="analysis/edit_industry_of_current_user.html",
            context=
            {
                "request": request,
                "wiki_pages": wiki_pages,
                "created_industries_of_current_user": created_industries_of_current_user
            }
        )

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return templates.TemplateResponse(
            request=request,
            name="error.html",
        )



