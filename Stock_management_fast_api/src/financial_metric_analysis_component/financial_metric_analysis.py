import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from src.financial_metric_analysis_component.utils import get_needed_metrics_map
from src.financial_metric_analysis_component.utils import \
    get_financial_metric_name_to_calculate
from src.financial_metric_analysis_component.utils import  add_to_metric_map_current_calculation
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




    async def get_total_financial_metrics_of_current_template(self, current_user_id: uuid.UUID)->dict:
        total_financial_metric_map = {}
        results = [await f.fetch(self.company_name) for f in self.financial_metric_fetchers]
        total_financial_metrics_map = merge_all_financial_metrics_map(*results)

        total_financial_metric_map = await self.get_calculated_metrics(total_financial_metric_map, current_user_id)
        return  total_financial_metric_map



    async def get_calculated_metrics(self, financial_metric_map,
                               current_user_id: uuid.UUID):

        needed_financial_metrics_map = await get_needed_metrics_map()

        employee_numbers = needed_financial_metrics_map.get("total_employee_number", [])
        revenues = needed_financial_metrics_map.get("revenue", [])
        total_equity = needed_financial_metrics_map.get("total_equity", [])
        total_liabilities = needed_financial_metrics_map.get("total_liabilities", [])
        total_current_liabilities = needed_financial_metrics_map.get("total_current_liabilities", [])
        cash_and_cash_equivalents = needed_financial_metrics_map.get("cash_and_cash_equivalents", [])
        total_current_assets = needed_financial_metrics_map.get("total_current_assets", [])
        total_non_current_assets = needed_financial_metrics_map.get("total_non_current_assets", [])
        total_assets = needed_financial_metrics_map.get("total_assets", [])
        total_good_will = needed_financial_metrics_map.get("good_will", [])

        calculated_metrics_name = await get_financial_metric_name_to_calculate(self.db)

        template_metric_service = TemplateMetricService(db=self.db)

        template_service = TemplateService(self.db)
        current_used_template_id = await template_service.get_last_selected_template_id_of_user(current_user_id)
        from src.financial_metric_analysis_component.financial_metric_service import MetricsService

        financial_metric_service = MetricsService(self.db)
        for current_metric in calculated_metrics_name:
            current_financial_metric_id = await financial_metric_service.get_id_of_current_metric_by_name(current_metric)

            if await template_metric_service.check_if_current_user_activated_this_metric_in_current_template(current_used_template_id,
                                                                                                       current_financial_metric_id):
                financial_metric_map = add_to_metric_map_current_calculation(
                    revenue_last_for_years=revenues,
                    total_employee_number_last_four_years=employee_numbers,
                    total_equity_last_four_years=total_equity,
                    total_liabilities_last_four_years=total_liabilities,
                    total_current_liabilities_last_four_years=total_current_liabilities,
                    cash_and_cash_equivalents_last_four_years=cash_and_cash_equivalents,
                    total_current_assets_last_four_years=total_current_assets,
                    total_non_current_assets_last_four_years=total_non_current_assets,
                    total_assets_last_four_years=total_assets,
                    good_will_last_four_years=total_good_will,
                    financial_metric_map=financial_metric_map,
                    financial_metric_name=current_metric
                )

        return financial_metric_map





