import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

from src.financial_metric_calculator.financial_calculator import FinancialMetricCalculator
from src.financial_metric_fetcher.financial_metric_fetcher import FinancialMetricFetcher
from src.financial_metric_fetcher.utils import merge_all_financial_metrics_map


class ActiveFinancialMetricComponent:

    def __init__(self, db: AsyncSession, company_name: str,
                 financial_metric_fetchers: list[FinancialMetricFetcher]):
        self.db = db
        self.company_name = company_name
        self.financial_metric_fetchers = financial_metric_fetchers

    async def get_total_financial_metrics_of_current_template(self, current_user_id: uuid.UUID)->dict:
        total_financial_metric_map = {}
        fetch_tasks = [f.fetch(self.company_name) for f in self.financial_metric_fetchers]
        results = await asyncio.gather(*fetch_tasks, return_exceptions=True)

        safe_results = [res if isinstance(res, dict) else {} for res in results]

        total_financial_metric_map = merge_all_financial_metrics_map(*safe_results)

        financial_metric_calculator = FinancialMetricCalculator(total_financial_metric_map=total_financial_metric_map,
                                                                db=self.db)

        calculated_financial_metrics_map = await  financial_metric_calculator.get_calculated_financial_metric_map()


        return total_financial_metric_map








