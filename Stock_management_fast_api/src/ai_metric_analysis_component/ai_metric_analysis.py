from abc import abstractmethod


class AIMetricAnalysisComponent:

    def __init__(self):
        pass

    @abstractmethod
    def analyse_financial_metrics(self, all_to_considered_financial_metrics):
        pass