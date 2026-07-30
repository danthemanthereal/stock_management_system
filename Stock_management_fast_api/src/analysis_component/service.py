import json
import time
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  Request
from src.ai_financial_metricevaluation_component.evaluation_ai_financial_metrics import FinancialMetricAIEvaluator
from src.configs.used_model import STRENGTH_WEAKNESS_MODEL, FINANCIAL_METRIC_EVALUATION_MODEL, LLM_WIKI_MODEL, \
    INDUSTRY_EVALUATION_MODEL
from src.financial_metric_analysis_component.financial_metric_service import MetricsService
from src.financial_metric_analysis_component.utils import merge_financial_summary_triples
from src.financial_metric_category_component.service import FinancialMetricCategoryService
from src.find_potential_stocks_component.find_potential_stocks import FindPotentialStocks
from src.get_news_component.get_news import NewsFinderComponent
from src.industry_ai_evaluation_compoment.industry_ai_evaluation import IndustryAIEvaluation
from src.industry_component.service import IndustryService
from src.kaparthies_llm_wiki_component.llm_wiki import LLMWiki
from src.stock_market_component.service import StockMarketComponentService
from src.strength_weakness_company_component.strenth_weakness_comapany import StrengthWeaknessOfCompanyComponent
from src.template_component.service import TemplateService
from src.template_metric_component.service import TemplateMetricService
from src.utils.utils import render_localized
from dotenv import load_dotenv
import os

load_dotenv()

GET_CONTENT_BY_TEXT_ACTION_NAME="update_by_text"

GET_CONTENT_BY_URL_ACTION_NAME="update_by_url"




