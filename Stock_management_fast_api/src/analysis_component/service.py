import json
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import  Request
from src.configs.used_model import STRENGTH_WEAKNESS_MODEL
from src.financial_metric_analysis_component.financial_metric_service import MetricsService
from src.strength_weakness_company_component.strenth_weakness_comapany import StrengthWeaknessOfCompanyComponent
from src.template_component.service import TemplateService
from src.template_metric_component.service import TemplateMetricService
from src.utils.utils import render_localized


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

    async def get_current_start_page(self,
                                     request: Request,
                                     current_user_id: UUID):


        last_selected_branch_profile_id = await self.get_last_selected_template_id_of_current_user(
            current_user_id)

        available_metrics = await self.get_available_metrics()

        current_user_created_templates = self.get_current_user_created_templates(current_user_id)

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