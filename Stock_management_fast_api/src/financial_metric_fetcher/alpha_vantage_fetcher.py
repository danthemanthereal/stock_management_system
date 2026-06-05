import httpx

from src.financial_metric_fetcher.financial_metric_fetcher import FinancialMetricFetcher
from src.financial_metric_fetcher.utils import get_alpha_ventage_metrics


class AlphaVantageFetcher(FinancialMetricFetcher):

    def __init__(self, alpha_vantage_api_key: str):
        self.alpha_vantage_api_key = alpha_vantage_api_key

    async def fetch(self, company_ticker: str) -> dict[str, list]:
        try:
            """url = f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={company_ticker}&apikey={self.alpha_vantage_api_key}'
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                data = response.json()


            alpha_ventage_financial_metrics = {}
            financial_metric_to_get = get_alpha_ventage_metrics()

            ## 22, 23, 24, 25

            annual_reports = list(reversed(data.get('annualReports', [])))[-4:]

            for annual_report in annual_reports:
                for (financial_metric, value) in annual_report.items():

                    alpha_ventage_financial_metrics.setdefault(financial_metric, []).append(value)
            return alpha_ventage_financial_metrics"""
        except Exception:
            return {}