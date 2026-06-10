import json
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.configs.used_model import STRENGTH_WEAKNESS_MODEL
from src.financial_metric_analysis_component.financial_metric_service import MetricsService
from src.strength_weakness_company_component.strenth_weakness_comapany import StrengthWeaknessOfCompanyComponent
from src.template_component.service import TemplateService


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

    async def get_available_metrics(self,):
        financial_metric_service = MetricsService(self.db)

        return await financial_metric_service.get_available_metrics()

    async def get_last_selected_template_id_of_current_user(self,
                                                            current_user_id: UUID):
        template_service = TemplateService(self.db)
        return await template_service.get_last_selected_template_id_of_user(current_user_id)