class AnalysisService:

    def __init__(self, db:AsyncSession):
        self.db = db

    async def analyse_url(self, url: str):
        strength_weakness_company_component = StrengthWeaknessOfCompanyComponent(
            groq_model_name=STRENGTH_WEAKNESS_MODEL
        )
        companies_array = await strength_weakness_company_component.get_strength_weakness_of_company(url)

        if isinstance(companies_array, str):
            try:
                return json.loads(companies_array)
            except json.JSONDecodeError:
                return []

        return companies_array

    async def analyse_yt_video(self, yt_url: str):
        strength_weakness_company_component = StrengthWeaknessOfCompanyComponent(
            groq_model_name=STRENGTH_WEAKNESS_MODEL
        )
        companies_array = strength_weakness_company_component.get_strength_weakness_of_youtube(yt_url)

        if isinstance(companies_array, str):
            try:
                return json.loads(companies_array)
            except json.JSONDecodeError:
                return []
        return companies_array

    async def analyse_markdown_file(self, markdown_file_content: str):
        strength_weakness_company_component = StrengthWeaknessOfCompanyComponent(
            groq_model_name=STRENGTH_WEAKNESS_MODEL
        )
        companies_array = strength_weakness_company_component.get_strength_weakness_of_markdown_file(markdown_file_content)

        if isinstance(companies_array, str):
            try:
                return json.loads(companies_array)
            except json.JSONDecodeError:
                return []
        return companies_array


    async def get_current_start_page(self,
                                     request: Request,
                                     current_user_id: UUID):


        last_selected_branch_profile_id = await self.get_last_selected_template_id_of_current_user(
            current_user_id)

        available_metrics = await self.get_available_metrics()

        current_user_created_templates = await self.get_current_user_created_templates(current_user_id)

        financial_metrics_of_last_selected_template_per_category = await self.get_all_financial_metrics_of_last_selected_template_per_category(
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

    async def get_available_metrics(self,):
        financial_metric_service = MetricsService(self.db)

        return await financial_metric_service.get_available_metrics()

    async def get_last_selected_template_id_of_current_user(self,
                                                            current_user_id: UUID):
        template_service = TemplateService(self.db)
        return await template_service.get_last_selected_template_id_of_user(current_user_id)

    async def get_current_user_created_templates(self, current_user_id: UUID):
        template_service = TemplateService(self.db)
        return await template_service.get_current_user_created_templates(current_user_id)

    async def get_all_financial_metrics_of_last_selected_template_per_category(self,
                                                                         last_selected_branch_profile_id: int):
        template_metric_service = TemplateMetricService(self.db)
        return await template_metric_service.get_all_financial_metrics_of_last_selected_template_per_category(
            last_selected_branch_profile_id)


    async def add_metric_to_profile(self,
                                    last_selected_branch_profile_id:int,
                                    financial_metric_id: int,
                                    reference_value: int,
                                    should_rise:bool,
                                    current_user_id: UUID):
        template_financial_metric_service = TemplateMetricService(self.db)
        await template_financial_metric_service.add_metric_to_profile(
            profile_id=last_selected_branch_profile_id,
            metric_id=financial_metric_id,
            reference_value=reference_value,
            should_rise=should_rise,
            user_id=current_user_id
        )

    async def create_template_from_active_metrics(self,
                                                  current_user_id: UUID,
                                                  branch_profile_name: str,
                                                  metric_data_triplets: str):
        template_service = TemplateService(self.db)
        await template_service.create_template_from_active_metrics(
            user_id=current_user_id,
            new_profile_name=branch_profile_name,
            triplets_str=metric_data_triplets)

    async def update_last_selected_template_id_of_current_user(self,
                                                               template_id:int,
                                                               current_user_id: UUID):
        template_service = TemplateService(self.db)
        await template_service.update_last_selected_template_id(template_id, current_user_id)

    async def get_template_by_id(self,
                                 template_id: int):
        template_service = TemplateService(self.db)
        return await template_service.get_template_by_id(template_id)

    async def get_metric_by_id(self,
                               metric_id: int):
        financial_metric_service = MetricsService(self.db)
        return await financial_metric_service.get_financial_metric_by_id(metric_id)

    async def get_all_metric_categories(self,):
        financial_metric_category_service = FinancialMetricCategoryService(self.db)
        return await financial_metric_category_service.get_all_metric_categories()

    async def get_get_config_by_metric_and_template_id(self,
        metric_id: int,
        last_selected_branch_profile_id: int):
        financial_metric_template_service = TemplateMetricService(self.db)

        return await financial_metric_template_service.get_config_by_metric_and_template_id(metric_id,
                                                                                              last_selected_branch_profile_id)

    async def get_update_template_metric_configuration(self,
        config_id: int,
        new_reference_value: int,
        should_rise: bool,
        is_active: bool,

    ):

        financial_metric_template_service = TemplateMetricService(self.db)
        await financial_metric_template_service.update_template_metric_configuration(
            config_id=config_id,
            new_reference_value=new_reference_value,
            should_rise=should_rise,
            is_active=is_active,
        )

    async def delete_metrics_of_current_template(self,
                                                 selected_template_id: int,
                                                 metric_ids: str):
        ids_to_delete = [int(id_str.strip()) for id_str in metric_ids.split(",") if id_str.strip()]

        template_metric_service = TemplateMetricService(self.db)

        await template_metric_service.delete_metrics_of_current_template(selected_template_id, ids_to_delete)

    async def find_potential_stock_of_filter(self, filters: dict):
        find_potential_stocks_component = FindPotentialStocks()
        return find_potential_stocks_component.find_potential_stocks_for_current_user(filters)

    async def get_headline_url_dict(self,
                                    stock: str):
        news_component = NewsFinderComponent(
            finhub_api_key=os.getenv("FINNHUB_API_KEY")
        )
        return news_component.get_all_news_of_stock(stock)

    async def get_eval_metric_page(self,
                                   request: Request,
                                   company: str,
                                   current_user_id: UUID):

        financial_metric_service = MetricsService(self.db)
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

        ai_evaluation = await self.get_ai_evaluation(
            satisfied_metrics_by_category=satisfied_metrics_by_category,
            unsatisfied_metrics_by_category=unsatisfied_metrics_by_category,
            satisfied_benchmarks_by_category=satisfied_benchmarks_by_category,
            unsatisfied_benchmarks_by_category=unsatisfied_benchmarks_by_category,
            satisfied_development_by_category=satisfied_development_by_category,
            unsatisfied_development_by_category=unsatisfied_development_by_category,
        )

        await self.update_wiki_page_with_ai_evaluation(
            company_ticker=company,
            current_user_id=current_user_id,
            new_strengths="",
            new_weaknesses="",
            new_content=ai_evaluation,
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

    async def get_ai_evaluation(self,
                          satisfied_metrics_by_category,
                          unsatisfied_metrics_by_category,
                          satisfied_benchmarks_by_category,
                          unsatisfied_benchmarks_by_category,
                          satisfied_development_by_category,
                          unsatisfied_development_by_category,
                          ):
        ai_financial_metric_evaluator = FinancialMetricAIEvaluator(
            model_name=FINANCIAL_METRIC_EVALUATION_MODEL
        )

        return await ai_financial_metric_evaluator.evaluate_financial_metrics(
            satisfied_by_category=satisfied_metrics_by_category,
            unsatisfied_by_category=unsatisfied_metrics_by_category,
            satisfied_only_reference_value=satisfied_benchmarks_by_category,
            unsatisfied_only_reference_value=unsatisfied_benchmarks_by_category,
            satisfied_only_development=satisfied_development_by_category,
            unsatisfied_only_development=unsatisfied_development_by_category,
        )

    async def update_wiki_page_with_ai_evaluation(self,
                                                  company_ticker:str,
                                                  current_user_id:UUID,
                                                  new_strengths: str,
                                                  new_weaknesses: str,
                                                  new_content:str
                                                  ):

        llm_wiki = LLMWiki(self.db,
                           groq_model_name=LLM_WIKI_MODEL)

        await llm_wiki.update_page_strength_weakness_if_company_on_watchlist_or_in_bought(
            company_ticker=company_ticker,
            current_user_id=current_user_id,
            new_strengths=new_strengths,
            new_weaknesses=new_weaknesses,
            new_content=new_content,
        )

    async def get_stock_market_analysis(self):
        news_component = NewsFinderComponent(
            finhub_api_key=os.getenv("FINNHUB_API_KEY")
        )
        return await news_component.get_stock_market_news_with_G_news()


    async def get_current_stock_market_wiki_page(self):
        stock_market_service = StockMarketComponentService(
            self.db
        )

        return await stock_market_service.get_current_wiki_page()

    async def update_stock_market_wiki_page(self, new_text):

        stock_market_service = StockMarketComponentService(self.db)
        await stock_market_service.update_stock_market_wiki_page(new_text)

    async def get_industry_wiki_pages_of_current_user(self, current_user_id: UUID):

        industry_service = IndustryService(self.db)
        return await industry_service.get_industry_wiki_page_of_current_user(current_user_id=current_user_id)

    async def get_all_created_industries_of_current_user(self, current_user_id: UUID):
        industry_service = IndustryService(self.db)

        return await industry_service.get_industries_of_current_user(current_user_id=current_user_id)


    async def add_to_current_user_new_industry(self,
                                               industry_name: str,
                                               current_user_id: UUID):
        industry_service = IndustryService(self.db)
        await industry_service.add_to_current_user_new_industry(
            industry_name=industry_name,
            current_user_id=current_user_id,
        )

    async def update_wiki_of_current_selected_industry_of_current_user(self,
                                                                       current_user_id: UUID,
                                                                       industry_name: str,
                                                                       input_link_or_text: str,
                                                                       action: str
                                                                       ):
        industry_service = IndustryService(self.db)

        llm_wiki = LLMWiki(self.db,
                           LLM_WIKI_MODEL
                           )

        new_content = await self.get_content_of_url_or_text(
            industry_name=industry_name,
            input_link_or_text=input_link_or_text,
            action=action
        )

        current_wiki_of_current_industry_of_current_user = await industry_service.get_current_wiki_page_of_industry_of_current_user(industry_name=industry_name,
                                                                                                                              current_user_id=current_user_id)

        current_bull_factors, current_bear_factors = await industry_service.get_bear_and_bull_factors_of_current_industry_of_current_user(
            current_user_id=current_user_id,
        industry_name=industry_name,
        )

        new_bull_factors, new_bear_factors = await self.get_new_bear_and_bull_factors_of_new_content(
            new_content=new_content,
            industry_name=industry_name,
        )


        updated_wiki_page = await llm_wiki.ingest_industry_wiki_page(
            industry_name=industry_name,
            current_wiki_page=current_wiki_of_current_industry_of_current_user,
            new_content=new_content,
        )

        new_combined_bear_factors = await llm_wiki.ingest_bear_factors_wiki_page(
            industry_name=industry_name,
            current_bear_factors=current_bear_factors,
            new_bear_factors=new_bear_factors,
        )

        time.sleep(61)

        new_combined_bull_factors = await llm_wiki.ingest_bull_factors_wiki_page(
            industry_name=industry_name,
            current_bull_factors=current_bull_factors,
            new_bull_factors=new_bull_factors,
        )

        await industry_service.update_wiki_page_of_selected_industry_of_current_user(
            current_user_id=current_user_id,
            industry_name=industry_name,
            new_wiki_page=updated_wiki_page
        )

        await industry_service.update_bear_and_bull_of_selected_industry_of_current_user(
            current_user_id=current_user_id,
            industry_name=industry_name,
            new_bear_factors=new_combined_bear_factors,
            new_bull_factors=new_combined_bull_factors
        )

    async def get_content_of_url_or_text(self,
                                   industry_name: str,
                                   input_link_or_text: str,
                                   action: str):
        if action == GET_CONTENT_BY_TEXT_ACTION_NAME:
            return input_link_or_text
        elif action == GET_CONTENT_BY_URL_ACTION_NAME:
            industry_ai_eval = IndustryAIEvaluation(
                groq_model_name=INDUSTRY_EVALUATION_MODEL,
                api_key=os.getenv("GROQ_API_KEY")
            )

            bear_factors, bull_factors = await industry_ai_eval.get_bear_and_bull_factors_by_url(
                industry=industry_name,
                url=input_link_or_text,
            )

            return f"""
                    Bear Factors: {bear_factors}
                    
                    Bull Factors: {bull_factors}
            """

        else:
            return ""


    async def get_new_bear_and_bull_factors_of_new_content(self,
                                                     industry_name: str,
                                                     new_content: str
                                                     ):
        try:
            industry_ai_eval = IndustryAIEvaluation(
                groq_model_name=INDUSTRY_EVALUATION_MODEL,
                api_key=os.getenv("GROQ_API_KEY")
            )

            bear_factors, bull_factors = await industry_ai_eval.get_bear_and_bull_factors_by_url(
                industry=industry_name,
                url=new_content,
            )

            return bull_factors, bear_factors
        except Exception as e:
            print(e)
            return "", ""

    async def update_industry_wiki_page_of_current_user(self,
                                                        current_user_id: UUID,
                                                        industry_name: str,
                                                        file
                                                        ):

        try:
            industry_service = IndustryService(self.db)

            current_wiki_page = await industry_service.get_current_wiki_page_of_industry_of_current_user(
                industry_name=industry_name,
                current_user_id=current_user_id)

            file_content_str =  (await file.read()).decode("utf-8")


            llm_wiki_component = LLMWiki(
                self.db,
                LLM_WIKI_MODEL
            )
            print("before current bull factor ")
            current_bull_factors, current_bear_factors = await industry_service.get_bear_and_bull_factors_of_current_industry_of_current_user(
                current_user_id=current_user_id,
                industry_name=industry_name,
            )

            new_bull_factors, new_bear_factors = await self.get_new_bear_and_bull_factors_of_new_content(
                new_content=file_content_str,
                industry_name=industry_name,
            )

            new_combined_bear_factors = await llm_wiki_component.ingest_bear_factors_wiki_page(
                industry_name=industry_name,
                current_bear_factors=current_bear_factors,
                new_bear_factors=new_bear_factors,
            )

            time.sleep(61)

            new_combined_bull_factors = await llm_wiki_component.ingest_bull_factors_wiki_page(
                industry_name=industry_name,
                current_bull_factors=current_bull_factors,
                new_bull_factors=new_bull_factors,
            )

            updated_page_industry_page = await llm_wiki_component.ingest_industry_wiki_page(
                industry_name=industry_name,
                current_wiki_page=current_wiki_page,
                new_content=file_content_str,
            )

            await industry_service.update_wiki_page_of_selected_industry_of_current_user(
                current_user_id=current_user_id,
                industry_name=industry_name,
                new_wiki_page=updated_page_industry_page
            )

            await industry_service.update_bear_and_bull_of_selected_industry_of_current_user(
                current_user_id=current_user_id,
                industry_name=industry_name,
                new_bear_factors=new_combined_bear_factors,
                new_bull_factors=new_combined_bull_factors
            )

        except Exception as e:
            print(e)
            return





