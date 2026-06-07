from src.financial_metric_calculator.utils import get_calculated_financial_metrics


class FinancialMetricCalculator:

    def __init__(self, total_financial_metric_map):
        self.total_financial_metric_map = total_financial_metric_map


    async def get_calculated_financial_metric_map(self):

        calculated_financial_metric_map = {}
        financial_metrics_to_calculate = await get_calculated_financial_metrics()
        for financial_metric in financial_metrics_to_calculate:
            values = []
            calculated_financial_metric_map[financial_metric] = values

        return calculated_financial_metric_map




