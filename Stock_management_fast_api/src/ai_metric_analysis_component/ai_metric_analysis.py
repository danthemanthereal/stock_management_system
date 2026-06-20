from abc import abstractmethod


class AIMetricAnalysisComponent:

    def __init__(self):
        pass

    @abstractmethod
    def analyse_financial_metrics(self,
                                  satisfied_by_category:dict,
                                  unsatisfied_by_category:dict,
                                  satisfied_only_reference_value:dict,
                                  unsatisfied_only_reference_value:dict,
                                  satisfied_only_development:dict,
                                  unsatisfied_only_development:dict,
                                  ):
        pass