from src.financial_metric_fetcher.financial_metric_fetcher import FinancialMetricFetcher


class FMPFetcher(FinancialMetricFetcher):

    def __init__(self, fmp_vantage_api_key: str):
        self.fmp_vantage_api_key = fmp_vantage_api_key

    async def fetch(self, company_ticker: str) -> dict[str, list]:
        try:
            return {}

        except Exception:
            return {}