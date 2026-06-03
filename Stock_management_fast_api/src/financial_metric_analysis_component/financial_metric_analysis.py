import uuid
import requests
from sqlalchemy.ext.asyncio import AsyncSession
import json
import aiofiles
import httpx
from src.financial_metric_analysis_component.utils import get_needed_metrics_map
from src.financial_metric_analysis_component.utils import \
    get_financial_metric_name_to_calculate
from src.financial_metric_analysis_component.utils import get_key_metrics_from_fmp, \
    get_ratio_metrics_of_fmp, add_to_metric_map_current_calculation
from src.template_component.service import TemplateService
from src.template_metric_component.service import TemplateMetricService
from src.financial_metric_analysis_component.utils import get_alpha_ventage_metrics




class ActiveFinancialMetricComponent:

    def __init__(self, db: AsyncSession, company_name: str,
                 fmp_api_key: str,
                 alpha_vantage_api_key: str):
        self.db = db
        self.company_name = company_name
        self.fmp_api_key = fmp_api_key
        self.alpha_vantage_api_key = alpha_vantage_api_key



    async def get_total_financial_metrics_of_current_template(self, current_user_id: uuid.UUID)->dict:
        total_financial_metric_map = {}
        total_financial_metric_map = await self.get_financial_metrics_by_guro_focus(total_financial_metric_map, current_user_id)
        total_financial_metric_map = await self.get_financial_metrics_with_alpha_ventage_api(total_financial_metric_map, current_user_id)
        total_financial_metric_map = await self.get_financial_metrics_with_fmp_api(total_financial_metric_map, current_user_id)
        total_financial_metric_map = await self.get_calculated_metrics(total_financial_metric_map, current_user_id)
        return  total_financial_metric_map

    async def get_financial_metrics_by_guro_focus(self, financial_metric_map: dict,
                                            current_user_id: uuid.UUID)->dict:
        """async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            async with page.expect_response(
                    lambda r: "/_api/stocks/" in r.url and "financial" in r.url,
                    timeout=60000
            ) as response_info:
                await page.goto(f"https://www.gurufocus.com/stock/{company}/financials")

            response = await response_info.value
            data = await response.json()
            print(f"data {data}")
            await browser.close()
            return data"""


        async with aiofiles.open("/Users/danielschmidt/Desktop/stock_management_system/Stock_management_fast_api/src/financial_metric_analysis_component/current_financial_metrics_guro_focus.json") as financial_metrics_file:
            metrics = await financial_metrics_file.read()
            financial_metrics = json.loads(metrics)


        annuals = financial_metrics.get("annual", [])

        template_metric_service = TemplateMetricService(db=self.db)

        template_service = TemplateService(self.db)
        current_used_template_id = await template_service.get_last_selected_template_id_of_user(current_user_id)
        from src.financial_metric_analysis_component.financial_metric_service import MetricsService

        financial_metric_service = MetricsService(db=self.db)
        for current_year_map in annuals:
            for key, value in current_year_map.items():
                if key == "date":
                    continue
                current_financial_metric_id = await financial_metric_service.get_id_of_current_metric_by_name(key)

                if await template_metric_service.check_if_current_user_activated_this_metric_in_current_template(
                        current_used_template_id,
                        current_financial_metric_id):
                    financial_metric_map.setdefault(key, []).append(value)

        return financial_metric_map


    async def get_financial_metrics_with_alpha_ventage_api(self, financial_metric_map,
                                                     current_user_id: uuid.UUID):

        url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={self.company_name}&apikey={self.alpha_vantage_api_key}'
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data =  response.json()


        financial_metric_to_get = get_alpha_ventage_metrics()

        ## 22, 23, 24, 25

        annual_reports = list(reversed(data.get('annualReports', [])))[-4:]
        template_metric_service = TemplateMetricService(db=self.db)

        template_service = TemplateService(self.db)
        current_used_template_id = await template_service.get_last_selected_template_id_of_user(current_user_id)
        from src.financial_metric_analysis_component.financial_metric_service import MetricsService

        financial_metric_service = MetricsService(self.db)
        for annual_report in annual_reports:
            for (key, value) in annual_report.items():
                if key not in financial_metric_to_get:
                    continue
                current_financial_metric_id = await financial_metric_service.get_id_of_current_metric_by_name(key)

                if await template_metric_service.check_if_current_user_activated_this_metric_in_current_template(
                            current_used_template_id,
                            current_financial_metric_id):
                    financial_metric_map.setdefault(key, []).append(value)
        return financial_metric_map

    async def get_financial_metrics_with_fmp_api(self,financial_metric_map,
                                           current_user_id: uuid.UUID):

        key_metrics_to_consider = get_key_metrics_from_fmp()

        ratio_metrics_to_consider = get_ratio_metrics_of_fmp()

        url = f"https://financialmodelingprep.com/stable/key-metrics?symbol={self.company_name}&apikey={self.fmp_api_key}"
        r = requests.get(url)
        ## 22, 23, 24, 25
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            data =  response.json()

        annual_reports = list(reversed(data))[-4:]
        template_metric_service = TemplateMetricService(db=self.db)

        template_service = TemplateService(self.db)
        current_used_template_id = await template_service.get_last_selected_template_id_of_user(current_user_id)
        from src.financial_metric_analysis_component.financial_metric_service import MetricsService

        financial_metric_service = MetricsService(self.db)
        for annual_report in annual_reports:
            for (key, value) in annual_report.items():
                if key not in key_metrics_to_consider:
                    continue
                current_financial_metric_id = await financial_metric_service.get_id_of_current_metric_by_name(key)

                if await template_metric_service.check_if_current_user_activated_this_metric_in_current_template(
                            current_used_template_id,
                            current_financial_metric_id):
                    financial_metric_map.setdefault(key, []).append(value)


        ratio_url = f"https://financialmodelingprep.com/stable/ratios?symbol={self.company_name}&apikey={self.fmp_api_key}"

        async with httpx.AsyncClient() as client:
            response = await client.get(ratio_url)
            ratio_response =  response.json()

        ## 22, 23, 24, 25
        annual_reports_because_of_ratio = list(reversed(ratio_response))[-4:]

        for annual_report in annual_reports_because_of_ratio:
            for (key, value) in annual_report.items():
                if key not  in ratio_metrics_to_consider:
                    continue
                current_financial_metric_id = await financial_metric_service.get_id_of_current_metric_by_name(key)

                if await template_metric_service.check_if_current_user_activated_this_metric_in_current_template(
                        current_used_template_id,
                        current_financial_metric_id):
                    financial_metric_map.setdefault(key, []).append(value)

        return financial_metric_map

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





