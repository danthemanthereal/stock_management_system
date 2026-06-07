from src.database.db import get_db
from src.financial_metric_analysis_component.financial_metric_service import MetricsService

FINANCIAL_METRIC_CATEGORIES = [
    "Aufwandsquote",
    "Working Capital Management",
    "Finanzielle Stabilität",
    "Rentabilität",
    "Bewertungskennzahl"
]

async def get_calculated_financial_metrics() -> list[str]:
    calculated_financial_metrics = []

    db = get_db()
    metric_service = MetricsService(db)

    for category in FINANCIAL_METRIC_CATEGORIES:
        calculated_financial_metrics_current_category = await metric_service.get_metrics_by_category_name(category)
        calculated_financial_metrics.extend(calculated_financial_metrics_current_category)

    return calculated_financial_metrics