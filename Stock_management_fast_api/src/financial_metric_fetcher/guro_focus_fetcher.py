import json

import aiofiles
from pathlib import Path
from src.financial_metric_fetcher.financial_metric_fetcher import FinancialMetricFetcher
from src.financial_metric_fetcher.utils import get_guro_metrics, metric_will_be_considered


class GuroFocusFetcher(FinancialMetricFetcher):

    def __init__(self,):
        self.considered_financial_metric_of_guro_focus = get_guro_metrics()

    async def fetch(self, company_ticker: str) -> dict[str, list]:
        try:

            financial_metric_guro_focus_map = {}

            current_path = Path(__file__).resolve()
            project_path = current_path.parents[2]
            guro_focus_financial_metric_file_path = project_path / "src" / "financial_metric_analysis_component" / "current_financial_metrics_guro_focus.json"

            async with aiofiles.open(
                   guro_focus_financial_metric_file_path) as financial_metrics_file:
                metrics = await financial_metrics_file.read()
                financial_metrics = json.loads(metrics)

            annuals = financial_metrics.get("annual", [])

            for current_year_map in annuals:
                for financial_metric, value in current_year_map.items():
                    if metric_will_be_considered(financial_metric, self.considered_financial_metric_of_guro_focus):
                        financial_metric_guro_focus_map.setdefault(financial_metric, []).append(value)

            return financial_metric_guro_focus_map
        except Exception as e:
            return {}