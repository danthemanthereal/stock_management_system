from src.ai_metric_analysis_component.ai_metric_analysis import AIMetricAnalysisComponent


class ProfitabilityAnalysis(AIMetricAnalysisComponent):

    def __init__(self,
                 model_name: str,
                 api_key: str,
                 user_prompt_path: str,
                 system_prmpt_path: str):
        super().__init__()
        self.model_name = model_name
        self.api_key = api_key

    def analyse_financial_metrics(self,
                                  satisfied_by_category: dict,
                                  unsatisfied_by_category: dict,
                                  satisfied_only_reference_value: dict,
                                  unsatisfied_only_reference_value: dict,
                                  satisfied_only_development: dict,
                                  unsatisfied_only_development: dict,
                                  ):
        pass