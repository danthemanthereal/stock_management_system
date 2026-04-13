from database.models import FinancialMetric


def get_satisfied_and_not_satisfied_financial_metrics(financial_metrics: dict, db):
    satisfied_financial_metrics = []
    unsatisfied_financial_metrics = []

    for financial_metric_name in financial_metrics.keys():
        financial_metric_object =    db.query(FinancialMetric).filter(FinancialMetric.name == financial_metric_name).first()
        values = financial_metrics[financial_metric_name]
        if check_satisfiability(financial_metric_object, values):
            satisfied_financial_metrics.append(financial_metric_name)
        else:
            unsatisfied_financial_metrics.append(financial_metric_name)

    return satisfied_financial_metrics, unsatisfied_financial_metrics

def check_satisfiability(financial_metric_obj: FinancialMetric, values: list[int])->bool:
    if financial_metric_obj.should_rise:
        asc_sorting = sorted(values)

        return asc_sorting == values and financial_metric_obj.reference_value > values[-1]
    else:
        desc_sorting = sorted(values, reverse=True)
        return desc_sorting == values and values[-1] < financial_metric_obj.reference_value
