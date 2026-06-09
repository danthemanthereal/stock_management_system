import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from src.financial_metric_calculator.financial_calculator import FinancialMetricCalculator
from src.financial_metric_fetcher.financial_metric_fetcher import FinancialMetricFetcher
from src.financial_metric_fetcher.utils import merge_all_financial_metrics_map
from src.template_component.service import TemplateService
from src.template_metric_component.service import TemplateMetricService


class ActiveFinancialMetricComponent:

    def __init__(self, db: AsyncSession, company_name: str,
                 financial_metric_fetchers: list[FinancialMetricFetcher]):
        self.db = db
        self.company_name = company_name
        self.financial_metric_fetchers = financial_metric_fetchers

    async def get_total_financial_metrics_of_current_template(self, current_user_id: uuid.UUID)->dict[str, list]:
        fetch_tasks = [f.fetch(self.company_name) for f in self.financial_metric_fetchers]
        results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        safe_results = [res if isinstance(res, dict) else {} for res in results]

        total_financial_metric_map = merge_all_financial_metrics_map(*safe_results)

        financial_metric_calculator = FinancialMetricCalculator(total_financial_metric_map=total_financial_metric_map,
                                                                db=self.db)


        calculated_financial_metrics_map = await  financial_metric_calculator.get_calculated_financial_metric_map()

        return await self.get_current_activated_metrics_and_non_empty(current_user_id,calculated_financial_metrics_map)

    async def get_current_activated_metrics_and_non_empty(self, current_user_id: uuid.UUID, total_financial_metric_map)->dict[str,list]:

        template_service = TemplateService(self.db)
        template_metric_service = TemplateMetricService(self.db)

        last_selected_branch_profile_id = await template_service.get_last_selected_template_id_of_user(current_user_id)
        all_activated_financial_metric_names = await template_metric_service.get_active_metric_names_of_last_selected_template(last_selected_branch_profile_id)
        return {
            key: value
            for key, value in total_financial_metric_map.items()
            if self.check_should_consider_metric(key, all_activated_financial_metric_names, value)
        }


    def check_should_consider_metric(self, metric_name: str,
                                     active_metrics: list[str],
                                     values_from_map:list) -> bool:
        return metric_name in active_metrics and values_from_map









