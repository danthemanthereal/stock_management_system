import asyncio

import httpx

from src.financial_metric_fetcher.financial_metric_fetcher import FinancialMetricFetcher
from src.financial_metric_fetcher.utils import get_alpha_ventage_metrics, metric_will_be_considered


class AlphaVantageFetcher(FinancialMetricFetcher):

    LAST_FOUR_YEARS = -4
    DIFFERENT_URL_ENDPOINTS = ["INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW"]

    def __init__(self, alpha_vantage_api_key: str):
        self.alpha_vantage_api_key = alpha_vantage_api_key
        self.consider_financial_metric_alpha_ventage = get_alpha_ventage_metrics()

    async def fetch(self, company_ticker: str) -> dict[str, list]:
        try:

            consider_financial_metric_map = {}
            last_four_years_metric = await self.get_all_metrics_of_alpha_vantage(company_ticker)

            for financial_metric_of_year in last_four_years_metric:
                for (financial_metric, value) in financial_metric_of_year.items():
                    if metric_will_be_considered(financial_metric,self.consider_financial_metric_alpha_ventage):
                        consider_financial_metric_map.setdefault(financial_metric, []).append(value)

            return consider_financial_metric_map
        except Exception as e :
            print(e)
            return {}


    async def get_all_metrics_of_alpha_vantage(self, company_ticker: str) -> list[dict]:
        try:
            metrics_last_four_years = []
            async with httpx.AsyncClient() as client:
                tasks = []
                for endpoint in self.DIFFERENT_URL_ENDPOINTS:
                    url = f"https://www.alphavantage.co/query?function={endpoint}&symbol={company_ticker}&apikey={self.alpha_vantage_api_key}"
                    tasks.append(client.get(url))
                responses = await asyncio.gather(*tasks, return_exceptions=True)

                for response in responses:
                    try:
                        if not isinstance(response, Exception):
                            data = response.json()
                            metrics_last_four_years.extend(list(reversed(data.get('annualReports', [])))[self.LAST_FOUR_YEARS:])
                        else:
                            metrics_last_four_years.extend([])
                    except Exception as e :
                        print(e)
            return metrics_last_four_years
        except Exception as e :
            print(e)
            return []

