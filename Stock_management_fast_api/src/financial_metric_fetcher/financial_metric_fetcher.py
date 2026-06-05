from abc import abstractmethod


class FinancialMetricFetcher:

    @abstractmethod
    async def fetch(self, company_ticker: str) -> dict[str, list]:
        ...
