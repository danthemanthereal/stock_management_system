from database.models import FinancialMetric
from sqlalchemy import and_


def get_satisfied_and_not_satisfied_financial_metrics(financial_metrics: dict, db):
    satisfied_financial_metrics = []
    unsatisfied_financial_metrics = []
    satisfied_development_metric = []
    unsatisfied_development_metric = []
    satisfied_benchmark_value = []
    unsatisfied_benchmark_value = []

    for financial_metric_name in financial_metrics.keys():
        financial_metric_object = db.query(FinancialMetric).filter(
            and_(
                FinancialMetric.name == financial_metric_name,
                FinancialMetric.is_active == True
            )
        ).first()
        values = financial_metrics[financial_metric_name]
        if not financial_metric_object or not values:
            continue
        if None in values:
            continue

        if any(isinstance(x, str) for x in values):
            continue
        if check_satisfiability(financial_metric_object, values):
            satisfied_financial_metrics.append(financial_metric_name)
        else:
            unsatisfied_financial_metrics.append(financial_metric_name)

        if check_satisfiability_development(financial_metric_object, values):
            satisfied_development_metric.append(financial_metric_name)
        else:
            unsatisfied_development_metric.append(financial_metric_name)

        if check_satisfiability_benchmark_value(financial_metric_object, values):
            satisfied_benchmark_value.append(financial_metric_name)
        else:
            unsatisfied_benchmark_value.append(financial_metric_name)

    return (satisfied_financial_metrics, unsatisfied_financial_metrics,
            satisfied_benchmark_value, unsatisfied_benchmark_value,
            satisfied_development_metric,unsatisfied_development_metric)


def check_satisfiability(financial_metric_obj: FinancialMetric, values: list[int])->bool:
    last_value = values[-1]
    if financial_metric_obj.unit == "%":
        last_value = int(last_value * 100)

    if financial_metric_obj.should_rise:
        print("val in method")
        print(values)
        asc_sorting = sorted(values)

        return asc_sorting == values and financial_metric_obj.reference_value > last_value
    else:
        desc_sorting = sorted(values, reverse=True)
        return desc_sorting == values and last_value < financial_metric_obj.reference_value

def check_satisfiability_development(financial_metric_obj: FinancialMetric, values: list[int])->bool:

    if financial_metric_obj.should_rise:
        asc_sorting = sorted(values)

        return asc_sorting == values
    else:
        desc_sorting = sorted(values, reverse=True)
        return desc_sorting == values


def check_satisfiability_benchmark_value(financial_metric_obj: FinancialMetric, values: list[int]) -> bool:

    last_value = values[-1]
    if financial_metric_obj.unit == "%":
        last_value = int(last_value * 100)

    if financial_metric_obj.should_rise:

        return financial_metric_obj.reference_value > last_value
    else:
        return financial_metric_obj.reference_value < last_value
