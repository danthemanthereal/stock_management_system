import uuid
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import FinancialMetric, FinancialMetricCategory
from src.financial_metric_analysis_component.financial_metric_analysis import \
    ActiveFinancialMetricComponent
import os
from dotenv import load_dotenv
from src.financial_metric_analysis_component.financial_metric_evaluator import FinancialMetricEvaluator
from src.financial_metric_fetcher.alpha_vantage_fetcher import AlphaVantageFetcher
from src.financial_metric_fetcher.from_pip_install_sources_fetcher import FROMPIPInstallSourceFetcher
from src.financial_metric_fetcher.guro_focus_fetcher import GuroFocusFetcher

load_dotenv()


class MetricsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_available_metrics(self) -> List[FinancialMetric]:
        result = await self.db.scalars(
            select(FinancialMetric).order_by(FinancialMetric.name)
        )
        return list(result.all())

    async def get_financial_metric_by_id(self, financial_metric_id: int) -> FinancialMetric:
        stmt = select(FinancialMetric).where(
            FinancialMetric.id == financial_metric_id
        )

        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()



    async def get_id_of_current_metric_by_name(self, metric_name: str) -> int:
        result = await self.db.scalar(
            select(FinancialMetric.id).where(
                FinancialMetric.name == metric_name
            )
        )
        return result or 0

    async def get_name_of_current_metric_name_by_id(self, metric_id: int) -> str:
        result = await self.db.scalar(
            select(FinancialMetric.id).where(
                FinancialMetric.id == metric_id
            )
        )
        return result or ""

    async def get_evaluation_of_over_all_reference_value_development(self,
                                                               company_name: str,
                                                               current_user_id: uuid.UUID, ):
        get_active_metrics_of_template_component = ActiveFinancialMetricComponent(
            db=self.db,
            company_name=company_name,
            financial_metric_fetchers=[FROMPIPInstallSourceFetcher()]
        )
        metrics_of_current_user_template = await get_active_metrics_of_template_component.get_total_financial_metrics_of_current_template(current_user_id)
        metric_evaluator = FinancialMetricEvaluator(self.db)
        return await metric_evaluator.get_satisfied_unsatisfied_by_category_and_summary(metrics_of_current_user_template,
                                                                                  current_user_id)

    async def get_metrics_by_category_name(self, category_name: str):
        stmt = (
            select(FinancialMetric.name)
            .join(FinancialMetricCategory)
            .where(FinancialMetricCategory.name == category_name)
        )

        result = await self.db.execute(stmt)
        return result.scalars().all()